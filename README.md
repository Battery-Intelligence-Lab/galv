<img src="docs/source/img/Galv-logo-shortened.png" width="225" />

[![Unit Tests (Docker)](https://github.com/Battery-Intelligence-Lab/galv/actions/workflows/unit-test.yml/badge.svg?branch=main)](https://github.com/Battery-Intelligence-Lab/galv/actions/workflows/unit-test.yml)
[![Docs](https://github.com/Battery-Intelligence-Lab/galv/actions/workflows/side-effects.yml/badge.svg?branch=main)](https://battery-intelligence-lab.github.io/galv/index.html)
<a href="https://Battery-Intelligence-Lab.github.io/galv/" target="_blank">
    [![Docs website](https://github.com/Battery-Intelligence-Lab/galv/actions/workflows/pages/pages-build-deployment/badge.svg?branch=gh-pages)](https://github.com/Battery-Intelligence-Lab/galv/actions/workflows/pages/pages-build-deployment)
</a>

Galv is an open-source platform for automated storage of battery cycler data with advanced metadata support for battery scientists. Galv is deployed with [docker](https://docs.docker.com/) to support robust local and cloud instances.

## Features:
- REST API for easy data storage and retrieval
- A Python, Julia, and MATLAB client for the REST API
- Metadata support using ontology definitions from BattINFO/EMMO
- A distributed platform with local data harvesters
- Docker based deployment

## Getting Started
A laboratory running a [Galv server](https://Battery-Intelligence-Lab.github.io/galv/UserGuide.html#galv-server) instance and a battery cycling machines can use Galv to make it easy to access, analyse, and share their experimental data. To do this, they:
1. Set the cycling machines up to output their raw test result files to a shared drive. 
2. Set up a [harvester](https://Battery-Intelligence-Lab.github.io/galv/UserGuide.html#harvesters) on a computer with access to that shared drive.
    - (This only needs to be done once)
3. Log into their lab [Web frontend](https://Battery-Intelligence-Lab.github.io/galv/UserGuide.html#web-frontend) and configure the
    [harvester](https://Battery-Intelligence-Lab.github.io/galv/UserGuide.html#harvesters) to crawl the appropriate directories on the shared drive.
4. Log into the [Web frontend](https://Battery-Intelligence-Lab.github.io/galv/UserGuide.html#web-frontend) to edit metadata and view data,
    or use the [Python client](https://Battery-Intelligence-Lab.github.io/galv/UserGuide.html#python-client) to download formatted data for analysis.

The harvesters are able to parse the following file types:

- MACCOR files in ``.txt``, ``.xsl``/``.xslx``, or ``raw`` format
- Ivium files in ``.idf`` format
- Biologic files in ``.mpr`` format (EC-Lab firmware < 11.50)

The server database is a relational database that stores each dataset along with information about column types, units, and other relevant metadata (e.g. cell information, owner, purpose of the experiment).
The [REST API](https://Battery-Intelligence-Lab.github.io/galv/UserGuide.html#rest-api) provides its own definition via a downloadable OpenAPI schema file 
(`schema/`), and provides interactive documentation via SwaggerUI (`schema/swagger-ui/`) and Redoc (`schema/redoc/`).

The schema can be downloaded from the [documentation page](https://Battery-Intelligence-Lab.github.io/galv/UserGuide.html#api-spec).

A diagram of the logical structure of the system is shown below. The arrows indicate the 
direction of data flow.

<p align="center">
    <img src="docs/source/img/GalvStructure.PNG" alt="Data flows from battery cycling machines to Galv Harvesters, then to the     Galv server and REST API. Metadata can be updated and data read using the web client, and data can be downloaded by the Python client." width="600" />
</p>


## Project documentation

Full documentation is available [here](https://Battery-Intelligence-Lab.github.io/galv/), build by Sphinx from `./docs/source/*.rst`.
