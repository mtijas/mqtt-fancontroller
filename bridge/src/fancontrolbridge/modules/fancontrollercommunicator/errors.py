class UnexpectedResponseError(Exception):
    """Unexpected response from Bridge"""

    pass


class ErrorResponseError(Exception):
    """Bridge responded with ERROR"""

    pass


class ResponseTimeoutError(Exception):
    """Bridge did not respond"""

    pass

class WriteTimeoutError(Exception):
    """Timeout while writing data to the Controller"""

    pass
