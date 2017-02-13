""" List of Stepmania exceptions """

from smserver import logger

mlog = logger.get_logger()

class StepmaniaUserException(Exception):
    """ Base exception which contains all informations for sending out errors """

    status_code = None

    def __init__(self, token, message, status_code=None, details=""):
        super().__init__(self, message)

        self.token = token
        self.message = message
        if self.status_code:
            self.status_code = status_code

        mlog.info("[%s] %s: %s (%s)", self.status_code, token, message, details)


class Unauthorized(StepmaniaUserException):
    """ Exception for unauthorized query """

    status_code = 401
    message = "Unauthorized"

    def __init__(self, token, details):
        super().__init__(self, token, self.message, details=details)


class Forbidden(StepmaniaUserException):
    """ Exception for unauthorized queries """

    status_code = 403
    message = "Foridden"

    def __init__(self, token, details):
        super().__init__(self, token, self.message, details=details)

class ValidationError(StepmaniaUserException):
    """ Exception for resource validation error """

    status_code = 400
    message = "Validation error"

    def __init__(self, token, details):
        super().__init__(self, token, self.message, details=details)

class NotFound(StepmaniaUserException):
    """ Exception for not found queries """

    status_code = 404
    message = "Not Found"

    def __init__(self, token, details):
        super().__init__(self, token, self.message, details=details)
