"""
Data cleansing and enrichment via Dadata API.
"""

from .sync import DadataClient as Dadata  # noqa
from .asynchr import DadataClient as DadataAsync  # noqa

__version__ = "21.10.1"
__all__ = []  # type: ignore
