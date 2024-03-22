# Signifies our desired python version
# Makefile macros (or variables) are defined a little bit differently than traditional bash, keep in mind that in the Makefile there's top-level Makefile-only syntax, and everything else is bash script syntax.
PYTHON = python
SHELL = /bin/bash

# .PHONY defines parts of the makefile that are not dependant on any specific file
# This is most often used to store functions
.PHONY = help

folders := travelagent tests
files := $(shell find . -name "*.py" -not -path "./venv/*")
doc_files := $(shell find sphinx -name "*.*")

# Uncomment to store cache installation in the environment
# cache_dir := $(shell python -c 'import site; print(site.getsitepackages()[0])')
cache_dir := .make_cache
package_name=$(shell python -c "import tomli;from pathlib import Path;print(tomli.loads(Path('pyproject.toml').read_text(encoding='utf-8'))['project']['name'])")

$(shell mkdir -p $(cache_dir))

pre_deps_tag := $(cache_dir)/.pre_deps
env_tag := $(cache_dir)/.env_tag
env_dev_tag := $(cache_dir)/.env_dev_tag
install_tag := $(cache_dir)/.install_tag
docker_build_tag := $(cache_dir)/.docker_build_tag
project_name := travelagent
registry := eu.gcr.io
image_name := $(registry)/aramix-team/$(project_name)

# ======================
# Rules and Dependencies
# ======================

help:
	@echo "---------------HELP-----------------"
	@echo "Package Name: $(package_name)"
	@echo " "
	@echo "Type 'make' followed by one of these keywords:"
	@echo " "
	@echo "  - reqs to compile closed package requirements from open ones in requirements/requirements.in"
	@echo "  - reqs_dev to compile closed development requirements from open ones in requiremetts/requirements_dev.in"
	@echo "  - setup to install package requirements"
	@echo "  - setup_dev to install development requirements"
	@echo "  - dist to build a tar.gz distribution"
	@echo "  - install to install the package"
	@echo "  - install_dev to install the package with development environment"
	@echo "  - uninstall to uninstall the environment"
	@echo "  - format to format code as configured in pyproject.toml"
	@echo "  - check_format to check formatting"
	@echo "  - tests to run unittests as configured in pyproject.toml"
	@echo "  - lint to check linting as configured in pyproject.toml"
	@echo "  - mypy to perform static type checking as configured in pyproject.toml"
	@echo "  - bandit to find security issues in app code using bandit as configured in pyproject.toml"
	@echo "  - licensecheck to check dependencies licences compatibility with application license using licensecheck as configured in pyproject.toml"
	@echo "  - docs to produce documentation in html format as configured in pyproject.toml"
	@echo "  - checks to run format, mypy, lint, bandit, licensecheck and tests altogether"
	@echo "  - clean to remove cache files"
	@echo "  - publish_test to publish package on TestPyPI"
	@echo "  - publish to publish package on PyPI"
	@echo "------------------------------------"


$(pre_deps_tag):
	@echo "==Installing pip-tools and black=="
	${PYTHON} -m pip install --upgrade --quiet pip
	${PYTHON} -m pip install --upgrade --quiet tomli setuptools
	grep "^pip-tools\|^black\|^pre-commit"  requirements/requirements_dev.in | xargs ${PYTHON} -m pip install --quiet
	if [[ -d ../.git ]] && [[ ! -s ../.git/hooks/pre-commit ]]; then pre-commit install; fi;
	touch $(pre_deps_tag)


requirements/requirements_dev.txt: requirements/requirements_dev.in requirements/requirements.in $(pre_deps_tag)
	@echo "==Compiling requirements_dev.txt=="
	pip-compile --output-file requirements/tmp.txt --quiet --no-emit-index-url --resolver=backtracking  pyproject.toml --all-extras  --no-strip-extras
	cat requirements/tmp.txt > requirements/requirements_dev.txt
	rm requirements/tmp.txt

reqs_dev: requirements/requirements_dev.txt

requirements/requirements.txt: requirements/requirements_dev.txt
	@echo "==Compiling requirements.txt=="
	cat requirements/requirements.in > subset.in
	echo "" >> subset.in
	echo " -c requirements/requirements_dev.txt" >> subset.in
	pip-compile --output-file "requirements/tmp.txt" --quiet --no-emit-index-url --resolver=backtracking --no-strip-extras subset.in
	rm subset.in
	cat requirements/tmp.txt > requirements/requirements.txt
	rm requirements/tmp.txt

reqs: requirements/requirements.txt

$(env_tag): requirements/requirements.txt
	@echo "==Installing requirements.txt=="
	pip-sync --quiet requirements/requirements.txt
	rm -f $(env_dev_tag)
	rm -f $(install_tag)
	touch $(env_tag)

$(env_dev_tag): requirements/requirements_dev.txt
	@echo "==Installing requirements_dev.txt=="
	pip-sync --quiet requirements/requirements_dev.txt
	rm -f $(env_tag)
	rm -f $(install_tag)
	touch $(env_dev_tag)

setup: $(env_tag)

setup_dev: $(env_dev_tag)

dist/.build-tag: $(files) pyproject.toml requirements/requirements.txt
	@echo "==Building package distribution=="
	${PYTHON} -m build --sdist . > /dev/null
	ls -rt  dist/* | tail -1 > dist/.build-tag

dist: dist/.build-tag pyproject.toml

$(install_tag): dist/.build-tag
	@echo "==Installing package=="
	${PYTHON} -m pip install --quiet $(shell ls -rt  dist/*.tar.gz | tail -1)
	touch $(install_tag)

uninstall:
	@echo "==Uninstall all packages=="
	pip-sync --quiet /dev/null
	${PYTHON} -m pip freeze | xargs pip uninstall -y --quiet
	@echo "==Removing all tags=="
	rm -f $(env_tag) $(env_dev_tag) $(pre_deps_tag) $(install_tag)

install: setup $(install_tag)

install_dev: setup_dev $(install_tag)

format: setup_dev
	${PYTHON} -m black $(folders)
	${PYTHON} -m isort $(folders)

check_format: setup_dev
	${PYTHON} -m black --check $(folders)
	${PYTHON} -m isort $(folders) -c

lint: setup_dev
	${PYTHON} -m flake8 $(folders)

mypy: setup_dev
	${PYTHON} -m mypy --install-types --non-interactive

tests: setup_dev
	${PYTHON} -m pytest

bandit: setup_dev
	${PYTHON} -m bandit -r -c pyproject.toml --severity-level high --confidence-level high .

licensecheck: setup_dev requirements/requirements.txt
	${PYTHON} -m licensecheck

checks: check_format lint mypy bandit licensecheck tests

docs: install_dev $(doc_files) pyproject.toml
	sphinx-apidoc --implicit-namespaces -f -d 20 -M -e -o sphinx/source/api travelagent
	make --directory=sphinx --file=Makefile clean html

clean: uninstall
	@echo "==Cleaning environment=="
	pip cache purge
	rm -rf docs
	rm -rf build
	rm -rf sphinx/source/api
	rm -rf $(shell find . -name "*.pyc" -not -path "./venv/*") $(shell find . -name "__pycache__" -not -path "./venv/*")
	rm -rf dist *.egg-info .mypy_cache .pytest_cache .make_cache $(env_tag) $(env_dev_tag) $(install_tag)

tag: install
	git fetch --tags origin; \
	VERSION=$$(${PYTHON} -c "from importlib.metadata import version;print(version('${project_name}'))"); \
	TAGS=$$(git tag); \
	if [[ " $${TAGS} " =~ " v$${VERSION} " ]]; then \
		echo "==Tag v$${VERSION} already exists, nothing to do=="; \
		exit 1; \
	elif [[ $${VERSION} =~ .*\.d[0-9]{8}$$ ]]; then \
		echo "==Version $${VERSION} is dirty, not creating tag =="; \
		exit 1; \
	else \
		echo "==Version $${VERSION} is fine, creating tag=="; \
		git tag -a "v$${VERSION}" -m "Version $${VERSION}"; git push origin "v$${VERSION}"; \
	fi
