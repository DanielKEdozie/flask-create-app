"""flask-create-app — Modern Flask project generator and scaffolding tool."""
from .cli import main
from .generator import scaffold_project

__all__ = ["main", "scaffold_project"]
__version__ = "1.0.0"