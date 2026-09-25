class AppException(Exception):
    """Excepcion base del dominio."""

    pass


class EntityNotFoundException(AppException):
    """Lanzada cuando un recurso no existe en la BD."""

    def __init__(self, entity_name: str, identifier: str | int) -> None:
        self.entity_name = entity_name
        self.identifier = identifier
        super().__init__(f"{entity_name} con id '{identifier}' no fue encontrado.")


class BusinessRuleViolationException(AppException):
    """Lanzada ante violaciones de reglas de negocio."""

    pass
