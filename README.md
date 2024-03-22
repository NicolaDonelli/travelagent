# TravelAgent  

This project contains the python package known as "travelagent" and requires Python 3.10.

### Clone the application
Clone the code directly from the repository:
```
git clone  https://github.com/NicolaDonelli/travelagent.git
cd "$(basename " https://github.com/NicolaDonelli/travelagent.git" .git)"
```

### Prerequisites


## Repository structure
After initialization repository is structured according to the following schema
```
PROJECT_DIR
│   README.md
│   Dockerfile      ==>  list of docker instructions to build imge
│   Makefile        ==>  list of make commands
│   LICENSE         ==>  project license
│   pyproject.toml  ==>  project configurations
│   .giattributes   ==>  file that gives attributes to pathnames
│   .gitignore      ==>  list of patterns to ignore with git
│   .dockerignore   ==>  list of patterns to ignore while building docker image
│
└───travelagent
    └───adapters
    └───api
    └───logic
    └───ms
│   │   __init__.py  ==> file containing version number
│   │   py.typed     ==> empty file required by mypy to recognize a typed package
│   
└───bin ==> folder that will contain executable files
│   
└───requirements
│   │   requirements.in  ==> application's open requirements
│   │   requirements.txt  ==> application's closed requirements, as built by make reqs
│   │   requirements_dev.in  ==> development environment's open requirements
│   │   requirements_dev.txt  ==> development environment's open requirements, as built by make reqs_dev
│   
└───sphinx ==> sphinx documentation folder containig varius files that will be used to compile code documentations
│   │   ... 
│   
└───tests ==> unit-tests module
    │   __init__.py
```


## Tools for the project

### GNU Make
This project uses [GNU make](https://www.gnu.org/software/make/) to orchestrate of some complex common actions. 
In particular the processes of compiling and installing requirements, running checks (static typing, linting, unittests, etc), 
compiling documentation, building a docker image and running it are streamlined within the Makefile and can be run using 
simple make commands.
To get a complete list of available make commands the user can simply type `make help` but the most relevant are:
* ``make setup``, to setup the minimal environment required for the application
* ``make setup_dev``, to setup the full development environment (i.e. including dependencies required for quality checks)
* ``make install``, to install the package with minimal requirements
* ``make install_dev``, to install the package with development requirements
* ``make checks``, to check formatting, linting, static typing and running unit-tests
* ``make docs``, to build and compile html documentation using sphinx

### Requirements tracking
This project uses ``pip-tools`` to keep track of requirements. In particular there is a ``requirements`` folder 
containing a ``requirements.in, requirements.txt, requirements_dev.in, requirements_dev.txt`` files corresponding to 
input (``*.in``) and actual (``*.txt``) requirements files for dev and prod environments.


### Code formatting
This project uses [`black`](https://black.readthedocs.io/en/stable/) for formatting and enforcing a coding style and 
[`isort`](https://pycqa.github.io/isort/) for automatically sorting imports. 
Their configurations are included in `pyproject.toml` configuration file.
Run ``make format`` to reformat all source code and tests files according to `black` and `isort` standards.

### Linting
This project uses [`flake8`](https://flake8.pycqa.org/en/latest/) for coding style checking. 
Its configurations are included in `pyproject.toml` configuration file. 
It coincides with the configuration suggested by the `black` developers. 
Run `make lint` to analyse all source code and tests files.

### Type hints
This project uses [`mypy`](http://mypy-lang.org/) for static type checking. Its configuration is included in `pyproject.toml`.
The only settings included in this configuration files are related to the missing typing annotations of some common third party libraries.

### Security checks
This project uses [`bandit`](https://bandit.readthedocs.io/en/latest//) for security checks. Its configuration is included in `pyproject.toml`.
It is currently set to check for issues of high severity and with high confidence.

### License compatibility checks
This project uses [`licensecheck`](https://github.com/FHPythonUtils/LicenseCheck) to check compatibility between the license of this package and the ones of its depencencies. Its configuration is included in `pyproject.toml`.
It is currently set to ignore dependency issues between locally-developed packages.

### Secret detection
This project uses [`detect-secrets`](https://github.com/Yelp/detect-secrets) to automatically search for tracked secrets. 
This check is run automatically before each commit using pre-commit hooks installed with [`pre-commit`](https://github.com/pre-commit/pre-commit) 
and configured in `.pre-commit-config.yaml`.

### Documentation
This project uses [`Sphinx`](https://www.sphinx-doc.org/en/master/) as a tool to create documentation. 
Run `make docs` to automatically build documentation.
There is a Github workflow setup to publish documentation on the repo's Github Page at every push on `main` branch. 
To let this action run smoothly there must exist the `gh_pages`branch and the Github Page must be manually setted (from
github repo web interface > Settings > Pages) to use `gh_pages` as source branch and `/root` as source folder. 
Since this action requires a GITHUB_TOKEN, for its first run in the repo it will be necessary to follow the steps 
detailed [here]( https://github.com/peaceiris/actions-gh-pages#%EF%B8%8F-first-deployment-with-github_token) 
to make the action run fine from then on.

### Semantic Versioning
This project automatically applies semantic versioning based on tags following PEP440 using [`setuptools_scm`](https://github.com/pypa/setuptools_scm).
The configuration is included in ``pyproject.toml``.  

## Continuous Integration and Continuous Delivery
CI/CD workflows are performed with CircleCI workflows as defined in _.circleci/config.yaml_.
The defined jobs are:
* ``check``, that runs ``make checks`` on checked-out code in a python container using ENV and PROJECT_DIR environment variables
* ``build-test-push-deploy-container``, that enables the connection to the Google Cloud Platform's project used to deploy, 
builds the Docker image, performs sanity checks on it, pushes it to the artifact registry and finally deploys it on the 
given cloud run. This job depends on the ENV and PROJECT_DIR environment variables defined as job's parameters.

### CI workflow
This workflow is activated only by commits on an open Pull Request and checks the application using the ``check`` job.
 
### CD workflow
This workflow is activated only by pushing version tags and performs the ``check`` and the ``build-test-push-deploy-container`` jobs.
Depending on the structure of the pushed tag it preforms the ``build-test-push-deploy-container`` job with ENV=prod 
if the tag is clean or with ENV=test either way.
