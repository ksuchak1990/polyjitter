class PolyJitterError(Exception):
    """Base exception for all polyjitter errors."""


class InvalidInputError(PolyJitterError):
    """Raised when inputs are malformed or inconsistent."""


class CRSAlignmentError(PolyJitterError):
    """Raised when point and polygon CRS do not match."""


class GeometryError(PolyJitterError):
    """Raised when geometry operations fail unexpectedly."""
