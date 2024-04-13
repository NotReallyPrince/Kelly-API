class BaseError(Exception):
    message = "An error occurred"

    def __init__(self, error=None):
        self.success = False
        self.error_message = error or self.message

    def __str__(self):
        return self.message


class TimeoutError(BaseError):
    message = "Internal Server Timeout, Please try again later"


class InvalidRequest(BaseError):
    message = "Invalid Request, Please read docs: https://api.princexd.tech/docs"


class InvalidContent(BaseError):
    message = "Invalid Content, Please report this: https://telegram.me/princexsupport"


class GenericApiError(BaseError):
    message = "Api Call Failed, Please report this: https://telegram.me/princexsupport"


class ConnectionError(BaseError):
    message = "Failed to communicate server, Please report this: https://telegram.me/princexsupport"


class InvalidApiKey(Exception):
    pass
