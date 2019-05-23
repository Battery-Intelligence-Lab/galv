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

-- Table: experiment.experiments

-- DROP TABLE experiment.experiments;

CREATE TABLE experiment.experiments
(
    id bigserial NOT NULL,
    name text,
    date timestamp with time zone,
    type text NOT NULL,
    PRIMARY KEY (name, date),
    UNIQUE (id)

)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.experiments
    OWNER to postgres;

GRANT INSERT, SELECT, TRIGGER ON TABLE experiment.experiments TO harvester;

GRANT ALL ON TABLE experiment.experiments TO postgres;

GRANT ALL ON SEQUENCE experiment.experiments_id_seq TO postgres;

GRANT USAGE ON SEQUENCE experiment.experiments_id_seq TO harvester;

-- Table: experiment.access

-- DROP TABLE experiment.access;

CREATE TABLE experiment.access
(
    experiment_id bigint NOT NULL,
    user_name text NOT NULL,
    PRIMARY KEY (experiment_id, user_name),
    FOREIGN KEY (experiment_id)
        REFERENCES experiment.experiments (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.access
    OWNER to postgres;

GRANT INSERT, SELECT ON TABLE experiment.access TO harvester;

GRANT ALL ON TABLE experiment.access TO postgres;

-- FUNCTION: experiment.create_child_data_table()

-- DROP FUNCTION experiment.create_child_data_table();

CREATE FUNCTION experiment.create_child_data_table()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF 
AS $BODY$
	DECLARE
    temprow RECORD;
	remainder integer;
BEGIN
	FOR temprow IN
SELECT DISTINCT id FROM public.data_default
LOOP
remainder = temprow.experiment_id % 256;
RAISE NOTICE 'CREATING TABLE experiment.data_%',remainder;
EXECUTE format('CREATE TABLE IF NOT EXISTS "experiment.data_%s" PARTITION OF experiment.data ( PRIMARY KEY (experiment_id, sample_no)) FOR VALUES IN (%s);', remainder, remainder);
END LOOP;

RETURN NULL;
END;$BODY$;

ALTER FUNCTION experiment.create_child_data_table()
    OWNER TO postgres;


CREATE TABLE experiment.data
(
    experiment_id bigint NOT NULL,
    sample_no bigint NOT NULL,
    test_time double precision NOT NULL,
    volts double precision NOT NULL,
    amps double precision NOT NULL,
    capacity double precision,
    temperature double precision,
    FOREIGN KEY (experiment_id)
        REFERENCES experiment.experiments (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
) PARTITION BY LIST ((experiment_id % 256)) 
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.data
    OWNER to postgres;

GRANT INSERT, SELECT, UPDATE, DELETE, TRIGGER ON TABLE experiment.data TO harvester;

-- Trigger: data_insert_create_table_trigger

-- DROP TRIGGER data_insert_create_table_trigger ON experiment.data;

CREATE TRIGGER data_insert_create_table_trigger
    AFTER INSERT
    ON experiment.data
    FOR EACH STATEMENT
    EXECUTE PROCEDURE experiment.create_child_data_table();

-- Partitions SQL

CREATE TABLE experiment.data_default PARTITION OF experiment.data_insert_create_table_trigger
    DEFAULT;