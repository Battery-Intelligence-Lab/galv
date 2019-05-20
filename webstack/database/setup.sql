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
    monitored_for text NOT NULL,
    path text,
    PRIMARY KEY (harvester_id, monitored_for, path),
    FOREIGN KEY (harvester_id)
        REFERENCES harvesters.harvesters (id_no) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
);

ALTER TABLE harvesters.monitored_paths
    OWNER to postgres;

GRANT SELECT ON TABLE harvesters.monitored_paths TO harvester;

GRANT ALL ON TABLE harvesters.monitored_paths TO postgres;

-- Table: harvesters.observed_files

-- DROP TABLE harvesters.observed_files;

CREATE TABLE harvesters.observed_files
(
    harvester_id bigint NOT NULL,
    path text NOT NULL,
    last_observed_size bigint NOT NULL,
    last_observed_time timestamp with time zone NOT NULL,
    PRIMARY KEY (harvester_id, path),
    FOREIGN KEY (harvester_id)
        REFERENCES harvesters.harvesters (id_no) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
);

ALTER TABLE harvesters.observed_files
    OWNER to postgres;

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE harvesters.observed_files TO harvester;