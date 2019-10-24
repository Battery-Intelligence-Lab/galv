-- Database: galvanalyser

-- DROP DATABASE galvanalyser;

CREATE DATABASE galvanalyser
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

ALTER DATABASE galvanalyser SET timezone TO 'UTC';
SELECT pg_reload_conf();

-- Role: normal_user
-- DROP ROLE normal_user;

CREATE ROLE normal_user WITH
  NOLOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION;

-- Role: harvester
-- DROP ROLE harvester;

CREATE ROLE harvester WITH
  NOLOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION;

-- SCHEMA: harvesters

-- DROP SCHEMA harvesters ;

CREATE SCHEMA harvesters
    AUTHORIZATION postgres;

GRANT ALL ON SCHEMA harvesters TO postgres;

GRANT USAGE ON SCHEMA harvesters TO harvester;

-- Table: harvesters.harvesters

-- DROP TABLE harvesters.harvesters;

CREATE TABLE harvesters.harvesters
(
    id_no bigserial NOT NULL,
    machine_id text NOT NULL,
    CONSTRAINT harvesters_pkey PRIMARY KEY (id_no),
    CONSTRAINT harvesters_machine_id_key UNIQUE (machine_id)

)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE harvesters.harvesters
    OWNER to postgres;

GRANT SELECT ON TABLE harvesters.harvesters TO harvester;

GRANT ALL ON TABLE harvesters.harvesters TO postgres;

-- Table: harvesters.monitored_paths

-- DROP TABLE harvesters.monitored_paths;

CREATE TABLE harvesters.monitored_paths
(
    harvester_id bigint NOT NULL,
    path text NOT NULL,
    monitored_for text[] NOT NULL,
    monitor_path_id bigint NOT NULL DEFAULT nextval('harvesters.monitored_paths_monitor_id_seq'::regclass) ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    CONSTRAINT monitored_paths_pkey PRIMARY KEY (path, harvester_id),
    CONSTRAINT monitored_paths_path_id_key UNIQUE (monitor_path_id)
,
    CONSTRAINT monitored_paths_harvester_id_fkey FOREIGN KEY (harvester_id)
        REFERENCES harvesters.harvesters (id_no) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE harvesters.monitored_paths
    OWNER to postgres;

GRANT SELECT ON TABLE harvesters.monitored_paths TO harvester;

GRANT ALL ON TABLE harvesters.monitored_paths TO postgres;

-- Table: harvesters.observed_files

-- DROP TABLE harvesters.observed_files;

CREATE TABLE harvesters.observed_files
(
    monitor_path_id bigint NOT NULL,
    path text NOT NULL,
    last_observed_size bigint NOT NULL,
    last_observed_time timestamp with time zone NOT NULL,
    file_state harvesters.file_state_t NOT NULL DEFAULT 'UNSTABLE'::harvesters.file_state_t,
    CONSTRAINT observed_files_pkey PRIMARY KEY (monitor_path_id, path),
    CONSTRAINT observed_files_monitor_path_id_fkey FOREIGN KEY (monitor_path_id)
        REFERENCES harvesters.monitored_paths (monitor_path_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE harvesters.observed_files
    OWNER to postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE harvesters.observed_files TO harvester;

GRANT ALL ON TABLE harvesters.observed_files TO postgres;

-- SCHEMA: experiment

-- DROP SCHEMA experiment ;

CREATE SCHEMA experiment
    AUTHORIZATION postgres;

GRANT ALL ON SCHEMA experiment TO postgres;

GRANT USAGE ON SCHEMA experiment TO harvester;

-- Table: experiment.dataset

-- DROP TABLE experiment.dataset;

CREATE TABLE experiment.dataset
(
    id bigserial NOT NULL,
    name text NOT NULL,
    date timestamp with time zone NOT NULL,
    institution text NOT NULL,
    type text NOT NULL,
    PRIMARY KEY (name, date, institution),
    UNIQUE (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.dataset
    OWNER to postgres;

GRANT INSERT, SELECT, TRIGGER ON TABLE experiment.dataset TO harvester;

GRANT SELECT ON TABLE experiment.dataset TO normal_user;

GRANT ALL ON TABLE experiment.dataset TO postgres;

GRANT ALL ON SEQUENCE experiment.dataset_id_seq TO postgres;

GRANT USAGE ON SEQUENCE experiment.dataset_id_seq TO harvester;


-- Table: experiment.access

-- DROP TABLE experiment.access;

CREATE TABLE experiment.access
(
    experiment_id bigint NOT NULL,
    user_name text NOT NULL,
    PRIMARY KEY (experiment_id, user_name),
    FOREIGN KEY (experiment_id)
        REFERENCES experiment.experiments (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.access
    OWNER to postgres;

GRANT INSERT, SELECT ON TABLE experiment.access TO harvester;

GRANT ALL ON TABLE experiment.access TO postgres;

GRANT SELECT ON TABLE experiment.access TO normal_user;

CREATE TABLE experiment.unit
(
    id bigserial NOT NULL,
    name text NOT NULL,
    symbol text NOT NULL,
    description text,
    CONSTRAINT unit_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE experiment.unit
    OWNER to harvester;

ALTER SEQUENCE experiment.unit_id_seq
    OWNER TO harvester;

-- Table: experiment.column_type

-- DROP TABLE experiment.column_type;

CREATE TABLE experiment.column_type
(
    id bigserial NOT NULL,
    name text NOT NULL,
    unit_id bigint,
    CONSTRAINT column_type_pkey PRIMARY KEY (id),
    CONSTRAINT column_type_unit_id_fkey FOREIGN KEY (unit_id)
        REFERENCES experiment.unit (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE experiment.column_type
    OWNER to harvester;

ALTER SEQUENCE experiment.column_type_id_seq
    OWNER TO harvester;

-- Table: experiment."column"

-- DROP TABLE experiment."column";

CREATE TABLE experiment."column"
(
    id bigserial NOT NULL,
    type_id bigint NOT NULL,
    name text NOT NULL,
    CONSTRAINT column_pkey PRIMARY KEY (id),
    CONSTRAINT column_type_id_fkey FOREIGN KEY (type_id)
        REFERENCES experiment.column_type (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE RESTRICT
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE experiment."column"
    OWNER to harvester;

ALTER SEQUENCE experiment.column_id_seq
    OWNER TO harvester;

-- Table: experiment.timeseries_data

-- DROP TABLE experiment.timeseries_data;

CREATE TABLE experiment.timeseries_data
(
    experiment_id bigint NOT NULL,
    sample_no bigint NOT NULL,
    value double precision NOT NULL,
    column_id bigint NOT NULL,
    CONSTRAINT timeseries_data_pkey PRIMARY KEY (experiment_id, sample_no),
    CONSTRAINT timeseries_data_column_id_fkey FOREIGN KEY (column_id)
        REFERENCES experiment."column" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE RESTRICT
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE experiment.timeseries_data
    OWNER to harvester;

-- Table: experiment.metadata

-- DROP TABLE experiment.metadata;

CREATE TABLE experiment.metadata
(
    experiment_id bigint NOT NULL,
    label_name text NOT NULL,
    sample_range int8range NOT NULL,
    info jsonb,
    PRIMARY KEY (experiment_id, label_name),
    FOREIGN KEY (experiment_id)
        REFERENCES experiment.experiments (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.metadata
    OWNER to postgres;

GRANT INSERT ON TABLE experiment.metadata TO harvester;

GRANT SELECT ON TABLE experiment.metadata TO normal_user;

-- SELECT * FROM experiment.data as d
-- INNER JOIN experiment.metadata AS m ON
-- d.experiment_id = m.experiment_id
-- WHERE m.experiment_id = 46 and
--       texteq(m.label_name, 'test_label_1') and
-- 	     d.sample_no <@ m.sample_range

ALTER TABLE experiment.access ENABLE ROW LEVEL SECURITY;

CREATE POLICY access_access_policy ON experiment.access
FOR SELECT USING ( user_name = current_user);

ALTER TABLE experiment.experiments ENABLE ROW LEVEL SECURITY;

CREATE POLICY experiments_access_policy ON experiment.experiments
FOR SELECT USING ( current_user in (SELECT user_name FROM experiment.access
									WHERE experiment_id = experiment.experiments.id));

ALTER TABLE experiment.metadata ENABLE ROW LEVEL SECURITY;

CREATE POLICY metadata_access_policy ON experiment.metadata
FOR SELECT USING ( current_user in (SELECT user_name FROM experiment.access
									WHERE experiment_id = experiment.metadata.experiment_id));

CREATE POLICY experiments_harvester_policy ON experiment.experiments
FOR ALL TO harvester USING (true);

CREATE POLICY access_harvester_policy ON experiment.access
FOR ALL TO harvester USING (true);

CREATE POLICY metadata_harvester_policy ON experiment.metadata
FOR ALL TO harvester USING (true);