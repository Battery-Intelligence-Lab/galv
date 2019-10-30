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

-- Table: harvesters.harvester

-- DROP TABLE harvesters.harvester;

CREATE TABLE harvesters.harvester
(
    id bigserial NOT NULL,
    machine_id text NOT NULL,
    CONSTRAINT harvester_pkey PRIMARY KEY (id),
    CONSTRAINT harvester_machine_id_key UNIQUE (machine_id)

)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE harvesters.harvester
    OWNER to postgres;

GRANT SELECT ON TABLE harvesters.harvester TO harvester;

GRANT ALL ON TABLE harvesters.harvester TO postgres;

-- Table: harvesters.monitored_path

-- DROP TABLE harvesters.monitored_path;

CREATE TABLE harvesters.monitored_path
(
    harvester_id bigint NOT NULL,
    path text NOT NULL,
    monitored_for text[] NOT NULL,
    monitor_path_id bigserial NOT NULL,
    PRIMARY KEY (path, harvester_id),
    UNIQUE (monitor_path_id),
    FOREIGN KEY (harvester_id)
        REFERENCES harvesters.harvester (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE harvesters.monitored_path
    OWNER to postgres;

GRANT SELECT ON TABLE harvesters.monitored_path TO harvester;

GRANT ALL ON TABLE harvesters.monitored_path TO postgres;

-- Type: file_state_t

-- DROP TYPE harvesters.file_state_t;

CREATE TYPE harvesters.file_state_t AS ENUM
    ('IMPORTED', 'IMPORTING', 'STABLE', 'UNSTABLE', 'IMPORT_FAILED');

ALTER TYPE harvesters.file_state_t
    OWNER TO postgres;


-- Table: harvesters.observed_file

-- DROP TABLE harvesters.observed_file;

CREATE TABLE harvesters.observed_file
(
    monitor_path_id bigint NOT NULL,
    path text NOT NULL,
    last_observed_size bigint NOT NULL,
    last_observed_time timestamp with time zone NOT NULL,
    file_state harvesters.file_state_t NOT NULL DEFAULT 'UNSTABLE'::harvesters.file_state_t,
    CONSTRAINT observed_files_pkey PRIMARY KEY (monitor_path_id, path),
    CONSTRAINT observed_files_monitor_path_id_fkey FOREIGN KEY (monitor_path_id)
        REFERENCES harvesters.monitored_path (monitor_path_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE harvesters.observed_file
    OWNER to postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE harvesters.observed_file TO harvester;

GRANT ALL ON TABLE harvesters.observed_file TO postgres;

-- SCHEMA: experiment

-- DROP SCHEMA experiment ;

CREATE SCHEMA experiment
    AUTHORIZATION postgres;

GRANT ALL ON SCHEMA experiment TO postgres;

GRANT USAGE ON SCHEMA experiment TO harvester;

-- Table: experiment.institution

-- DROP TABLE experiment.institution;

CREATE TABLE experiment.institution
(
    id bigserial NOT NULL,
    name text NOT NULL,
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.institution
    OWNER to postgres;

GRANT SELECT ON TABLE experiment.institution TO harvester;

GRANT SELECT ON TABLE experiment.institution TO normal_user;

-- Table: experiment.dataset

-- DROP TABLE experiment.dataset;

CREATE TABLE experiment.dataset
(
    id bigserial NOT NULL,
    name text NOT NULL,
    date timestamp with time zone NOT NULL,
    institution_id bigint NOT NULL,
    type text NOT NULL,
    PRIMARY KEY (name, date, institution_id),
    UNIQUE (id),
    FOREIGN KEY (institution_id)
        REFERENCES experiment.institution (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE RESTRICT
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
    dataset_id bigint NOT NULL,
    user_name text NOT NULL,
    PRIMARY KEY (dataset_id, user_name),
    FOREIGN KEY (dataset_id)
        REFERENCES experiment.dataset (id) MATCH SIMPLE
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
    dataset_id bigint NOT NULL,
    sample_no bigint NOT NULL,
    column_id bigint NOT NULL,
    value double precision NOT NULL,
    CONSTRAINT timeseries_data_pkey PRIMARY KEY (dataset_id, sample_no, column_id),
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

GRANT SELECT ON TABLE experiment.timeseries_data TO normal_user;

-- Table: experiment.metadata

-- DROP TABLE experiment.metadata;

CREATE TABLE experiment.range_label
(
    dataset_id bigint NOT NULL,
    label_name text NOT NULL,
	created_by text NOT NULL,
    sample_range int8range NOT NULL,
    info jsonb,
    PRIMARY KEY (dataset_id, label_name, created_by),
    FOREIGN KEY (dataset_id)
        REFERENCES experiment.dataset (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.metadata
    OWNER to postgres;

GRANT INSERT, SELECT, UPDATE ON TABLE experiment.metadata TO harvester;

GRANT SELECT ON TABLE experiment.metadata TO normal_user;

-- SELECT * FROM experiment.data as d
-- INNER JOIN experiment.metadata AS m ON
-- d.dataset_id = m.dataset_id
-- WHERE m.dataset_id = 46 and
--       texteq(m.label_name, 'test_label_1') and
-- 	     d.sample_no <@ m.sample_range

ALTER TABLE experiment.access ENABLE ROW LEVEL SECURITY;

CREATE POLICY access_access_policy ON experiment.access
FOR SELECT USING ( user_name = current_user);

ALTER TABLE experiment.dataset ENABLE ROW LEVEL SECURITY;

CREATE POLICY dataset_access_policy ON experiment.dataset
FOR SELECT USING ( current_user in (SELECT user_name FROM experiment.access
									WHERE dataset_id = experiment.dataset.id));

ALTER TABLE experiment.metadata ENABLE ROW LEVEL SECURITY;

CREATE POLICY metadata_access_policy ON experiment.metadata
FOR SELECT USING ( current_user in (SELECT user_name FROM experiment.access
									WHERE dataset_id = experiment.metadata.dataset_id));

CREATE POLICY dataset_harvester_policy ON experiment.dataset
FOR ALL TO harvester USING (true);

CREATE POLICY access_harvester_policy ON experiment.access
FOR ALL TO harvester USING (true);

CREATE POLICY metadata_harvester_policy ON experiment.metadata
FOR ALL TO harvester USING (true);

-- SCHEMA: user_data

-- DROP SCHEMA user_data ;

CREATE SCHEMA user_data
    AUTHORIZATION postgres;

GRANT ALL ON SCHEMA user_data TO postgres;

GRANT USAGE ON SCHEMA user_data TO normal_user;

CREATE TABLE user_data.range_label
(
    access text[],
    PRIMARY KEY (dataset_id, label_name, created_by),
    FOREIGN KEY (dataset_id)
        REFERENCES experiment.dataset (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
    INHERITS (experiment.range_label)
WITH (
    OIDS = FALSE
);

ALTER TABLE user_data.range_label
    OWNER to postgres;

GRANT INSERT, SELECT, UPDATE ON TABLE user_data.range_label TO normal_user;