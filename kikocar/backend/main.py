import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional
from uuid import UUID

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi.responses import FileResponse, Response

from src.domain.entities import Mantenimiento, OrdenServicio, ReporteDiario
from src.infrastructure.adapters.pdf_reporte import generar_pdf_valorizacion
from src.infrastructure.adapters.predictive_adapter import PredictiveAdapter
from src.infrastructure.adapters.supabase_repository import (
    SupabaseDashboardAnalytics,
    SupabaseMantenimientoRepository,
    SupabaseMaquinaRepository,
    SupabaseOperadorRepository,
    SupabaseOrdenRepository,
    SupabaseReporteRepository,
)

load_dotenv()
app = FastAPI(title="Kikocar Construcción API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Repositorios (inyección manual) ──────────────────────────
maquina_repo = SupabaseMaquinaRepository()
operador_repo = SupabaseOperadorRepository()
orden_repo = SupabaseOrdenRepository()
reporte_repo = SupabaseReporteRepository()
mantenimiento_repo = SupabaseMantenimientoRepository()
analytics_repo = SupabaseDashboardAnalytics()
predictive = PredictiveAdapter()


# ── Schemas de request/response ──────────────────────────────

class OrdenCreateRequest(BaseModel):
    numero_orden: str
    cliente: str
    descripcion: Optional[str] = None
    monto: float
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    horas_estimadas: float = 240
    horometro_ingreso: Optional[float] = None
    frente_id: Optional[str] = None
    maquina_id: str
    operador_id: str


class ReporteCreateRequest(BaseModel):
    orden_id: str
    fecha: date
    horometro_inicio: float
    horometro_fin: float
    galones_inicial: float = 0
    galones_final: float = 0
    descripcion: Optional[str] = None
    fallas_reportadas: Optional[str] = None


class MantenimientoCreateRequest(BaseModel):
    maquina_id: str
    orden_id: Optional[str] = None
    fecha: date
    horometro_actual: float
    tipo: str = "PREVENTIVO"
    descripcion: Optional[str] = None
    costo: float = 0


# ── Endpoints ────────────────────────────────────────────────

@app.get("/api/v1/maquinaria")
async def listar_maquinaria():
    maquinas = await maquina_repo.listar_todas()
    return [
        {
            "id": str(m.id),
            "codigo_interno": m.codigo_interno,
            "marca": m.marca,
            "modelo": m.modelo,
            "tipo": m.tipo,
            "capacidad_ton": m.capacidad_ton,
            "consumo_teorico_gh": float(m.consumo_teorico_gh),
            "horometro_actual": float(m.horometro_actual),
            "ultimo_mant_horas": float(m.ultimo_mant_horas),
            "intervalo_mant_horas": float(m.intervalo_mant_horas),
            "horas_restantes_mant": m.horas_restantes_mant,
            "estado_operativo": m.estado_operativo,
            "notas_mantenimiento": m.notas_mantenimiento,
            "nombre_completo": m.nombre_completo,
        }
        for m in maquinas
    ]


@app.get("/api/v1/maquinaria/{maquina_id}/diagnostico")
async def diagnosticar_maquina(maquina_id: str):
    maquina = await maquina_repo.obtener_por_id(UUID(maquina_id))
    if not maquina:
        raise HTTPException(404, "Máquina no encontrada")

    prob, dias = predictive.evaluar(
        horas_desde_ultimo_mant=maquina.horas_desde_ultimo_mant,
        intervalo_mant_horas=float(maquina.intervalo_mant_horas),
        horas_totales_maquina=float(maquina.horometro_actual),
        capacidad_ton=maquina.capacidad_ton,
        tipo_equipo=maquina.tipo.split()[-1].lower() if maquina.tipo else "movil",
        consumo_teorico_gh=float(maquina.consumo_teorico_gh),
        alertas_previas=0,
    )
    criticidad = predictive.obtener_criticidad(prob)
    diagnostico = predictive.diagnosticar(prob, dias)
    return {
        "maquina_id": str(maquina.id),
        "nombre_completo": maquina.nombre_completo,
        "horometro_actual": float(maquina.horometro_actual),
        "ultimo_mant_horas": float(maquina.ultimo_mant_horas),
        "horas_desde_ultimo_mant": maquina.horas_desde_ultimo_mant,
        "horas_restantes_mant": maquina.horas_restantes_mant,
        "intervalo_mant_horas": float(maquina.intervalo_mant_horas),
        "probabilidad_fallo": prob,
        "dias_restantes_mant": dias,
        "criticidad": criticidad,
        "diagnostico": diagnostico,
    }


class MaquinaUpdateRequest(BaseModel):
    horometro_actual: Optional[float] = None
    estado_operativo: Optional[str] = None


@app.put("/api/v1/maquinaria/{maquina_id}")
async def actualizar_maquina(maquina_id: str, data: MaquinaUpdateRequest):
    maquina = await maquina_repo.obtener_por_id(UUID(maquina_id))
    if not maquina:
        raise HTTPException(404, "Maquina no encontrada")

    if data.horometro_actual is not None:
        await maquina_repo.actualizar_horometro(UUID(maquina_id), data.horometro_actual)
    if data.estado_operativo is not None:
        estados_validos = ["OPERATIVA", "EN MANTENIMIENTO", "FUERA DE SERVICIO"]
        if data.estado_operativo not in estados_validos:
            raise HTTPException(400, f"Estado invalido. Use: {', '.join(estados_validos)}")
        await maquina_repo.actualizar_estado(UUID(maquina_id), data.estado_operativo)

    return {"mensaje": "Maquina actualizada exitosamente"}


@app.get("/api/v1/operadores")
async def listar_operadores():
    operadores = await operador_repo.listar_todos()
    return [
        {
            "id": str(o.id),
            "dni": o.dni,
            "nombre": o.nombre,
            "apellido": o.apellido,
            "licencia": o.licencia,
            "estado": o.estado,
            "nombre_completo": o.nombre_completo,
        }
        for o in operadores
    ]


class OrdenEstadoRequest(BaseModel):
    estado: str


@app.post("/api/v1/ordenes")
async def crear_orden(data: OrdenCreateRequest):
    maquina = await maquina_repo.obtener_por_id(UUID(data.maquina_id))
    if not maquina:
        raise HTTPException(404, "Máquina no encontrada")
    operador = await operador_repo.obtener_por_id(UUID(data.operador_id))
    if not operador:
        raise HTTPException(404, "Operador no encontrado")

    # Validar que la máquina no tenga una orden activa
    orden_maquina = await orden_repo.obtener_activa_por_maquina(UUID(data.maquina_id))
    if orden_maquina:
        raise HTTPException(400, f"La máquina ya tiene una orden activa ({orden_maquina.numero_orden}). Finalícela o cancélela primero.")

    # Validar que el operador no tenga una orden activa
    orden_operador = await orden_repo.obtener_por_operador(UUID(data.operador_id))
    if orden_operador:
        raise HTTPException(400, f"El operador ya tiene una orden activa ({orden_operador.numero_orden}). Finalícela o cancélela primero.")

    orden = await orden_repo.crear(
        OrdenServicio(
            numero_orden=data.numero_orden,
            cliente=data.cliente,
            descripcion=data.descripcion,
            monto=Decimal(str(data.monto)),
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
            horas_estimadas=Decimal(str(data.horas_estimadas)),
            horometro_ingreso=Decimal(str(data.horometro_ingreso)) if data.horometro_ingreso is not None else None,
            frente_id=UUID(data.frente_id) if data.frente_id else None,
            maquina_id=UUID(data.maquina_id),
            operador_id=UUID(data.operador_id),
        )
    )

    # Sincronizar horometro de la maquina con el ingreso de la orden
    if data.horometro_ingreso is not None:
        await maquina_repo.actualizar_horometro(
            UUID(data.maquina_id), data.horometro_ingreso
        )

    return {"mensaje": "Orden creada exitosamente", "id": str(orden.id)}


@app.get("/api/v1/ordenes/operador/{operador_id}")
async def obtener_orden_operador(operador_id: str):
    orden = await orden_repo.obtener_por_operador(UUID(operador_id))
    if not orden:
        return None

    maquina = await maquina_repo.obtener_por_id(orden.maquina_id)
    ultimo_reporte = await reporte_repo.obtener_ultimo_reporte_por_orden(orden.id)

    # Si no hay reportes previos, el horometro_inicial = horometro_ingreso de la orden o el actual de la máquina
    horometro_inicial = float(orden.horometro_ingreso) if orden.horometro_ingreso is not None else (float(maquina.horometro_actual) if maquina else 0)
    ultima_fecha = None
    if ultimo_reporte:
        horometro_inicial = float(ultimo_reporte.horometro_fin)
        ultima_fecha = ultimo_reporte.fecha.isoformat()

    return {
        "id": str(orden.id),
        "numero_orden": orden.numero_orden,
        "cliente": orden.cliente,
        "descripcion": orden.descripcion,
        "monto": float(orden.monto),
        "fecha_inicio": orden.fecha_inicio.isoformat(),
        "fecha_fin": orden.fecha_fin.isoformat() if orden.fecha_fin else None,
        "maquina": maquina.nombre_completo if maquina else None,
        "maquina_id": str(orden.maquina_id),
        "estado": orden.estado,
        "horometro_inicial": horometro_inicial,
        "ultima_fecha_reporte": ultima_fecha,
    }


@app.put("/api/v1/ordenes/{orden_id}/estado")
async def cambiar_estado_orden(orden_id: str, data: OrdenEstadoRequest):
    orden = await orden_repo.obtener_por_id(UUID(orden_id))
    if not orden:
        raise HTTPException(404, "Orden no encontrada")
    estados_validos = ["COMPLETADA", "CANCELADA"]
    if data.estado not in estados_validos:
        raise HTTPException(400, f"Estado invalido. Use: {', '.join(estados_validos)}")
    await orden_repo.actualizar_estado_orden(UUID(orden_id), data.estado)
    return {"mensaje": f"Orden {data.estado.lower()} exitosamente"}


@app.get("/api/v1/ordenes")
async def listar_ordenes():
    ordenes = await orden_repo.listar_activas()
    resultados = []
    for o in ordenes:
        maquina = await maquina_repo.obtener_por_id(o.maquina_id)
        operador = await operador_repo.obtener_por_id(o.operador_id)
        resumen = await reporte_repo.resumen_por_orden(o.id)
        total_horas = resumen["total_horas"]
        estimadas = float(o.horas_estimadas)
        pct = min(100.0, round(total_horas / max(estimadas, 1) * 100, 1)) if estimadas else 0.0
        resultados.append(
            {
                "id": str(o.id),
                "numero_orden": o.numero_orden,
                "cliente": o.cliente,
                "maquina": maquina.nombre_completo if maquina else "—",
                "maquina_id": str(o.maquina_id),
                "operador": operador.nombre_completo if operador else "—",
                "operador_id": str(o.operador_id),
                "fecha_inicio": o.fecha_inicio.isoformat(),
                "fecha_fin": o.fecha_fin.isoformat() if o.fecha_fin else "—",
                "monto": float(o.monto),
                "horas_estimadas": estimadas,
                "estado": o.estado,
                "cantidad_reportes": resumen["cantidad_reportes"],
                "total_horas": total_horas,
                "porcentaje_avance": pct,
            }
        )
    return resultados


@app.post("/api/v1/reportes")
async def crear_reporte(data: ReporteCreateRequest):
    orden = await orden_repo.obtener_por_id(UUID(data.orden_id))
    if not orden:
        raise HTTPException(404, "Orden no encontrada")

    maquina = await maquina_repo.obtener_por_id(orden.maquina_id)
    if not maquina:
        raise HTTPException(404, "Máquina no encontrada")

    # ── Validación: fecha no menor a fecha de inicio de orden
    if data.fecha < orden.fecha_inicio:
        raise HTTPException(400, "La fecha del reporte no puede ser anterior a la fecha de inicio de la orden")

    # ── Validación: fecha no menor al último reporte registrado
    ultimo_reporte = await reporte_repo.obtener_ultimo_reporte_por_orden(orden.id)
    if ultimo_reporte and data.fecha < ultimo_reporte.fecha:
        raise HTTPException(400, f"La fecha del reporte no puede ser anterior al último reporte ({ultimo_reporte.fecha})")
    if ultimo_reporte and data.fecha == ultimo_reporte.fecha:
        raise HTTPException(400, f"Ya existe un reporte para la fecha {data.fecha}")

    # ── Validación: horometro_inicio debe coincidir con el último reporte (o con horometro de máquina)
    if ultimo_reporte:
        if abs(data.horometro_inicio - float(ultimo_reporte.horometro_fin)) > 0.5:
            raise HTTPException(400, f"El horómetro inicial debe ser {float(ultimo_reporte.horometro_fin):.2f} (último registro)")
    else:
        if abs(data.horometro_inicio - float(maquina.horometro_actual)) > 0.5:
            raise HTTPException(400, f"El horómetro inicial debe ser {float(maquina.horometro_actual):.2f} (horómetro actual de la máquina)")

    horas_trabajadas = Decimal(str(round(data.horometro_fin - data.horometro_inicio, 2)))
    if horas_trabajadas <= 0:
        raise HTTPException(400, "Las horas trabajadas deben ser mayores a cero")

    galones_consumidos = max(data.galones_inicial - data.galones_final, 0)

    ct = float(maquina.consumo_teorico_gh)
    if ct <= 0 or ct > 15:
        ct = 5.0
    alerta_robo = Decimal(str(galones_consumidos)) > horas_trabajadas * Decimal(str(ct)) * Decimal("1.15")

    reportes_orden = await reporte_repo.listar_por_orden(orden.id)
    alertas_previas = sum(1 for r in reportes_orden if r.alerta_robo)
    relacion_consumo = (
        (galones_consumidos / max(float(horas_trabajadas), 0.1)) / float(maquina.consumo_teorico_gh)
        if float(maquina.consumo_teorico_gh) > 0 else 1.0
    )

    requiere_atencion = bool(data.fallas_reportadas and data.fallas_reportadas.strip())
    horas_desde_ultimo_mant = maquina.horas_desde_ultimo_mant
    probabilidad_fallo, dias_restantes = predictive.evaluar(
        horas_desde_ultimo_mant=horas_desde_ultimo_mant + float(horas_trabajadas),
        intervalo_mant_horas=float(maquina.intervalo_mant_horas),
        horas_totales_maquina=float(maquina.horometro_actual) + float(horas_trabajadas),
        capacidad_ton=maquina.capacidad_ton,
        tipo_equipo=maquina.tipo.split()[-1].lower() if maquina.tipo else "movil",
        consumo_teorico_gh=float(maquina.consumo_teorico_gh),
        relacion_consumo_real=relacion_consumo,
        alertas_previas=alertas_previas,
    )

    reporte = await reporte_repo.crear(
        ReporteDiario(
            orden_id=UUID(data.orden_id),
            fecha=data.fecha,
            horometro_inicio=Decimal(str(data.horometro_inicio)),
            horometro_fin=Decimal(str(data.horometro_fin)),
            horas_trabajadas=horas_trabajadas,
            galones_inicial=Decimal(str(data.galones_inicial)),
            galones_final=Decimal(str(data.galones_final)),
            descripcion=data.descripcion,
            fallas_reportadas=data.fallas_reportadas,
            requiere_atencion=requiere_atencion,
            alerta_robo=alerta_robo,
            probabilidad_fallo=Decimal(str(probabilidad_fallo)),
            dias_restantes_mant=dias_restantes,
        )
    )

    await maquina_repo.actualizar_horometro(
        orden.maquina_id, data.horometro_fin
    )

    return {
        "mensaje": "Reporte registrado exitosamente",
        "id": str(reporte.id),
        "alerta_robo": alerta_robo,
        "probabilidad_fallo": probabilidad_fallo,
        "dias_restantes_mant": dias_restantes,
        "galones_consumidos": galones_consumidos,
        "requiere_atencion": requiere_atencion,
    }


@app.get("/api/v1/reportes/ultimo/{orden_id}")
async def obtener_ultimo_reporte(orden_id: str):
    reporte = await reporte_repo.obtener_ultimo_reporte_por_orden(UUID(orden_id))
    if not reporte:
        return None
    return {
        "horometro_fin": float(reporte.horometro_fin),
        "galones_final": float(reporte.galones_final),
        "fecha": reporte.fecha.isoformat(),
        "fallas_reportadas": reporte.fallas_reportadas,
    }


@app.get("/api/v1/reportes/alertas")
async def obtener_reportes_con_alerta():
    reportes = await reporte_repo.listar_con_alerta()
    resultados = []
    for r in reportes:
        orden = await orden_repo.obtener_por_id(r.orden_id)
        resultados.append(
            {
                "id": str(r.id),
                "orden": orden.numero_orden if orden else "N/A",
                "cliente": orden.cliente if orden else "N/A",
                "fecha": r.fecha.isoformat(),
                "horas_trabajadas": float(r.horas_trabajadas),
                "galones_inicial": float(r.galones_inicial),
                "galones_final": float(r.galones_final),
                "alerta_robo": r.alerta_robo,
            }
        )
    return resultados


@app.get("/api/v1/reportes/atencion")
async def obtener_reportes_con_atencion():
    reportes = await reporte_repo.listar_con_atencion()
    resultados = []
    for r in reportes:
        orden = await orden_repo.obtener_por_id(r.orden_id)
        resultados.append(
            {
                "id": str(r.id),
                "orden": orden.numero_orden if orden else "N/A",
                "cliente": orden.cliente if orden else "N/A",
                "fecha": r.fecha.isoformat(),
                "operador": "—",
                "fallas_reportadas": r.fallas_reportadas,
                "requiere_atencion": r.requiere_atencion,
            }
        )
    return resultados


@app.post("/api/v1/mantenimientos")
async def crear_mantenimiento(data: MantenimientoCreateRequest):
    maquina = await maquina_repo.obtener_por_id(UUID(data.maquina_id))
    if not maquina:
        raise HTTPException(404, "Máquina no encontrada")

    mant = await mantenimiento_repo.crear(
        Mantenimiento(
            maquina_id=UUID(data.maquina_id),
            orden_id=UUID(data.orden_id) if data.orden_id else None,
            fecha=data.fecha,
            horometro_actual=Decimal(str(data.horometro_actual)),
            tipo=data.tipo,
            descripcion=data.descripcion,
            costo=Decimal(str(data.costo)),
        )
    )

    # Actualizar último mantenimiento de la máquina + notas
    notas = f"[{data.fecha}] {data.tipo}: {data.descripcion or 'Sin descripción'}"
    if maquina.notas_mantenimiento:
        notas = f"{notas}\n{maquina.notas_mantenimiento}"

    await maquina_repo.registrar_mantenimiento(
        UUID(data.maquina_id), data.horometro_actual, notas
    )

    return {"mensaje": "Mantenimiento registrado exitosamente", "id": str(mant.id)}


@app.get("/api/v1/mantenimientos")
async def listar_mantenimientos(maquina_id: Optional[str] = None):
    if maquina_id:
        mants = await mantenimiento_repo.listar_por_maquina(UUID(maquina_id))
    else:
        mants = await mantenimiento_repo.listar_todos()

    resultados = []
    for m in mants:
        maquina = await maquina_repo.obtener_por_id(m.maquina_id)
        resultados.append(
            {
                "id": str(m.id),
                "maquina": maquina.codigo_interno if maquina else "—",
                "fecha": m.fecha.isoformat(),
                "horometro_actual": float(m.horometro_actual),
                "tipo": m.tipo,
                "descripcion": m.descripcion,
                "costo": float(m.costo),
            }
        )
    return resultados


@app.get("/api/v1/dashboard/kpis")
async def obtener_kpis():
    total_facturado = await analytics_repo.total_facturado()
    total_horas = await analytics_repo.total_horas_trabajadas()
    flota = await analytics_repo.resumen_flota()
    return {"total_facturado": total_facturado, "total_horas": total_horas, "flota": flota}


@app.get("/api/v1/dashboard/flota")
async def obtener_flota_completa():
    try:
        flota = await analytics_repo.flota_completa()
        return flota
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/v1/reportes/valorizacion")
async def obtener_valorizacion():
    data = await reporte_repo.obtener_valorizacion()
    return data


@app.delete("/api/v1/reportes/{reporte_id}")
async def eliminar_reporte(reporte_id: str):
    from uuid import UUID
    ok = await reporte_repo.eliminar(UUID(reporte_id))
    if not ok:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return {"mensaje": "Reporte eliminado correctamente"}


@app.get("/api/v1/reportes/valorizacion/pdf")
async def exportar_valorizacion_pdf():
    data = await reporte_repo.obtener_valorizacion()
    pdf_bytes = generar_pdf_valorizacion(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=valorizacion.pdf"},
    )


@app.get("/api/v1/reportes/valorizacion/pdf/{orden_nro}")
async def exportar_valorizacion_orden_pdf(orden_nro: str):
    data = await reporte_repo.obtener_valorizacion()
    filtrado = [r for r in data if r["orden"] == orden_nro]
    if not filtrado:
        raise HTTPException(404, f"No hay reportes para la orden {orden_nro}")
    pdf_bytes = generar_pdf_valorizacion(filtrado)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=valorizacion_{orden_nro}.pdf"},
    )


@app.get("/api/v1/reportes/predictivo")
async def obtener_predictivo():
    try:
        maquinas = await maquina_repo.listar_todas()
        ordenes = await orden_repo.obtener_todas()
    except Exception as e:
        raise HTTPException(500, f"Error cargando datos: {e}")

    ordenes_por_maq = {}
    for o in ordenes:
        mid = str(o.maquina_id)
        if mid not in ordenes_por_maq:
            ordenes_por_maq[mid] = []
        ordenes_por_maq[mid].append(o)

    resultados = []
    for m in maquinas:
        try:
            reportes_maq = []
            for o in ordenes_por_maq.get(str(m.id), []):
                rs = await reporte_repo.listar_por_orden(o.id)
                reportes_maq.extend(rs)

            total_horas = sum(float(r.horas_trabajadas) for r in reportes_maq)
            alertas = sum(1 for r in reportes_maq if r.alerta_robo)
            consumo_total = sum(float(r.galones_consumidos) for r in reportes_maq)

            ct = float(m.consumo_teorico_gh)
            if ct <= 0 or ct > 15:
                ct = 5.0
            relacion = (consumo_total / max(total_horas, 0.1)) / ct if ct > 0 else 1.0

            prob, dias = predictive.evaluar(
                horas_desde_ultimo_mant=float(m.horas_desde_ultimo_mant),
                intervalo_mant_horas=float(m.intervalo_mant_horas),
                horas_totales_maquina=float(m.horometro_actual),
                capacidad_ton=m.capacidad_ton,
                tipo_equipo=m.tipo.split()[-1].lower() if m.tipo else "movil",
                consumo_teorico_gh=ct,
                relacion_consumo_real=relacion,
                alertas_previas=alertas,
            )

            criticidad = predictive.obtener_criticidad(prob)
            diagnostico = predictive.diagnosticar(prob, dias)

            resultados.append({
                "id": str(m.id),
                "maquina": m.nombre_completo,
                "codigo": m.codigo_interno,
                "probabilidad_fallo": prob,
                "dias_restantes_mant": dias,
                "criticidad": criticidad,
                "diagnostico": diagnostico,
                "total_horas": total_horas,
                "horometro_actual": float(m.horometro_actual),
                "intervalo_mant": float(m.intervalo_mant_horas),
                "horas_desde_mant": float(m.horas_desde_ultimo_mant),
            })
        except Exception as e:
            raise HTTPException(500, f"Error procesando maquina {m.codigo_interno}: {e}")
    return resultados


_BACKEND_DIR = Path(__file__).parent


@app.get("/api/v1/modelo/metricas")
async def obtener_metricas_ml():
    path = _BACKEND_DIR / "metricas_ml.json"
    if not path.exists():
        raise HTTPException(404, "Modelo no entrenado. Ejecute train_model.py primero.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/v1/modelo/arbol")
async def obtener_arbol_img():
    path = _BACKEND_DIR / "arbol_decision.png"
    if not path.exists():
        raise HTTPException(404, "Imagen no disponible")
    return FileResponse(path, media_type="image/png")


@app.get("/api/v1/modelo/matriz-confusion")
async def obtener_matriz_img():
    path = _BACKEND_DIR / "matriz_confusion.png"
    if not path.exists():
        raise HTTPException(404, "Imagen no disponible")
    return FileResponse(path, media_type="image/png")


@app.get("/api/v1/modelo/importancia")
async def obtener_importancia_img():
    path = _BACKEND_DIR / "importancia_vars.png"
    if not path.exists():
        raise HTTPException(404, "Imagen no disponible")
    return FileResponse(path, media_type="image/png")
