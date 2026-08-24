"""
Custom exception classes for MedVision AI.
Provides specific exception types for different error scenarios.
"""


class MedVisionException(Exception):
    """Base exception for all MedVision errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(MedVisionException):
    """Raised when authentication fails (401)."""
    pass


class AuthorizationError(MedVisionException):
    """Raised when user lacks permissions (403)."""
    pass


class ResourceNotFoundError(MedVisionException):
    """Raised when a requested resource doesn't exist (404)."""
    def __init__(self, resource: str = "Resource", identifier=None):
        if identifier is not None:
            message = f"{resource} with id '{identifier}' not found"
        else:
            message = f"{resource} not found"
        super().__init__(message)


# Alias for backward compatibility and semantic clarity
UserNotFoundError = ResourceNotFoundError


class DuplicateResourceError(MedVisionException):
    """Raised when attempting to create a duplicate resource (409)."""
    def __init__(self, resource: str = "Resource", field: str = "field", value: str = ""):
        message = f"{resource} with {field} '{value}' already exists"
        super().__init__(message)


class ValidationError(MedVisionException):
    """Raised when input validation fails (422)."""
    pass


class InactiveUserError(MedVisionException):
    """Raised when user account is inactive (403)."""
    def __init__(self, message: str = "User account is inactive"):
        super().__init__(message)
