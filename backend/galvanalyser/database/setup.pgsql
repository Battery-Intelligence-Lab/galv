-- SCHEMA: user_data

-- DROP SCHEMA user_data ;

CREATE SCHEMA user_data
    AUTHORIZATION postgres;

GRANT ALL ON SCHEMA user_data TO postgres;

-- Table: user_data.user

-- DROP TABLE user_data.user;

CREATE TABLE user_data.user
(
  id bigserial PRIMARY KEY,
  username VARCHAR (100),
  password VARCHAR (64), --storing a 32-bit hash
  salt VARCHAR (64), --storing a 32-bit salt
  email VARCHAR (100),
  UNIQUE (username),
  CONSTRAINT username_email_notnull CHECK (
    NOT (
      ( username IS NULL  OR  username = '' )
      AND
      ( email IS NULL  OR  email = '' )
    )
  )
)
WITH (
    OIDS = FALSE
);


ALTER TABLE user_data.user
    OWNER to postgres;

-- Table: user_data.group

-- DROP TABLE user_data.group;

CREATE TABLE user_data.group
(
  id bigserial PRIMARY KEY,
  groupname VARCHAR (100),
  UNIQUE (groupname),
  CONSTRAINT name_notnull CHECK (
    NOT ( groupname IS NULL  OR  groupname = '' )
  )
)
WITH (
    OIDS = FALSE
);


ALTER TABLE user_data.group
    OWNER to postgres;


-- SCHEMA: harvesters

-- DROP SCHEMA harvesters ;

CREATE SCHEMA harvesters
    AUTHORIZATION postgres;

GRANT ALL ON SCHEMA harvesters TO postgres;

GRANT USAGE ON SCHEMA harvesters TO ${harvester_role};

-- Table: harvesters.harvester

-- DROP TABLE harvesters.harvester;

CREATE TABLE harvesters.harvester
(
    id bigserial NOT NULL,
    machine_id text NOT NULL,
    harvester_name text,
    last_successful_run timestamp with time zone,
    is_running bool DEFAULT FALSE,
    periodic_hour integer,
    PRIMARY KEY (id),
    UNIQUE (machine_id),
    CONSTRAINT is_hour CHECK (periodic_hour >= 0 AND periodic_hour < 24)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE harvesters.harvester
    OWNER to postgres;

GRANT UPDATE, SELECT ON TABLE harvesters.harvester TO ${harvester_role};

GRANT ALL ON TABLE harvesters.harvester TO postgres;

ALTER TABLE harvesters.harvester ENABLE ROW LEVEL SECURITY;

CREATE POLICY harvester_access_policy ON harvesters.harvester
USING ( harvester_name = current_user);


-- Table: harvesters.monitored_path

-- DROP TABLE harvesters.monitored_path;

CREATE TABLE harvesters.monitored_path
(
    harvester_id bigint NOT NULL,
    path text NOT NULL,
    monitor_path_id bigserial NOT NULL,
    UNIQUE (path, harvester_id),
    PRIMARY KEY (monitor_path_id),
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

GRANT SELECT ON TABLE harvesters.monitored_path TO ${harvester_role};

GRANT ALL ON TABLE harvesters.monitored_path TO postgres;

-- Table: experiment.monitored_for

-- DROP TABLE experiment.monitored_for;

CREATE TABLE harvesters.monitored_for
(
    path_id bigint NOT NULL,
    user_id bigint NOT NULL,
    PRIMARY KEY (path_id, user_id),
    FOREIGN KEY (path_id)
        REFERENCES harvesters.monitored_path (monitor_path_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
        REFERENCES user_data.user (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
);

ALTER TABLE harvesters.monitored_for
    OWNER to postgres;

GRANT ALL ON TABLE harvesters.monitored_for TO postgres;

GRANT SELECT ON TABLE harvesters.monitored_for TO ${harvester_role};

-- Type: file_state_t

-- DROP TYPE harvesters.file_state_t;

CREATE TYPE harvesters.file_state_t AS ENUM
    ('IMPORTED', 'IMPORTING', 'STABLE', 'UNSTABLE', 'IMPORT_FAILED', 'GROWING');

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

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE harvesters.observed_file TO ${harvester_role};

GRANT ALL ON TABLE harvesters.observed_file TO postgres;

-- SCHEMA: cell_data

-- DROP SCHEMA cell_data ;

CREATE SCHEMA cell_data
    AUTHORIZATION postgres;

GRANT USAGE ON SCHEMA cell_data TO ${harvester_role};

-- Table: cell_data.cell

-- DROP TABLE cell_data.cell;

CREATE TABLE cell_data.cell
(
    id bigserial NOT NULL,
    name text NOT NULL,
    cell_form_factor varchar(11),
    link_to_datasheet text,
    anode_chemistry text,
    cathode_chemistry text,
    nominal_capacity double precision,
    nominal_cell_weight double precision,
    manufacturer text,
    CONSTRAINT cell_unique_name UNIQUE (name),
    CONSTRAINT cell_pkey PRIMARY KEY (id)
) WITH (
    OIDS = FALSE
);

ALTER TABLE cell_data.cell
    OWNER to postgres;

GRANT SELECT ON TABLE cell_data.cell TO ${harvester_role};

GRANT ALL ON TABLE cell_data.cell TO postgres;


-- SCHEMA: experiment

-- DROP SCHEMA experiment ;

CREATE SCHEMA experiment
    AUTHORIZATION postgres;

GRANT ALL ON SCHEMA experiment TO postgres;

GRANT USAGE ON SCHEMA experiment TO ${harvester_role};

-- Table: experiment.dataset

-- DROP TABLE experiment.dataset;

CREATE TABLE experiment.dataset
(
    id bigserial NOT NULL,
    name text NOT NULL,
    date timestamp with time zone NOT NULL,
    type text NOT NULL,
    cell_id bigint,
    owner_id bigint,
    purpose text,
    json_data jsonb,
    
    PRIMARY KEY (name, date),
    FOREIGN KEY (cell_id)
        REFERENCES cell_data.cell (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    FOREIGN KEY (owner_id)
        REFERENCES user_data.user (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    UNIQUE (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.dataset
    OWNER to postgres;

GRANT INSERT, UPDATE, SELECT, TRIGGER ON TABLE experiment.dataset TO ${harvester_role};

GRANT ALL ON TABLE experiment.dataset TO postgres;

GRANT ALL ON SEQUENCE experiment.dataset_id_seq TO postgres;

GRANT USAGE ON SEQUENCE experiment.dataset_id_seq TO ${harvester_role};

-- Table: experiment.equipment

-- DROP TABLE experiment.equipment;

CREATE TABLE experiment.equipment
(
    id bigserial NOT NULL,
    name VARCHAR (50) NOT NULL,
    type VARCHAR (50),
    UNIQUE (name),
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.equipment
    OWNER to postgres;

GRANT ALL ON TABLE experiment.equipment TO postgres;

-- Table: experiment.dataset_equipment

-- DROP TABLE experiment.dataset_equipment;

CREATE TABLE experiment.dataset_equipment
(
    dataset_id bigint NOT NULL,
    equipment_id bigint NOT NULL,
    PRIMARY KEY (dataset_id, equipment_id),
    FOREIGN KEY (dataset_id)
        REFERENCES experiment.dataset (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (equipment_id)
        REFERENCES experiment.equipment (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.dataset_equipment
    OWNER to postgres;

GRANT ALL ON TABLE experiment.dataset_equipment TO postgres;


-- Table: experiment.access

-- DROP TABLE experiment.access;

CREATE TABLE experiment.access
(
    dataset_id bigint NOT NULL,
    user_id bigint NOT NULL,
    PRIMARY KEY (dataset_id, user_id),
    FOREIGN KEY (dataset_id)
        REFERENCES experiment.dataset (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
        REFERENCES user_data.user (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
);

ALTER TABLE experiment.access
    OWNER to postgres;

GRANT INSERT, SELECT ON TABLE experiment.access TO ${harvester_role};

GRANT ALL ON TABLE experiment.access TO postgres;

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
    OWNER TO ${harvester_role};

ALTER SEQUENCE experiment.unit_id_seq
    OWNER TO ${harvester_role};

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
    OWNER TO ${harvester_role};

ALTER SEQUENCE experiment.column_type_id_seq
    OWNER TO ${harvester_role};

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
    OWNER TO ${harvester_role};

ALTER SEQUENCE experiment.column_id_seq
    OWNER TO ${harvester_role};

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
INSERT INTO experiment.column_type (id, name, unit_id) VALUES (7, 'Impedence Magnitude', 8);
INSERT INTO experiment.column_type (id, name, unit_id) VALUES (8, 'Impedence Phase', 9);
INSERT INTO experiment.column_type (id, name, unit_id) VALUES (9, 'Frequency', 10);
SELECT setval('experiment.column_type_id_seq'::regclass, 9);

INSERT INTO experiment."column" (id, type_id, name, description) VALUES (0, 0, 'Sample Number', 'The sample or record number. Is increased by one each time a test machine records a reading. Usually counts from 1 at the start of a test');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (1, 1, 'Test Time', 'The time in seconds since the test run began.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (2, 2, 'Volts', 'The voltage of the cell.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (3, 3, 'Amps', 'The current current.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (4, 4, 'Energy Capacity', 'The Energy Capacity.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (5, 5, 'Charge Capacity', 'The Charge Capacity.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (6, 6, 'Temperature', 'The temperature.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (7, 1, 'Step Time', 'The time in seconds since the current step began.');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (8, 7, 'Impedence Magnitude', 'The magnitude of the impedence (EIS).');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (9, 8, 'Impedence Phase', 'The phase of the impedence (EIS).');
INSERT INTO experiment."column" (id, type_id, name, description) VALUES (10, 9, 'Frequency', 'The frequency of the input EIS voltage signal.');
SELECT setval('experiment.column_id_seq'::regclass, 10);


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
    OWNER TO ${harvester_role};

CREATE INDEX timeseries_data_dataset_id ON experiment.timeseries_data (dataset_id);
CREATE INDEX timeseries_data_dataset_id_column_id ON experiment.timeseries_data (dataset_id, value) WHERE column_id = 1;

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

GRANT INSERT, SELECT, UPDATE ON TABLE experiment.range_label TO ${harvester_role};

GRANT USAGE ON SEQUENCE experiment.range_label_id_seq TO ${harvester_role};

-- SELECT * FROM experiment.data as d
-- INNER JOIN experiment.range_label AS m ON
-- d.dataset_id = m.dataset_id
-- WHERE m.dataset_id = 46 and
--       texteq(m.label_name, 'test_label_1') and
-- 	     d.sample_no <@ m.sample_range
