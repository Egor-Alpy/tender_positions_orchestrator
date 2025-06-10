class OrchestratorException(Exception):
    """Базовое исключение оркестратора"""
    pass


class ServiceUnavailable(OrchestratorException):
    """Сервис недоступен"""
    pass


class ServiceError(OrchestratorException):
    """Ошибка при вызове сервиса"""
    pass


class ProcessingError(OrchestratorException):
    """Ошибка обработки тендера"""
    pass


class ConfigurationError(OrchestratorException):
    """Ошибка конфигурации"""
    pass