"""Base module for the project with version initialization."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version(__package__)
except PackageNotFoundError:
    # package is not installed
    pass
