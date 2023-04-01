"""Get the version of the package."""
from importlib import metadata

try:
    __version__ = metadata.version("kor")
except metadata.PackageNotFoundError:
    __version__ = "local"
