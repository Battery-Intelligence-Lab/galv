######################################################################################
First Time Quick Setup
######################################################################################

This section describes how to set up the system for the first time. 
It is assumed you are logged into the server machine that you 
wish to use, using the user account that you want to run the server with. 
The entire application has been dockerised, so can in theory be used on 
any major operating system with minimal modification.

**************************************************************************************
Installing required tools
**************************************************************************************

You need to have ``docker``, ``docker-compose`` and ``git`` installed and available on your
command-line. 

You can find installation instructions for ``docker`` on all major operating systems
`here <https://docs.docker.com/engine/install/>`_, and for ``docker-compose``
`here <https://docs.docker.com/compose/install/>`_. For linux hosts, it is useful to be
able to use ``docker`` as a non-root user, and you can find instructions on how to set
this up `here <https://docs.docker.com/engine/install/linux-postinstall/>`_. If you don't,
note that you will need to add ``sudo ...`` in front of every ``docker`` and
``docker-compose`` command listed below.

Installation instructions for ``git`` for all major OSs can be found
`here <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.


Get the galvanalyser source code
=======================================================================================

First you will need to clone the galvanalyser repository using ``git``:

.. code-block:: bash

	git clone https://gitlab.com/battery-intelligence-lab/galvanalyser-project/galvanalyser.git
	cd galvanalyser


Setup environment variables
=======================================================================================

The Galvanalyser project uses two ``.env`` files, ``.env`` and ``.env.secret``.

You will already have a ``.env`` file in the repository you cloned, with sensible defaults.

If you're running a **production deployment**, you will want to set the value of the
``VIRTUAL_HOST_ROOT`` to your domain name, e.g. ``VIRTUAL_HOST_ROOT=example.com``.
This will serve the Galvanalyser web application from the root of your domain,
e.g. at ``http://example.com/``; and the API from the subdomain, e.g. ``http://api.example.com``.
You will likely also want to enable HTTPS, for which we use LetsEncrypt to generate SSL certificates.
By default, the staging (test) server is used, which generates certificates that are not trusted by browsers.
When your production setup appears to work correctly, you can switch to fetching real certificates
by setting ``LETSENCRYPT_TEST=false`` and restarting the nginx-proxy container.

If you wish to change where the database is saved, you can change the first entry
in ``.env``, ``GALVANALYSER_DATA_PATH`` to the directory where you want the postgres database.

Create ``.env.secret``
=======================================================================================

The second ``.env`` file is a secrets file.
This is not included because you should come up with your own secret values for the
entries within it. 
Create the file and edit it so that it has the following keys:

* DJANGO_SECRET_KEY
* DJANGO_SUPERUSER_PASSWORD
* POSTGRES_PASSWORD

All of these values should be unguessable secure passwords. 
DJANGO_SECRET_KEY should be very long and complex, consider 60+ characters
with a mixture of special characters (avoid $), upper- and lower-case letters, 
and numbers.
The only one of these you will need to use again will be the superuser password.

If you would like the Django superuser to have a name that is not 'admin', 
you can also specify DJANGO_SUPERUSER_USERNAME.

.. code-block:: shell

	vi .env.secret  # could also use nano, emacs, etc.


Build docker images (only when upgrading to a new version of galvanalyser)
=======================================================================================

If you have previously installed and run galvanalyser you might already have old docker 
images already built. To rebuild the images, run the following command:

.. code-block:: bash

	docker-compose build

**************************************************************************************
Running Galvanalyser
**************************************************************************************

You can run the galvanalyser server and web application frontend using the following 
``docker-compose`` command from the root folder of the repository.

.. code-block:: bash

	docker-compose up

Now view the 'localhost' IP address `http://127.0.0.1/ <http://127.0.0.1/>`_ in your
browser and you should see the Galvanalyser login page. 
This is the web frontend.
If you wish to use the frontend from another machine, 
use the IP address or URL of the server instead.

Creating a user account
========================================================================================

It's not a good idea to do everything with the Django superuser, 
so create a new account on the login page. 
You'll see that you get a message telling you that the account 
needs to be approved by an existing account.

* Refresh the page, and login using the _superuser_ credentials.
* Once logged in, go to the bottom tab in the menu (Activate Users), and click the button next to your new user account
* Now, click the logout button in the top right, and log back in with your new user account

**************************************************************************************
Setting up a Harvester
**************************************************************************************

Harvesters are set up using a part of the code of the main Galvanalyser repository.
The first step, then, is to log onto the machine that will run the harvesters and 
clone the repository again.
If you are using the same server for the harvester and the rest of Galvanalyser, 
you can skip this step.

.. code-block:: bash

	git clone https://gitlab.com/battery-intelligence-lab/galvanalyser-project/galvanalyser.git
	cd galvanalyser


Next, launch the harvester container, specifying the Harvester's docker-compose configuration file:

.. code-block:: shell

	docker-compose -f docker-compose.harvester.yml run harvester


This will launch into an interactive shell which will guide you through the Harvester setup process.

First, you'll be asked for the Galvanalyser server URL.
If you're running on the same server as the Galvanalyser server, this will be ``http://app``,
otherwise it will be the path you entered above to connect to the web frontend, 
but using the ``api`` subdomain. So if you went to ``http://example.com``, go to ``http://api.example.com``.

Next, you'll be asked to specify a name for the new Harvester. 

Each Harvester needs at least one administrator.
You'll be given a list of active user accounts, and will select one to be the 
Harvester administrator. 
If you're following this guide, you'll see the Django superuser account and the
regular user account you just created.
Select the regular user account.
You can add other administrators and users to the Harvester using the web frontend later.

When an administrator has been selected the Harvester will register itself with
the Galvanalyser server and begin to monitor for data files. 
Of course, it currently has no directories to monitor, so the last step is to
go to the web frontend and configure at least one monitored path for the Harvester.

Open up the web frontend in a browser, log in as the Harvester administrator user,
and select the 'Harvesters' tab.
Click on the magnifying glass icon to see details for your new Harvester.
Enter a path for the Harvester to monitor (relative to the Harvester's system), 
and click the plus icon to save your new path.

The Harvester will now crawl the directory, observing files and importing them
when they have been stable for a sufficiently long time.

**************************************************************************************
Maintenance
**************************************************************************************

To run the server in detached mode (i.e. run containers in the background) using the 
``-d`` option

.. code-block:: bash

	docker-compose up -d


To start the server side system again after it has been stopped simply run 
``docker-compose up`` in the root folder.

A template SystemD service file is included in the repository root directory 
``galvanalyser.service`` that can be used to automatically start the system on Linux servers.


If Harvesters go down, they can be restarted by overriding the launch command:
.. code-block:: shell

	docker-compose -f docker-compose.harvester.yml run --entrypoint "python start.py --restart" harvester

