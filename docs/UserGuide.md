# Galvalanyser User Guide

For help on setting up the Galvanalyser server and Harvesters, see the
[First Time Quick Setup guide](FirstTimeQuickSetup.md)

## Galvanalyser server

Once set up, the Galvanalyser server instance should not need attending to.

You may wish to provide a proxy server for it, especially if it is to be
open to the web. A proxy server such as [nginx](https://www.nginx.com/)
will provide simple proxy services, allowing you to abstract SSL and other
layers away from the Galvanalyser server instance. 
If running a proxy, bear in mind that Galvanalyser requires the following
ports to be exposed:
- 80 HTTP web frontend
- 5000 HTTP REST API

These ports can be changed in the `docker-compose.yml` file.

### User accounts

User accounts are created via the [web frontend](#web-frontend).
Each user account must be approved by an existing user before it can log on
to the system. 
Once user accounts are created and approved, they can be assigned roles
on Harvesters and Paths.

#### User roles

Each [Harvester](#harvesters) requires at least one administrator, and may 
have as many additional administrators as required.
Each Harvester administrator has the following rights:
- Edit Harvester details (name, sleep time)
- Appoint other users to administrator role
- Remove administrators (except the last administrator)
- Create new [Monitored paths](#monitored-paths)
- Perform any of the administrator actions for any of the Harvester's Paths

Harvesters have [Paths](#monitored-paths) - directories which are monitored for data files.
Each Path may have any number of administrators and users.
The Path's Harvester administrators have the same rights as the Path's administrators.
Path administrators may:
- Edit Path details (path, stable time)
- Appoint other users to administrator and user roles
- Remove users from administrator and user roles
- Perform any of the Path user actions

Path users may:
- View and edit details of datafiles found in the Path directory
- View and edit datasets produced when those datafiles are imported

Additionally, any registered user may create, and view Cell and Equipment details.
They may also edit and delete those Cell and Equipment instances provided that no
datasets are using them.

### REST API

Endpoints are written as absolute paths starting from the Galvanalyser server
address, so to reach the `/harvesters/` endpoint for a Galvanalyser server 
located at `http://localhost`, you would go to `http://localhost/harvesters/`.

#### API Spec

The REST API provides a browsable interface at `/spec/swagger-ui/`.
Its OpenAPI spec can be downloaded from `/spec/`.
Spec download defaults to `.yml` format, but `.json` is available from `/spec/?format=json`.

#### Browsable API

The browsable API provided by Django REST Framework is not fully functional, 
but does provide a relatively useful way to browse the raw data on the REST API.
It is provided at the base address (endpoint `/`), and provides its own list of 
available endpoints.

### Web frontend

The primary tool for interacting with the REST API is the web frontend.
This is designed to provide a user-friendly way to view and edit [Harvesters](#harvesters),
[Paths](#monitored-paths), [Datasets](#datasets) and their metadata.

The web frontend is accessed via a [User account](#user-accounts), 
and allows new user accounts to be created and approved by existing users.
Each user's view of the web frontend is customised to only include information
relevant to them.

#### Datasets page

When first successfully logging in with an active account, the user will land
on the Datasets page.
This page lists information about any [Datasets](#datasets) that have been 
imported from files in a [Monitored path](#monitored-paths) that the user 
has access to. 

The first time you log in, this is likely to be blank. 
Once some datasets have been imported, you will see them listed here and
you will be able to edit their metadata.

Each dataset can be described in terms of its name and type, 
a purpose selected from a pre-populated list, and may be associated with 
the particular [Cell](#cell-page) that generated it, as well as any
[Equipment](#equipment-page) that was used.

##### Data view

Clicking the magnifying glass icon for a dataset allows you to inspect the data.
This will bring up two buttons which provide boilerplate code for accessing the
data using the [Python client](#python-client) or MATLAB, as well as a plot of
the voltage and ampage of the cell over the duration of the test.

Additional columns in the data can be added to the preview graph by clicking on their
names.

#### Harvesters page

The Harvesters page lists [Harvesters](#harvesters) that you have access to,
either because you are an administrator of that Harvester, or because you are
a user or administrator on one or more of the Harvester's [Paths](#monitored-paths).

If you are an administrator on the Harvester, you will be able to modify the
Harvester properties, changing the Harvester name or the sleep time. 
Sleep time governs how long the Harvester spends idle between harvest cycles.

##### Monitored paths view

Click on the magnifying glass icon to view the selected Harvester's Paths.
The Path view shows the [Monitored paths](#monitored-paths) on the Harvester
that you can access. 
If you have sufficient permissions, you will be able to alter Path details,
including the directory path, the length of time files must be stable before 
attempting import, and user permissions.

###### File view

Click on the magnifying glass icon to view the Files found in the Monitored path.
These are read-only because their properties are directly dependent on the actual
files in the monitored directory.
If any file has failed to import, the last error associated with that import will
appear when you mouse-over the IMPORT FAILED state. 

If for any reason you want to force the harvester to attempt to import a file
that has failed to import correctly, you can do so by clicking the refresh button
in the 'Force Re-import' column.

Files that have been successfully imported will show at least one linked [Dataset](#datasets).
Once you have some, your initial [Dataset view](#datasets-page) will be populated
and you can add metadata to your dataset.

#### Cell page

Each dataset will be generated by a specific cell. 
The Cell page is where you can provide information about cells, which you can 
then link to their datasets in the [Datasets page](#datasets-page).

The majority of cell properties are grouped together in a Cell family. 
The family contains generic information about name, manufacturer, form factor, 
chemistry, and capacity and weight statistics. 
For any cell family that is not currently in use, you can edit its properties.
You can also create new cell families. 

Once you have a cell family that you would like to create a cell for, click on 
the magnifying glass icon to view its cells. 
A cell should have a unique identifier which should be a globally unique value
that specifically identifies that cell. 
A good choice is to use the serial number of the physical cell you are describing.
Cells may also have display names so that they are easier to identify when adding
metadata to datasets.
Where cells are not in use by a dataset, 
you can edit their unique identifiers and display names.

#### Equipment page

Equipment can be defined on the equipment page. 
Equipment has a name and a type, and these can be edited for any equipment
that is not in use by a dataset.

### Python client



## Harvesters



### Monitored paths

## Datasets
