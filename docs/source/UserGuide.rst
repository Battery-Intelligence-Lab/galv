######################################################################################
Galvalanyser User Guide
######################################################################################

For help on setting up the Galvanalyser server and Harvesters, see the
:doc:`FirstTimeQuickSetup` guide.

Galvanalyser server
==================================================================================

Once set up, the Galvanalyser server instance should not need attending to.
To set it up, all you need to do is change the .env file's VIRTUAL_HOST_ROOT
and LETSENCRYPT_EMAIL variables to your domain name and email.
When you've verified that it works, you can also set LETSENCRYPT_TEST to false
to generate real SSL certificates that you do not need to manually accept.
It exposes two webservers: the frontend on the main domain and the backend on its
``api`` subdomain.

.. _user-accounts:

User accounts
-------------------------------------------------------------------------------

User accounts are created via the :ref:`web-frontend`.
Each user account must be approved by an existing user before it can log on
to the system.
Once user accounts are created and approved, they can be assigned roles
on Harvesters and Paths.

User roles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each :ref:`Harvester <harvesters>` requires at least one administrator, and may
have as many additional administrators as required.
Each Harvester administrator has the following rights:

* Edit Harvester details (name, sleep time)
* Appoint other users to administrator role
* Remove administrators (except the last administrator)
* Create new :ref:`monitored-paths`
* Perform any of the administrator actions for any of the Harvester's Paths

Harvesters have :ref:`monitored-paths` - directories which are monitored for data files.
Each Path may have any number of administrators and users.
The Path's Harvester administrators have the same rights as the Path's administrators.
Path administrators may:

* Edit Path details (path, stable time)
* Appoint other users to administrator and user roles
* Remove users from administrator and user roles
* Perform any of the Path user actions

Path users may:

* View and edit details of datafiles found in the Path directory
* View and edit datasets produced when those datafiles are imported

Additionally, any registered user may create, and view Cell and Equipment details.
They may also edit and delete those Cell and Equipment instances provided that no
datasets are using them.

REST API
-------------------------------------------------------------------------------

Endpoints are written as absolute paths starting from the Galvanalyser server
address, so to reach the ``/harvesters/`` endpoint for a Galvanalyser server
located at ``http://api.localhost``, you would go to ``http://api.localhost/harvesters/``.

API Spec
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The REST API provides a browsable interface at ``/spec/swagger-ui/``.
Its OpenAPI spec can be downloaded from ``/spec/``.
Spec download defaults to ``.yml`` format, but ``.json`` is available from ``/spec/?format=json``.

Static versions of this spec can be downloaded directly from this website:

* :download:`.yml format <resources/schema.yml>`
* :download:`.json format <resources/schema.json>`

Browsable API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The browsable API provided by Django REST Framework is not fully functional, 
but does provide a relatively useful way to browse the raw data on the REST API.
It is provided at the base address (endpoint ``/``), and provides its own list of
available endpoints.

.. _web-frontend:

Web frontend
==================================================================================

The primary tool for interacting with the REST API is the web frontend.
This is designed to provide a user-friendly way to view and edit :ref:`harvesters`,
:ref:`monitored-paths`, :ref:`datasets` and their metadata.

The web frontend is accessed via a :ref:`User account <user-accounts>`,
and allows new user accounts to be created and approved by existing users.
Each user's view of the web frontend is customised to only include information
relevant to them.

.. _datasets-page:

Datasets page
--------------------------------------------------------------------

When first successfully logging in with an (approved) account, the user will land
on the Datasets page.
This page lists information about any :ref:`datasets` that have been
imported from files in a :ref:`Monitored path <monitored-paths>` that the user
has access to. 

The first time you log in, this is likely to be blank. 
Once some datasets have been imported, you will see them listed here and
you will be able to edit their metadata.

Each dataset can be described in terms of its name and type, 
a purpose selected from a pre-populated list, and may be associated with 
the particular :ref:`Cell <cell-page>` that generated it, as well as any
:ref:`Equipment <equipment-page>` that was used.

Data view
--------------------------------------------------------------------

Clicking the magnifying glass icon for a dataset allows you to inspect the data.
This will bring up two buttons which provide boilerplate code for accessing the
data using the :ref:`python-client` or MATLAB, as well as a plot of
the voltage and ampage of the cell over the duration of the test.

Additional columns in the data can be added to the preview graph by clicking on their
names.

Harvesters page
--------------------------------------------------------------------

The Harvesters page lists :ref:`harvesters` that you have access to,
either because you are an administrator of that Harvester, or because you are
a user or administrator on one or more of the Harvester's :ref:`monitored-paths`.

If you are an administrator on the Harvester, you will be able to modify the
Harvester properties, changing the Harvester name or the sleep time. 
Sleep time governs how long the Harvester spends idle between harvest cycles.

There will be an additional section below the monitored paths section that
allows you to view or edit the harvester program's environment variables
according to your permissions.

Monitored paths view
--------------------------------------------------------------------

Click on the magnifying glass icon to view the selected Harvester's Paths.
The Path view shows the :ref:`monitored-paths` on the Harvester
that you can access. 
If you have sufficient permissions, you will be able to alter Path details,
including the directory path, the length of time files must be stable before 
attempting import, and user permissions.

File view
--------------------------------------------------------------------

Click on the magnifying glass icon to view the Files found in the Monitored path.
These are read-only because their properties are directly dependent on the actual
files in the monitored directory.
If any file has failed to import, the last error associated with that import will
appear when you mouse-over the IMPORT FAILED state. 

If for any reason you want to force the harvester to attempt to import a file
that has failed to import correctly, you can do so by clicking the refresh button
in the 'Force Re-import' column.

Files that have been successfully imported will show at least one linked :ref:`datasets`.
Once you have some, your initial :ref:`Dataset view <datasets-page>` will be populated
and you can add metadata to your dataset.

.. _cell-page:

Cell page
--------------------------------------------------------------------

Each dataset will be generated by a specific cell. 
The Cell page is where you can provide information about cells, which you can 
then link to their datasets in the :ref:`datasets-page`.

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

.. _equipment-page:

Equipment page
--------------------------------------------------------------------

Equipment can be defined on the equipment page. 
Equipment has a name and a type, and these can be edited for any equipment
that is not in use by a dataset.

.. _python-client:

Python client
--------------------------------------------------------------------

The best way to access the data is via the Python API client.
This provides read-only access to datasets and their metadata, 
and allows you to write reproducible analysis scripts that do not require local
storage to run their analyses.

You can download the latest Python API client :download:`here <resources/galvanalyser-client-python.zip>`.

.. _harvesters:

Harvesters
============================================

Harvesters are standalone programs that run continually in Docker containers.
Each Harvester has a set of directories called :ref:`monitored-paths`
that it watches for changes.
When files appear in those paths, the Harvester reports the size to the 
Galvanalyser server.
If the file size has been stable for long enough, the Harvester will attempt
to import the dataset, sending its metadata and parsed data to the Galvanalyser server.

At the beginning of each cycle, the Harvester checks in with the Galvanalyser
server and updates its configuration if it has been changed.

.. _monitored-paths:

Monitored paths
============================================

Monitored paths are directory paths relative to the Harvester container.
It is a good idea to use `Docker's volume mounting <https://docs.docker.com/storage/>`_
to provide easily reachable paths to the Harvester which can then be 
registered as Monitored paths.


.. _datasets:

Datasets
============================================

Files that are stable for long enough are parsed by the Harvester.
If the file is suitable for parsing, its metadata will be sent to the
Galvanalyser server and a Dataset will be constructed to house the data.

The file's data will then be extracted into Galvanalyser's column-value format
and sent to the server.
The column-value format means that column metadata is abstracted away,
allowing every column to be stored as a series of numbers.
Columns that contain strings generate an encoding map that is used to 
restore the values on demand. 
This method of storing data means that large quantities of data can be
stored in the database relatively rapidly.

Datasets' metadata can be edited in the web frontend's :ref:`datasets-page`,
and the data downloaded directly using the :ref:`python-client`.
