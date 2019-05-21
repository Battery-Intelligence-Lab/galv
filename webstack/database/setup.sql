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
    path text COLLATE pg_catalog."default" NOT NULL,
    monitored_for text[] COLLATE pg_catalog."default" NOT NULL,
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
    path text COLLATE pg_catalog."default" NOT NULL,
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