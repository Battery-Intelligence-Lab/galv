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
    PRIMARY KEY (id),
    UNIQUE (machine_id)

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
    CONSTRAINT observed_file_pkey PRIMARY KEY (monitor_path_id, path),
    FOREIGN KEY (monitor_path_id)
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

GRANT USAGE ON SCHEMA experiment TO normal_user;

-- Table: experiment.institution

-- DROP TABLE experiment.institution;

CREATE TABLE experiment.institution
(
    id bigserial NOT NULL,
    name text NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (name)
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

-- Table: experiment.misc_file_data

-- DROP TABLE experiment.misc_file_data;

CREATE TABLE experiment.misc_file_data
(
    dataset_id bigint NOT NULL,
    sample_range int8range NOT NULL,
    key text NOT NULL,
    json_data jsonb,
    binary_data bytea,
    PRIMARY KEY (dataset_id, sample_range, key),
    FOREIGN KEY (dataset_id)
        REFERENCES experiment.dataset (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.misc_file_data
    OWNER to harvester;

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
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE experiment.unit
    OWNER to harvester;

GRANT SELECT ON TABLE experiment.unit TO normal_user;

ALTER SEQUENCE experiment.unit_id_seq
    OWNER TO harvester;

-- Table: experiment.column_type

-- DROP TABLE experiment.column_type;

CREATE TABLE experiment.column_type
(
    id bigserial NOT NULL,
    name text NOT NULL,
    unit_id bigint,
    PRIMARY KEY (id),
    FOREIGN KEY (unit_id)
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

GRANT SELECT ON TABLE experiment.column_type TO normal_user;

ALTER SEQUENCE experiment.column_type_id_seq
    OWNER TO harvester;

-- Table: experiment."column"

-- DROP TABLE experiment."column";

CREATE TABLE experiment."column"
(
    id bigserial NOT NULL,
    type_id bigint NOT NULL,
    name text NOT NULL,
    description text,
    PRIMARY KEY (id),
    FOREIGN KEY (type_id)
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

GRANT SELECT ON TABLE experiment."column" TO normal_user;

ALTER SEQUENCE experiment.column_id_seq
    OWNER TO harvester;

-- Add required column

INSERT INTO experiment.unit (id, name, symbol, description) VALUES (0, 'Unitless', '', 'A value with no units');
INSERT INTO experiment.unit (id, name, symbol, description) VALUES (1, 'Time', 's', 'Time in seconds');
INSERT INTO experiment.unit (id, name, symbol, description) VALUES (2, 'Volts', 'V', 'Voltage');
INSERT INTO experiment.unit (id, name, symbol, description) VALUES (3, 'Amps', 'A', 'Current');
INSERT INTO experiment.unit (id, name, symbol, description) VALUES (4, 'Energy', 'Wh', 'Energy in Watt-Hours');
INSERT INTO experiment.unit (id, name, symbol, description) VALUES (5, 'Charge', 'Ah', 'Charge in Amp-Hours');
INSERT INTO experiment.unit (id, name, symbol, description) VALUES (6, 'Temperature', '°c', 'Temperature in Centigrade');
INSERT INTO experiment.unit (id, name, symbol, description) VALUES (7, 'Power', 'W', 'Power in Watts');
INSERT INTO experiment.unit (id, name, symbol, description) VALUES (8, 'Ohm', 'Ω', 'Resistance or impediance in Ohms');
INSERT INTO experiment.unit (id, name, symbol, description) VALUES (9, 'Degrees', '°', 'Angle in degrees');
INSERT INTO experiment.unit (id, name, symbol, description) VALUES (10, 'Frequency', 'Hz', 'Frequency in Hz');
SELECT setval('experiment.unit_id_seq'::regclass, 10);

INSERT INTO experiment.column_type (id, name, unit_id) VALUES (-1, 'Unknown', NULL);
INSERT INTO experiment.column_type (id, name, unit_id) VALUES (0, 'Sample Number', 0);
INSERT INTO experiment.column_type (id, name, unit_id) VALUES (1, 'Time', 1);
INSERT INTO experiment.column_type (id, name, unit_id) VALUES (2, 'Volts', 2);
INSERT INTO experiment.column_type (id, name, unit_id) VALUES (3, 'Amps', 3);
INSERT INTO experiment.column_type (id, name, unit_id) VALUES (4, 'Energy Capacity', 4);
INSERT INTO experiment.column_type (id, name, unit_id) VALUES (5, 'Charge Capacity', 5);
INSERT INTO experiment.column_type (id, name, unit_id) VALUES (6, 'Temperature', 6);
SELECT setval('experiment.column_type_id_seq'::regclass, 6);

INSERT INTO experiment."column" (id, type_id, name, description) VALUES (0, 0, 'Sample Number', 'The sample or record number. Is increased by one each time a test machine records a reading. Usually counts from 1 at the start of a test');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (1, 1, 'Test Time', 'The time in seconds since the test run began.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (2, 2, 'Volts', 'The voltage of the cell.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (3, 3, 'Amps', 'The current current.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (4, 4, 'Energy Capacity', 'The Energy Capacity.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (5, 5, 'Charge Capacity', 'The Charge Capacity.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (6, 6, 'Temperature', 'The temperature.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (7, 1, 'Step Time', 'The time in seconds since the current step began.');
SELECT setval('experiment.column_id_seq'::regclass, 7);


-- Table: experiment.timeseries_data

-- DROP TABLE experiment.timeseries_data;

CREATE TABLE experiment.timeseries_data
(
    dataset_id bigint NOT NULL,
    sample_no bigint NOT NULL,
    column_id bigint NOT NULL,
    value double precision NOT NULL,
    PRIMARY KEY (dataset_id, sample_no, column_id),
    FOREIGN KEY (column_id)
        REFERENCES experiment."column" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (dataset_id)
        REFERENCES experiment.dataset (id) MATCH SIMPLE
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

-- Table: experiment.range_label

-- DROP TABLE experiment.range_label;

CREATE TABLE experiment.range_label
(
    id bigserial NOT NULL,
    dataset_id bigint NOT NULL,
    label_name text NOT NULL,
	created_by text NOT NULL,
    sample_range int8range NOT NULL,
    info jsonb,
    PRIMARY KEY (dataset_id, label_name, created_by),
    FOREIGN KEY (dataset_id)
        REFERENCES experiment.dataset (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    UNIQUE (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.range_label
    OWNER to postgres;

GRANT INSERT, SELECT, UPDATE ON TABLE experiment.range_label TO harvester;

GRANT SELECT ON TABLE experiment.range_label TO normal_user;

GRANT USAGE ON SEQUENCE experiment.range_label_id_seq TO harvester;

-- SELECT * FROM experiment.data as d
-- INNER JOIN experiment.range_label AS m ON
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

ALTER TABLE experiment.range_label ENABLE ROW LEVEL SECURITY;

CREATE POLICY range_label_access_policy ON experiment.range_label
FOR SELECT USING ( current_user in (SELECT user_name FROM experiment.access
									WHERE dataset_id = experiment.range_label.dataset_id));

CREATE POLICY dataset_harvester_policy ON experiment.dataset
FOR ALL TO harvester USING (true);

CREATE POLICY access_harvester_policy ON experiment.access
FOR ALL TO harvester USING (true);

CREATE POLICY range_label_harvester_policy ON experiment.range_label
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
