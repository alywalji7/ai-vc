from .base import BaseIngestor
from .github import GitHubIngestor
from .crunchbase import CrunchbaseIngestor

__all__ = [
    "BaseIngestor", 
    "GitHubIngestor", 
    "CrunchbaseIngestor"
]