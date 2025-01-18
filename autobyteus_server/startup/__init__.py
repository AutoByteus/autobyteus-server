"""
Startup module handling all initialization tasks that need to run when the application starts.
This includes database migrations, cache warming, resource verification, etc.
"""

from .migrations import run_migrations

__all__ = ['run_migrations']
