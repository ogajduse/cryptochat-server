"""Exception for the database errors"""
from tornado.web import HTTPError


class DatabaseError(HTTPError):
    """Raised in case of database error."""
