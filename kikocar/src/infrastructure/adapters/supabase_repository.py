import os
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from dotenv import load_dotenv
from supabase import Client, create_client

from src.application.ports.repository_port import (
    DashboardAnalyticsPort,
    MantenimientoRepositoryPort,
    MaquinaRepositoryPort,
    OperadorRepositoryPort,
    OrdenRepositoryPort,
    ReporteRepositoryPort,
)
from src.domain.entities import (
    Maquina,
    Mantenimiento,
    Operador,
    OrdenServicio,
    ReporteDiario,
)

load_dotenv()


class SupabaseClientFactory:
    _client: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            url = os.environ["SUPABASE_URL"]
            key = os.environ["SUPABASE_KEY"]
            cls._client = create_client(url, key)
        return cls._client


def _map_maquina(row: dict) -> Maquina:
    return Maquina(
        id=UUID(row["id"]),
        codigo_interno=row["codigo_interno"],
        marca=row["marca"],
        modelo=row["modelo"],
        tipo=row["tipo"],
        capacidad_ton=int(row.get("capacidad_ton", 0)),
        consumo_teorico_gh=Decimal(str(row["consumo_teorico_gh"])),
        horometro_actual=Decimal(str(row["horometro_actual"])),
        ultimo_mant_horas=Decimal(str(row["ultimo_mant_horas"])),
        intervalo_mant_horas=Decimal(str(row["intervalo_mant_horas"])),
        estado_operativo=row["estado_operativo"],
        ubicacion=row.get("ubicacion", ""),
        notas_mantenimiento=row.get("notas_mantenimiento", ""),
    )


def _map_operador(row: dict) -> Operador:
    return Operador(
        id=UUID(row["id"]),
        dni=row["dni"],
        nombre=row["nombre"],
        apellido=row["apellido"],
        licencia=row["licencia"],
        estado=row["estado"],
    )


def _map_orden(row: dict) -> OrdenServicio:
    return OrdenServicio(
        id=UUID(row["id"]),
        numero_orden=row["numero_orden"],
        cliente=row["cliente"],
        descripcion=row.get("descripcion"),
        monto=Decimal(str(row["monto"])),
        fecha_inicio=row["fecha_inicio"],
        fecha_fin=row.get("fecha_fin"),
        horas_estimadas=Decimal(str(row.get("horas_estimadas", 240))),
        horometro_ingreso=Decimal(str(row["horometro_ingreso"])) if row.get("horometro_ingreso") else None,
        frente_id=UUID(row["frente_id"]) if row.get("frente_id") else None,
        maquina_id=UUID(row["maquina_id"]),
        operador_id=UUID(row["operador_id"]),
        estado=row["estado"],
    )


def _map_reporte(row: dict) -> ReporteDiario:
    return ReporteDiario(
        id=UUID(row["id"]),
        orden_id=UUID(row["orden_id"]),
        fecha=row["fecha"],
        horometro_inicio=Decimal(str(row["horometro_inicio"])),
        horometro_fin=Decimal(str(row["horometro_fin"])),
        horas_trabajadas=Decimal(str(row["horas_trabajadas"])),
        galones_inicial=Decimal(str(row.get("galones_inicial", 0))),
        galones_final=Decimal(str(row.get("galones_final", 0))),
        descripcion=row.get("descripcion"),
        fallas_reportadas=row.get("fallas_reportadas"),
        requiere_atencion=row.get("requiere_atencion", False),
        alerta_robo=row["alerta_robo"],
        probabilidad_fallo=Decimal(str(row["probabilidad_fallo"])),
        dias_restantes_mant=row["dias_restantes_mant"],
    )


def _map_mantenimiento(row: dict) -> Mantenimiento:
    return Mantenimiento(
        id=UUID(row["id"]),
        maquina_id=UUID(row["maquina_id"]),
        orden_id=UUID(row["orden_id"]) if row.get("orden_id") else None,
        fecha=row["fecha"],
        horometro_actual=Decimal(str(row["horometro_actual"])),
        tipo=row["tipo"],
        descripcion=row.get("descripcion"),
        costo=Decimal(str(row.get("costo", 0))),
    )


class SupabaseMaquinaRepository(MaquinaRepositoryPort):
    def __init__(self) -> None:
        self.client = SupabaseClientFactory.get_client()

    async def listar_todas(self) -> List[Maquina]:
        resp = self.client.table("maquinaria").select("*").order("codigo_interno").execute()
        return [_map_maquina(r) for r in resp.data]

    async def obtener_por_id(self, maquina_id: UUID) -> Optional[Maquina]:
        resp = self.client.table("maquinaria").select("*").eq("id", str(maquina_id)).execute()
        if resp.data:
            return _map_maquina(resp.data[0])
        return None

    async def actualizar_horometro(self, maquina_id: UUID, nuevo_horometro: float) -> None:
        self.client.table("maquinaria").update({"horometro_actual": nuevo_horometro}).eq(
            "id", str(maquina_id)
        ).execute()

    async def actualizar_estado(self, maquina_id: UUID, nuevo_estado: str) -> None:
        self.client.table("maquinaria").update({"estado_operativo": nuevo_estado}).eq(
            "id", str(maquina_id)
        ).execute()

    async def registrar_mantenimiento(self, maquina_id: UUID, nuevo_ultimo_mant: float, notas: Optional[str] = None) -> None:
        update = {"ultimo_mant_horas": nuevo_ultimo_mant, "estado_operativo": "OPERATIVA"}
        if notas:
            update["notas_mantenimiento"] = notas
        self.client.table("maquinaria").update(update).eq(
            "id", str(maquina_id)
        ).execute()


class SupabaseOperadorRepository(OperadorRepositoryPort):
    def __init__(self) -> None:
        self.client = SupabaseClientFactory.get_client()

    async def listar_todos(self) -> List[Operador]:
        resp = self.client.table("operadores").select("*").order("apellido").execute()
        return [_map_operador(r) for r in resp.data]

    async def obtener_por_id(self, operador_id: UUID) -> Optional[Operador]:
        resp = self.client.table("operadores").select("*").eq("id", str(operador_id)).execute()
        if resp.data:
            return _map_operador(resp.data[0])
        return None


class SupabaseOrdenRepository(OrdenRepositoryPort):
    def __init__(self) -> None:
        self.client = SupabaseClientFactory.get_client()

    async def crear(self, orden: OrdenServicio) -> OrdenServicio:
        payload = {
            "numero_orden": orden.numero_orden,
            "cliente": orden.cliente,
            "descripcion": orden.descripcion,
            "monto": float(orden.monto),
            "fecha_inicio": orden.fecha_inicio.isoformat(),
            "fecha_fin": orden.fecha_fin.isoformat() if orden.fecha_fin else None,
            "horas_estimadas": float(orden.horas_estimadas),
            "horometro_ingreso": float(orden.horometro_ingreso) if orden.horometro_ingreso else None,
            "frente_id": str(orden.frente_id) if orden.frente_id else None,
            "maquina_id": str(orden.maquina_id),
            "operador_id": str(orden.operador_id),
            "estado": orden.estado,
        }
        resp = self.client.table("ordenes_servicio").insert(payload).execute()
        return _map_orden(resp.data[0])

    async def obtener_por_operador(self, operador_id: UUID) -> Optional[OrdenServicio]:
        resp = (
            self.client.table("ordenes_servicio")
            .select("*")
            .eq("operador_id", str(operador_id))
            .in_("estado", ["ACTIVA", "EN_PROGRESO"])
            .execute()
        )
        if resp.data:
            return _map_orden(resp.data[0])
        return None

    async def listar_activas(self) -> List[OrdenServicio]:
        resp = (
            self.client.table("ordenes_servicio")
            .select("*")
            .in_("estado", ["ACTIVA", "EN_PROGRESO"])
            .order("fecha_inicio", desc=True)
            .execute()
        )
        return [_map_orden(r) for r in resp.data]

    async def obtener_por_id(self, orden_id: UUID) -> Optional[OrdenServicio]:
        resp = self.client.table("ordenes_servicio").select("*").eq("id", str(orden_id)).execute()
        if resp.data:
            return _map_orden(resp.data[0])
        return None

    async def obtener_activa_por_maquina(self, maquina_id: UUID) -> Optional[OrdenServicio]:
        resp = (
            self.client.table("ordenes_servicio")
            .select("*")
            .eq("maquina_id", str(maquina_id))
            .in_("estado", ["ACTIVA", "EN_PROGRESO"])
            .limit(1)
            .execute()
        )
        if resp.data:
            return _map_orden(resp.data[0])
        return None

    async def actualizar_estado_orden(self, orden_id: UUID, nuevo_estado: str) -> None:
        self.client.table("ordenes_servicio").update({"estado": nuevo_estado}).eq(
            "id", str(orden_id)
        ).execute()


class SupabaseReporteRepository(ReporteRepositoryPort):
    def __init__(self) -> None:
        self.client = SupabaseClientFactory.get_client()

    async def crear(self, reporte: ReporteDiario) -> ReporteDiario:
        payload = {
            "orden_id": str(reporte.orden_id),
            "fecha": reporte.fecha.isoformat(),
            "horometro_inicio": float(reporte.horometro_inicio),
            "horometro_fin": float(reporte.horometro_fin),
            "horas_trabajadas": float(reporte.horas_trabajadas),
            "galones_inicial": float(reporte.galones_inicial),
            "galones_final": float(reporte.galones_final),
            "galones_combustible": 0,
            "costo_combustible": 0,
            "descripcion": reporte.descripcion,
            "fallas_reportadas": reporte.fallas_reportadas,
            "requiere_atencion": reporte.requiere_atencion,
            "alerta_robo": reporte.alerta_robo,
            "probabilidad_fallo": float(reporte.probabilidad_fallo),
            "dias_restantes_mant": reporte.dias_restantes_mant,
        }
        resp = self.client.table("reportes_diarios").insert(payload).execute()
        return _map_reporte(resp.data[0])

    async def listar_por_orden(self, orden_id: UUID) -> List[ReporteDiario]:
        resp = (
            self.client.table("reportes_diarios")
            .select("*")
            .eq("orden_id", str(orden_id))
            .order("fecha", desc=True)
            .execute()
        )
        return [_map_reporte(r) for r in resp.data]

    async def listar_con_alerta(self) -> List[ReporteDiario]:
        resp = (
            self.client.table("reportes_diarios")
            .select("*")
            .eq("alerta_robo", True)
            .order("fecha", desc=True)
            .execute()
        )
        return [_map_reporte(r) for r in resp.data]

    async def listar_con_atencion(self) -> List[ReporteDiario]:
        try:
            resp = (
                self.client.table("reportes_diarios")
                .select("*")
                .eq("requiere_atencion", True)
                .order("fecha", desc=True)
                .execute()
            )
            return [_map_reporte(r) for r in resp.data]
        except Exception:
            return []

    async def obtener_todos(self) -> List[ReporteDiario]:
        resp = self.client.table("reportes_diarios").select("*").order("fecha", desc=True).execute()
        return [_map_reporte(r) for r in resp.data]

    async def resumen_por_orden(self, orden_id: UUID) -> dict:
        resp = (
            self.client.table("reportes_diarios")
            .select("horas_trabajadas")
            .eq("orden_id", str(orden_id))
            .execute()
        )
        total_horas = sum(float(r["horas_trabajadas"]) for r in resp.data)
        return {"cantidad_reportes": len(resp.data), "total_horas": total_horas}

    async def obtener_valorizacion(self) -> list:
        resp = self.client.table("reportes_diarios").select("*").order("fecha", desc=True).execute()
        ordenes_resp = self.client.table("ordenes_servicio").select("*").execute()
        ordenes_map = {o["id"]: o for o in (ordenes_resp.data or [])}
        resultado = []
        for r in resp.data or []:
            orden = ordenes_map.get(r["orden_id"])
            resultado.append({
                "orden": orden["numero_orden"] if orden else "N/A",
                "cliente": orden["cliente"] if orden else "N/A",
                "monto": float(orden["monto"]) if orden else 0,
                "fecha": r["fecha"],
                "horometro_inicio": float(r["horometro_inicio"]),
                "horometro_fin": float(r["horometro_fin"]),
                "horas_trabajadas": float(r["horas_trabajadas"]),
                "galones_inicial": float(r.get("galones_inicial", 0)),
                "galones_final": float(r.get("galones_final", 0)),
                "descripcion": r.get("descripcion", ""),
                "fallas_reportadas": r.get("fallas_reportadas"),
                "requiere_atencion": r.get("requiere_atencion", False),
                "alerta_robo": r.get("alerta_robo", False),
            })
        return resultado

    async def obtener_ultimo_reporte_por_orden(self, orden_id: UUID) -> Optional[ReporteDiario]:
        resp = (
            self.client.table("reportes_diarios")
            .select("*")
            .eq("orden_id", str(orden_id))
            .order("fecha", desc=True)
            .limit(1)
            .execute()
        )
        if resp.data:
            return _map_reporte(resp.data[0])
        return None

    async def eliminar(self, reporte_id: UUID) -> bool:
        resp = self.client.table("reportes_diarios").delete().eq("id", str(reporte_id)).execute()
        return len(resp.data) > 0


class SupabaseMantenimientoRepository(MantenimientoRepositoryPort):
    def __init__(self) -> None:
        self.client = SupabaseClientFactory.get_client()

    async def crear(self, mantenimiento: Mantenimiento) -> Mantenimiento:
        payload = {
            "maquina_id": str(mantenimiento.maquina_id),
            "orden_id": str(mantenimiento.orden_id) if mantenimiento.orden_id else None,
            "fecha": mantenimiento.fecha.isoformat(),
            "horometro_actual": float(mantenimiento.horometro_actual),
            "tipo": mantenimiento.tipo,
            "descripcion": mantenimiento.descripcion,
            "costo": float(mantenimiento.costo),
        }
        resp = self.client.table("mantenimientos").insert(payload).execute()
        return _map_mantenimiento(resp.data[0])

    async def listar_por_maquina(self, maquina_id: UUID) -> List[Mantenimiento]:
        resp = (
            self.client.table("mantenimientos")
            .select("*")
            .eq("maquina_id", str(maquina_id))
            .order("fecha", desc=True)
            .execute()
        )
        return [_map_mantenimiento(r) for r in resp.data]

    async def listar_todos(self) -> List[Mantenimiento]:
        resp = self.client.table("mantenimientos").select("*").order("fecha", desc=True).execute()
        return [_map_mantenimiento(r) for r in resp.data]


class SupabaseDashboardAnalytics(DashboardAnalyticsPort):
    def __init__(self) -> None:
        self.client = SupabaseClientFactory.get_client()

    async def total_facturado(self) -> float:
        resp = self.client.table("ordenes_servicio").select("monto").in_("estado", ["ACTIVA", "EN_PROGRESO", "COMPLETADA"]).execute()
        return sum(float(r["monto"]) for r in resp.data)

    async def total_horas_trabajadas(self) -> float:
        resp = self.client.table("reportes_diarios").select("horas_trabajadas").execute()
        return sum(float(r["horas_trabajadas"]) for r in resp.data)

    async def resumen_flota(self) -> dict:
        resp = self.client.table("maquinaria").select("estado_operativo").execute()
        total = len(resp.data)
        operativas = sum(1 for r in resp.data if r["estado_operativo"] == "OPERATIVA")
        mantenimiento = sum(1 for r in resp.data if r["estado_operativo"] == "EN MANTENIMIENTO")
        fuera = sum(1 for r in resp.data if r["estado_operativo"] == "FUERA DE SERVICIO")
        return {"total": total, "operativas": operativas, "en_mantenimiento": mantenimiento, "fuera_servicio": fuera}

    async def flota_completa(self) -> list:
        maq_resp = self.client.table("maquinaria").select("*").order("codigo_interno").execute()
        # Precargar ordenes activas y operadores
        ord_resp = self.client.table("ordenes_servicio").select("*").in_("estado", ["ACTIVA", "EN_PROGRESO"]).execute()
        op_resp = self.client.table("operadores").select("*").execute()
        ordenes_activas = ord_resp.data if ord_resp.data else []
        operadores = {o["id"]: f"{o['nombre']} {o['apellido']}" for o in (op_resp.data or [])}

        resultado = []
        for m in maq_resp.data or []:
            orden = next((o for o in ordenes_activas if o["maquina_id"] == m["id"]), None)

            total_horas = 0
            if orden:
                rep_resp = self.client.table("reportes_diarios").select("horas_trabajadas").eq("orden_id", orden["id"]).execute()
                total_horas = sum(float(r["horas_trabajadas"]) for r in (rep_resp.data or []))

            desde_mant = max(float(m["horometro_actual"]) - float(m["ultimo_mant_horas"]), 0)
            restantes = max(float(m["intervalo_mant_horas"]) - desde_mant, 0)

            operador_nombre = operadores.get(orden["operador_id"]) if orden else None

            resultado.append({
                "id": m["id"],
                "codigo_interno": m["codigo_interno"],
                "marca": m["marca"],
                "modelo": m["modelo"],
                "tipo": m["tipo"],
                "capacidad_ton": m["capacidad_ton"],
                "horometro_actual": float(m["horometro_actual"]),
                "ultimo_mant_horas": float(m["ultimo_mant_horas"]),
                "intervalo_mant_horas": float(m["intervalo_mant_horas"]),
                "horas_desde_ultimo_mant": desde_mant,
                "horas_restantes_mant": restantes,
                "estado_operativo": m["estado_operativo"],
                "notas_mantenimiento": m.get("notas_mantenimiento", ""),
                "nombre_completo": f"{m['marca']} {m['modelo']} ({m['codigo_interno']})",
                "en_trabajo": orden is not None,
                "ubicacion": orden.get("cliente", "") if orden else "Sin asignar",
                "operador": operador_nombre or "Sin asignar",
                "orden_id": orden["id"] if orden else None,
                "numero_orden": orden["numero_orden"] if orden else None,
                "orden_monto": float(orden["monto"]) if orden else 0,
                "total_horas_orden": total_horas,
            })
        return resultado
