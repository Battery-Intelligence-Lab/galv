

Folder Structure
----------------
.
├── config
├── galvanalyser -- The python code goes here, all under the galvanalyser namespace
│   ├── database -- Library files for interacting with the database
│   ├── harvester -- The harvester app
│   ├── protobuf -- Automatically generated protobuf python code
│   └── webapp -- The webapp
├── harvester -- Harvester docker file
├── libs -- assorted dependency libraries
│   ├── closure-library -- google library, used for building the single js file for protobufs and dependencies, provides AVL Tree data structure
│   ├── galvanalyser-js-protobufs  -- Automatically generated protobuf javascript code
│   └── protobuf -- google protobuf library
├── protobuf -- definition of the protobufs used in this project
├── tests -- Tests (these are old and may not work anymore and aren't proper unit tests)
│   └── harvester
├── webapp-static-content -- Static content served by nginx
│   ├── js -- Custom JS files can go here
│   └── libs -- The automatically generated js file made by closure-library gets put here
└── webstack -- Docker-compose things go here
    ├── dashapp -- The dockerfile for the web app
    ├── database -- The sql file for setting up the database (should probably move elsewhere)
    └── nginx-config -- The nginx config file