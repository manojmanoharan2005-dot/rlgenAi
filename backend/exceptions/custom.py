class BaseAppException(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ApplicationException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, code="APP_ERROR")

class ValidationException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")

class ConfigurationException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, code="CONFIG_ERROR")

class ExternalServiceException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, code="EXTERNAL_SERVICE_ERROR")
