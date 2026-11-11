
class PubMedTimeOutError(Exception):
    """Raised when an HTTP request times out"""

class PubMedTransportError(Exception):
    """Raised when the HTTP transport fails"""

class PubMedHTTPError(Exception):
    """Raised when an PubMed returns an unseccessfull HTTP response"""
