-- User: harvester_user
-- DROP USER harvester_user;

CREATE USER harvester_user WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  PASSWORD 'password';

GRANT harvester TO harvester_user;

-- User: alice
-- DROP USER alice;

CREATE USER alice WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  PASSWORD 'alice_pass';

GRANT normal_user TO alice;

-- User: bob
-- DROP USER bob;

CREATE USER bob WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  PASSWORD 'bob_pass';

GRANT normal_user TO bob;

-- SAMPLE DATA

DO $$ 
DECLARE
   the_id integer;
BEGIN 
    INSERT INTO harvesters.harvester (machine_id) VALUES ('test_machine_01') RETURNING id INTO the_id;
    INSERT INTO harvesters.monitored_path (harvester_id, path, monitored_for) VALUES (the_id, '/usr/src/app/config/test-data', '{alice}');
    INSERT INTO experiment.institution (name) VALUES ('Oxford');
END $$;