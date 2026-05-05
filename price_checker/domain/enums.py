from enum import Enum


class RolesEnum(str, Enum):
    OPERADOR = "operador"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"

    @classmethod
    def get_hierarchy(cls) -> dict[str, list[str]]:
        """Retorna hierarquia de permissões."""
        return {
            cls.ADMIN.value: [cls.ADMIN.value, cls.SUPERVISOR.value, cls.OPERADOR.value],
            cls.SUPERVISOR.value: [cls.SUPERVISOR.value, cls.OPERADOR.value],
            cls.OPERADOR.value: [cls.OPERADOR.value],
        }
