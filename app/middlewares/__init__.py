"""
Common middlewares.
"""

from app.middlewares.acl import ACLMiddleware
from app.middlewares.i18n import DatabaseI18nMiddleware

__all__ = ["ACLMiddleware", "DatabaseI18nMiddleware"]
