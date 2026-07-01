from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class Operador(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    dni: str
    nombre: str
    apellido: str
    licencia: str
    estado: str = "DISPONIBLE"

    class Config:
        from_attributes = True

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


class Maquina(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    codigo_interno: str
    marca: str
    modelo: str
    tipo: str
    capacidad_ton: int = 0
    consumo_teorico_gh: Decimal
    horometro_actual: Decimal = Decimal("0")
    ultimo_mant_horas: Decimal = Decimal("0")
    intervalo_mant_horas: Decimal = Decimal("250")
    estado_operativo: str = "OPERATIVA"
    ubicacion: str = ""
    notas_mantenimiento: Optional[str] = None

    class Config:
        from_attributes = True

    @property
    def nombre_completo(self) -> str:
        return f"{self.marca} {self.modelo} ({self.codigo_interno})"

    @property
    def horas_desde_ultimo_mant(self) -> float:
        return max(float(self.horometro_actual - self.ultimo_mant_horas), 0)

    @property
    def horas_restantes_mant(self) -> float:
        return max(float(self.intervalo_mant_horas) - self.horas_desde_ultimo_mant, 0)


class FrenteObra(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    nombre: str
    ubicacion: str
    cliente: str

    class Config:
        from_attributes = True


class OrdenServicio(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    numero_orden: str
    cliente: str
    descripcion: Optional[str] = None
    monto: Decimal = Decimal("0")
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    horas_estimadas: Decimal = Decimal("240")
    horometro_ingreso: Optional[Decimal] = None
    frente_id: Optional[UUID] = None
    maquina_id: UUID
    operador_id: UUID
    estado: str = "ACTIVA"

    class Config:
        from_attributes = True


class ReporteDiario(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    orden_id: UUID
    fecha: date = Field(default_factory=date.today)
    horometro_inicio: Decimal
    horometro_fin: Decimal
    horas_trabajadas: Decimal = Decimal("0")
    galones_inicial: Decimal = Decimal("0")
    galones_final: Decimal = Decimal("0")
    descripcion: Optional[str] = None
    fallas_reportadas: Optional[str] = None
    requiere_atencion: bool = False
    alerta_robo: bool = False
    probabilidad_fallo: Decimal = Decimal("0")
    dias_restantes_mant: int = 0

    class Config:
        from_attributes = True

    @property
    def galones_consumidos(self) -> Decimal:
        return max(self.galones_inicial - self.galones_final, Decimal("0"))


class Mantenimiento(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    maquina_id: UUID
    orden_id: Optional[UUID] = None
    fecha: date = Field(default_factory=date.today)
    horometro_actual: Decimal
    tipo: str = "PREVENTIVO"
    descripcion: Optional[str] = None
    costo: Decimal = Decimal("0")

    class Config:
        from_attributes = True
