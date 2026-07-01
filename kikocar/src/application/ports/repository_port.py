from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities import (
    Maquina,
    Mantenimiento,
    Operador,
    OrdenServicio,
    ReporteDiario,
)


class MaquinaRepositoryPort(ABC):
    @abstractmethod
    async def listar_todas(self) -> List[Maquina]: ...

    @abstractmethod
    async def obtener_por_id(self, maquina_id: UUID) -> Optional[Maquina]: ...

    @abstractmethod
    async def actualizar_horometro(self, maquina_id: UUID, nuevo_horometro: float) -> None: ...

    @abstractmethod
    async def registrar_mantenimiento(self, maquina_id: UUID, nuevo_ultimo_mant: float, notas: Optional[str] = None) -> None: ...

    @abstractmethod
    async def actualizar_estado(self, maquina_id: UUID, nuevo_estado: str) -> None: ...


class OperadorRepositoryPort(ABC):
    @abstractmethod
    async def listar_todos(self) -> List[Operador]: ...

    @abstractmethod
    async def obtener_por_id(self, operador_id: UUID) -> Optional[Operador]: ...


class OrdenRepositoryPort(ABC):
    @abstractmethod
    async def crear(self, orden: OrdenServicio) -> OrdenServicio: ...

    @abstractmethod
    async def obtener_por_operador(self, operador_id: UUID) -> Optional[OrdenServicio]: ...

    @abstractmethod
    async def listar_activas(self) -> List[OrdenServicio]: ...

    @abstractmethod
    async def obtener_por_id(self, orden_id: UUID) -> Optional[OrdenServicio]: ...

    @abstractmethod
    async def obtener_activa_por_maquina(self, maquina_id: UUID) -> Optional[OrdenServicio]: ...

    @abstractmethod
    async def obtener_todas(self) -> List[OrdenServicio]: ...

    @abstractmethod
    async def actualizar_estado_orden(self, orden_id: UUID, nuevo_estado: str) -> None: ...


class ReporteRepositoryPort(ABC):
    @abstractmethod
    async def crear(self, reporte: ReporteDiario) -> ReporteDiario: ...

    @abstractmethod
    async def listar_por_orden(self, orden_id: UUID) -> List[ReporteDiario]: ...

    @abstractmethod
    async def listar_con_alerta(self) -> List[ReporteDiario]: ...

    @abstractmethod
    async def listar_con_atencion(self) -> List[ReporteDiario]: ...

    @abstractmethod
    async def obtener_todos(self) -> List[ReporteDiario]: ...

    @abstractmethod
    async def resumen_por_orden(self, orden_id: UUID) -> dict: ...

    @abstractmethod
    async def obtener_ultimo_reporte_por_orden(self, orden_id: UUID) -> Optional[ReporteDiario]: ...

    @abstractmethod
    async def obtener_valorizacion(self) -> list: ...

    @abstractmethod
    async def eliminar(self, reporte_id: UUID) -> bool: ...


class MantenimientoRepositoryPort(ABC):
    @abstractmethod
    async def crear(self, mantenimiento: Mantenimiento) -> Mantenimiento: ...

    @abstractmethod
    async def listar_por_maquina(self, maquina_id: UUID) -> List[Mantenimiento]: ...

    @abstractmethod
    async def listar_todos(self) -> List[Mantenimiento]: ...


class DashboardAnalyticsPort(ABC):
    @abstractmethod
    async def total_facturado(self) -> float: ...

    @abstractmethod
    async def total_horas_trabajadas(self) -> float: ...

    @abstractmethod
    async def resumen_flota(self) -> dict: ...

    @abstractmethod
    async def flota_completa(self) -> list: ...
