import os
from datetime import date
from typing import Optional

import pandas as pd
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Kikocar Construccion",
    layout="wide",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    /* ── App background ── */
    .stApp, .main > div {
        background-color: #F8F9FA;
    }
    .block-container {
        padding: 1.5rem 2rem 2rem;
        max-width: 1400px;
    }

    /* ── Sidebar dark theme ── */
    section[data-testid="stSidebar"] {
        background-color: #2B3E50 !important;
        padding: 1rem 0.75rem;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] .st-emotion-cache-1gulkj5,
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #FFC107 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.12);
        margin: 1rem 0;
    }

    /* Sidebar radio navigation */
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 2px;
        transition: all 0.2s;
        color: rgba(255,255,255,0.85) !important;
        font-size: 13px;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255,193,7,0.12);
        color: #fff !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
        background: #FFC107 !important;
        color: #2B3E50 !important;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p {
        color: #2B3E50 !important;
        font-weight: 600;
    }

    /* Sidebar button (Cerrar Sesion) */
    section[data-testid="stSidebar"] button {
        border: 1px solid rgba(255,255,255,0.25) !important;
        color: #fff !important;
        background: transparent !important;
        border-radius: 6px !important;
        font-size: 13px !important;
        transition: all 0.2s;
    }
    section[data-testid="stSidebar"] button:hover {
        background: rgba(255,255,255,0.1) !important;
        border-color: #FFC107 !important;
        color: #FFC107 !important;
    }

    /* Sidebar selectbox, radio (login) */
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label {
        color: rgba(255,255,255,0.8) !important;
    }
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background: rgba(255,255,255,0.1);
        border-color: rgba(255,255,255,0.2);
        border-radius: 6px;
    }

    /* ── Titles ── */
    .main h2, .main h3 {
        color: #2B3E50;
        font-weight: 600;
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
    }
    .main h2:after {
        content: '';
        display: block;
        width: 50px;
        height: 3px;
        background: #FFC107;
        margin-top: 6px;
        border-radius: 2px;
    }

    /* ── Subheader (st.subheader) ── */
    .stMarkdown h3 {
        color: #2B3E50;
        font-weight: 600;
        font-size: 1.15rem;
    }

    /* ── Dividers ── */
    .main hr {
        border-color: #E0E0E0;
        margin: 1.25rem 0;
    }

    /* ── DataFrames / Tables ── */
    .stDataFrame {
        border: 1px solid #E8E8E8;
        border-radius: 8px;
        overflow: hidden;
        background: white;
    }
    .stDataFrame thead tr th {
        background: #2B3E50 !important;
        color: white !important;
        font-weight: 600;
        font-size: 12px;
        padding: 8px 10px;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background: #F8F9FA;
    }
    .stDataFrame tbody tr:hover {
        background: #FFF8E1;
    }

    /* ── Info/Success/Warning/Error boxes ── */
    .stAlert {
        border-radius: 8px;
        border-left-width: 4px;
        font-size: 13px;
    }

    /* ── Buttons ── */
    button[kind="primary"] {
        background: #FFC107 !important;
        color: #2B3E50 !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.2s;
    }
    button[kind="primary"]:hover {
        background: #FFD54F !important;
        box-shadow: 0 2px 8px rgba(255,193,7,0.4);
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 6px;
        font-weight: 500;
        color: #2B3E50;
    }

    /* ── Containers / borders ── */
    div[data-testid="stVerticalBlockBorderWrapper"] > div,
    div.st-emotion-cache-1wmy9hl {
        border-radius: 8px;
    }

    /* ── KPI sidebar role box ── */
    .role-badge {
        background: rgba(255,193,7,0.15);
        border: 1px solid rgba(255,193,7,0.3);
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 12px;
        font-size: 12px;
        color: rgba(255,255,255,0.9);
    }
    .role-badge strong {
        color: #FFC107;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── Session State ────────────────────────────────────────────
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol" not in st.session_state:
    st.session_state.rol = None
if "operador_id" not in st.session_state:
    st.session_state.operador_id = None
if "operador_nombre" not in st.session_state:
    st.session_state.operador_nombre = None


# ── Helpers ─────────────────────────────────────────────────

def api_get(path: str) -> Optional[list | dict]:
    try:
        resp = requests.get(f"{API_BASE}{path}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        st.error(f"Error de conexion: {e}")
        return None


def api_post(path: str, payload: dict) -> Optional[dict]:
    try:
        resp = requests.post(f"{API_BASE}{path}", json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        st.error(f"Error de conexion: {e}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def api_put(path: str, payload: dict) -> Optional[dict]:
    try:
        resp = requests.put(f"{API_BASE}{path}", json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        st.error(f"Error de conexion: {e}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def api_get_raw(path: str) -> Optional[bytes]:
    try:
        resp = requests.get(f"{API_BASE}{path}", timeout=30)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException as e:
        st.error(f"Error de conexion: {e}")
        return None


def api_delete(path: str) -> Optional[dict]:
    try:
        resp = requests.delete(f"{API_BASE}{path}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        st.error(f"Error de conexion: {e}")
        return None


def _generar_html_valorizacion(orden: str, cliente: str, monto: float, reportes: list) -> str:
    total_h = sum(r["horas_trabajadas"] for r in reportes)
    total_g = sum(max(r["galones_inicial"] - r["galones_final"], 0) for r in reportes)
    consumo = total_g / max(total_h, 0.1)
    hoy = date.today().strftime("%d/%m/%Y")

    filas = ""
    for r in reportes:
        gc = max(r["galones_inicial"] - r["galones_final"], 0)
        filas += f"""<tr>
            <td>{r['fecha'][:10]}</td>
            <td>{r['horometro_inicio']:.1f}</td>
            <td>{r['horometro_fin']:.1f}</td>
            <td>{r['horas_trabajadas']:.1f}</td>
            <td>{r['galones_inicial']:.1f}</td>
            <td>{r['galones_final']:.1f}</td>
            <td>{gc:.1f}</td>
            <td>{r.get('descripcion','') or '-'}</td>
            <td>{r.get('fallas_reportadas','') or '-'}</td>
        </tr>"""

    tarifa = f"$ {monto / total_h:,.2f} / h" if total_h > 0 and monto > 0 else "-"

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8">
<style>
    @page {{ margin: 2cm; }}
    body {{ font-family: 'Calibri', 'Arial', sans-serif; font-size: 11pt; color: #222; }}
    h1 {{ color: #003366; font-size: 18pt; text-align: center; border-bottom: 2px solid #003366; padding-bottom: 8px; }}
    h2 {{ color: #003366; font-size: 14pt; margin-top: 20px; }}
    .header {{ text-align: center; margin-bottom: 20px; }}
    .header h3 {{ color: #003366; margin: 2px 0; }}
    .header p {{ margin: 1px 0; font-size: 9pt; color: #555; }}
    table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 9pt; }}
    th {{ background: #003366; color: white; padding: 6px 4px; text-align: center; }}
    td {{ border: 1px solid #ccc; padding: 4px; text-align: center; }}
    tr:nth-child(even) {{ background: #f5f5f5; }}
    .resumen {{ display: flex; gap: 15px; margin: 15px 0; }}
    .resumen-item {{ background: #f0f4ff; padding: 8px 15px; border-radius: 4px; border-left: 3px solid #003366; }}
    .resumen-item strong {{ display: block; font-size: 10pt; color: #003366; }}
    .footer {{ margin-top: 30px; text-align: center; border-top: 1px solid #003366; padding-top: 10px; font-size: 9pt; }}
</style>
</head>
<body>
<div class="header">
    <h1>KIKOCAR CONSTRUCCION S.A.C.</h1>
    <h3>INFORME DE VALORIZACION</h3>
    <p>RUC: 20605478921 | Av. Industrial 450, Lima - Peru</p>
</div>

<h2>ORDEN DE SERVICIO N {orden}</h2>
<p><b>Cliente:</b> {cliente} | <b>Monto Contrato:</b> $ {monto:,.2f} | <b>Total Horas:</b> {total_h:.1f} h</p>

<h2>CUADRO DE TRABAJOS DIARIOS</h2>
<table>
<tr>
    <th>Fecha</th><th>H. Inicio</th><th>H. Fin</th><th>Horas</th>
    <th>Gal. Inicial</th><th>Gal. Final</th><th>Gal. Cons.</th>
    <th>Trabajo Realizado</th><th>Observaciones</th>
</tr>
{filas}
</table>

<h2>RESUMEN</h2>
<div class="resumen">
    <div class="resumen-item"><strong>{total_h:.1f} h</strong>Total Horas Trabajadas</div>
    <div class="resumen-item"><strong>{total_g:.1f} gal</strong>Total Combustible</div>
    <div class="resumen-item"><strong>{consumo:.2f} gal/h</strong>Consumo Promedio</div>
    <div class="resumen-item"><strong>{tarifa}</strong>Tarifa Efectiva</div>
</div>

<div class="footer">
    <p><b>INGENIERO DE PROYECTOS</b><br>KIKOCAR CONSTRUCCION S.A.C.</p>
    <p>Documento generado el {hoy}</p>
</div>
</body>
</html>"""


# ── Sidebar ─────────────────────────────────────────────────

with st.sidebar:
    st.title("Kikocar Control")

    if not st.session_state.autenticado:
        st.markdown(
            "<div style='text-align:center; padding:16px 0 8px; margin-bottom:8px'>"
            "<h1 style='color:#FFC107; margin:0; font-size:22px; letter-spacing:3px; font-weight:700'>KIKOCAR</h1>"
            "<p style='color:rgba(255,255,255,0.5); font-size:9px; margin:2px 0 0; letter-spacing:2px; text-transform:uppercase'>Construccion S.A.C.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<p style='color:rgba(255,255,255,0.7); font-size:12px; font-weight:600; margin-bottom:12px'>INICIO DE SESION</p>", unsafe_allow_html=True)

        rol_sel = st.selectbox("Seleccione su rol", ["ADMINISTRADOR", "OPERADOR"], key="login_rol")

        if rol_sel == "OPERADOR":
            operadores = api_get("/api/v1/operadores")
            if operadores:
                op_options = {o["nombre_completo"]: o["id"] for o in operadores}
                selected = st.selectbox("Seleccione su nombre", list(op_options.keys()), key="login_op")
                password = st.text_input("Contrasena", type="password", key="login_pass_op")
                if st.button("Ingresar", use_container_width=True, type="primary"):
                    primer_nombre = selected.split()[0]
                    expected = primer_nombre[0].upper() + "4321"
                    if password == expected:
                        st.session_state.autenticado = True
                        st.session_state.rol = "OPERADOR"
                        st.session_state.operador_id = op_options[selected]
                        st.session_state.operador_nombre = selected
                        st.rerun()
                    else:
                        st.error("Contrasena incorrecta")
            else:
                st.warning("No hay operadores registrados")
        else:
            password = st.text_input("Contrasena", type="password", key="login_pass_admin")
            if st.button("Ingresar", use_container_width=True, type="primary"):
                if password == "1234":
                    st.session_state.autenticado = True
                    st.session_state.rol = "ADMINISTRADOR"
                    st.rerun()
                else:
                    st.error("Contrasena incorrecta")

    else:
        # Logo empresa
        st.markdown(
            "<div style='text-align:center; padding:12px 0 10px; margin-bottom:8px'>"
            "<h1 style='color:#FFC107; margin:0; font-size:24px; letter-spacing:3px; font-weight:700'>KIKOCAR</h1>"
            "<p style='color:rgba(255,255,255,0.6); font-size:9px; margin:2px 0 0; letter-spacing:2px; text-transform:uppercase'>Construccion S.A.C.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div class='role-badge'>"
            f"<strong>Rol:</strong> {st.session_state.rol}<br>"
            + (f"<strong>Operador:</strong> {st.session_state.operador_nombre}" if st.session_state.operador_nombre else "")
            + "</div>",
            unsafe_allow_html=True,
        )

        st.divider()

        # Navegacion Admin
        if st.session_state.rol == "ADMINISTRADOR":
            if "nav_admin" not in st.session_state:
                st.session_state.nav_admin = "Panel General"
            st.session_state.nav_admin = st.radio(
                "NAVEGACION",
                ["Panel General", "Registrar Orden", "Ordenes Activas",
                 "Control de Combustible", "Mantenimiento Predictivo",
                 "Alertas de Operador", "Exportar Valorizacion"],
                index=["Panel General", "Registrar Orden", "Ordenes Activas",
                       "Control de Combustible", "Mantenimiento Predictivo",
                       "Alertas de Operador", "Exportar Valorizacion"].index(st.session_state.nav_admin),
                label_visibility="collapsed",
            )
        else:
            if "nav_op" not in st.session_state:
                st.session_state.nav_op = "Mi Orden Asignada"
            st.session_state.nav_op = st.radio(
                "NAVEGACION",
                ["Mi Orden Asignada", "Rellenar Parte Diario"],
                index=["Mi Orden Asignada", "Rellenar Parte Diario"].index(st.session_state.nav_op),
                label_visibility="collapsed",
            )

        st.divider()

        # Cerrar sesion al fondo
        st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
        if st.button("Cerrar Sesion", use_container_width=True, type="secondary"):
            st.session_state.autenticado = False
            st.session_state.rol = None
            st.session_state.operador_id = None
            st.session_state.operador_nombre = None
            if "nav_admin" in st.session_state:
                del st.session_state.nav_admin
            if "nav_op" in st.session_state:
                del st.session_state.nav_op
            st.rerun()


# ── Pantalla de Login ───────────────────────────────────────

if not st.session_state.autenticado:
    st.markdown(
        """
<div style="text-align:center; padding:60px 20px">
    <h1 style="color:#2B3E50; font-size:36px; letter-spacing:3px; font-weight:700; margin-bottom:4px">KIKOCAR</h1>
    <p style="color:#777; font-size:11px; letter-spacing:2px; text-transform:uppercase; margin-bottom:30px">Construccion S.A.C.</p>
    <div style="max-width:420px; margin:0 auto; background:white; border-radius:12px; padding:30px; box-shadow:0 2px 16px rgba(43,62,80,0.1)">
        <h3 style="color:#2B3E50; margin:0 0 6px">Sistema de Gestion</h3>
        <p style="color:#888; font-size:13px; margin:0 0 20px">Flota y Ordenes de Servicio</p>
        <p style="color:#555; font-size:13px">Seleccione su rol en la barra lateral para comenzar.</p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.stop()


# ═══════════════════════════════════════════════════════════
#  PANEL ADMINISTRADOR
# ═══════════════════════════════════════════════════════════

if st.session_state.rol == "ADMINISTRADOR":
    nav = st.session_state.nav_admin

    if nav == "Panel General":
        st.subheader("Panel General de Flota")

        kpis = api_get("/api/v1/dashboard/kpis")
        flota = api_get("/api/v1/dashboard/flota")

        if kpis:
            disp = round(kpis["flota"]["operativas"] / max(kpis["flota"]["total"], 1) * 100, 1)
            total_ingresos = kpis['total_facturado']
            total_horas = kpis['total_horas']
            total_unidades = kpis['flota']['total']
            en_mant = kpis['flota']['en_mantenimiento']
            operativas = kpis['flota']['operativas']

            st.markdown(
                f"""
<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:20px">
    <div style="background:#198754; border-radius:10px; padding:18px 20px; color:white; box-shadow:0 2px 8px rgba(25,135,84,0.25)">
        <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.5px; opacity:0.85">Ingresos</div>
        <div style="font-size:24px; font-weight:700; margin-top:4px">$ {total_ingresos:,.2f}</div>
        <div style="font-size:11px; margin-top:4px; opacity:0.7">Total facturado</div>
    </div>
    <div style="background:#DC3545; border-radius:10px; padding:18px 20px; color:white; box-shadow:0 2px 8px rgba(220,53,69,0.25)">
        <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.5px; opacity:0.85">Horas Trabajadas</div>
        <div style="font-size:24px; font-weight:700; margin-top:4px">{total_horas:,.1f} h</div>
        <div style="font-size:11px; margin-top:4px; opacity:0.7">Total acumulado</div>
    </div>
    <div style="background:#0D6EFD; border-radius:10px; padding:18px 20px; color:white; box-shadow:0 2px 8px rgba(13,110,253,0.25)">
        <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.5px; opacity:0.85">Disponibilidad</div>
        <div style="font-size:24px; font-weight:700; margin-top:4px">{disp}%</div>
        <div style="font-size:11px; margin-top:4px; opacity:0.7">{operativas} de {total_unidades} unidades operativas</div>
    </div>
    <div style="background:#FD7E14; border-radius:10px; padding:18px 20px; color:white; box-shadow:0 2px 8px rgba(253,126,20,0.25)">
        <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.5px; opacity:0.85">Flota</div>
        <div style="font-size:24px; font-weight:700; margin-top:4px">{total_unidades} uds.</div>
        <div style="font-size:11px; margin-top:4px; opacity:0.7">{en_mant} en mantenimiento</div>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Tabla de flota ──────────────────────────────────
        if flota:
            st.subheader("Estado de la Flota")

            fleet_rows = []
            for m in flota:
                estado = m["estado_operativo"]
                if m["en_trabajo"]:
                    estado_display = "En Trabajo"
                elif estado == "OPERATIVA":
                    estado_display = "Disponible"
                elif estado == "EN MANTENIMIENTO":
                    estado_display = "En Mantenimiento"
                else:
                    estado_display = "Fuera de Servicio"

                # Horas restantes para mantenimiento
                restantes = m["horas_restantes_mant"]
                if restantes <= 0:
                    mant_status = "VENCIDO"
                elif restantes <= 50:
                    mant_status = f"{restantes:.0f} h (proximo)"
                else:
                    mant_status = f"{restantes:.0f} h"

                pct_avance = 0
                if m.get("total_horas_orden"):
                    orden_m = next((o for o in (api_get("/api/v1/ordenes") or []) if o["id"] == m.get("orden_id")), None)
                    if orden_m:
                        pct_avance = orden_m.get("porcentaje_avance", 0)

                # Rentabilidad (monto/hora si hay horas trabajadas)
                rent = "-"
                if m.get("total_horas_orden", 0) > 0 and m.get("orden_monto", 0) > 0:
                    tarifa = m["orden_monto"] / m["total_horas_orden"]
                    rent = f"$ {tarifa:,.0f}/h"

                fleet_rows.append({
                    "Codigo": m["codigo_interno"],
                    "Marca / Modelo": f"{m['marca']} {m['modelo']}",
                    "Estado": estado_display,
                    "Ubicacion": m.get("ubicacion", "Sin asignar"),
                    "Horometro": f"{m['horometro_actual']:,.0f} h",
                    "Operador": m.get("operador", "Sin asignar"),
                    "Rentabilidad": rent,
                    "Prox. Mantenimiento": mant_status,
                })

            df_fleet = pd.DataFrame(fleet_rows)
            st.dataframe(df_fleet, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos de flota disponibles")

        st.divider()

        # ── Graficos ────────────────────────────────────────
        if flota:
            col_ch1, col_ch2 = st.columns(2)

            with col_ch1:
                st.subheader("Horas por Unidad (Acumulado)")
                df_horas = pd.DataFrame([
                    {"Unidad": m["codigo_interno"], "Horas": m.get("total_horas_orden", 0)}
                    for m in flota if m.get("total_horas_orden", 0) > 0
                ])
                if not df_horas.empty:
                    df_horas = df_horas.set_index("Unidad")
                    st.bar_chart(df_horas)
                else:
                    st.caption("Sin datos de horas trabajadas")

            with col_ch2:
                st.subheader("Distribucion de Flota")
                estados = {"Operativas": 0, "En Trabajo": 0, "En Mantenimiento": 0, "Fuera de Servicio": 0}
                for m in flota:
                    if m["en_trabajo"]:
                        estados["En Trabajo"] += 1
                    elif m["estado_operativo"] == "OPERATIVA":
                        estados["Operativas"] += 1
                    elif m["estado_operativo"] == "EN MANTENIMIENTO":
                        estados["En Mantenimiento"] += 1
                    else:
                        estados["Fuera de Servicio"] += 1
                df_estados = pd.DataFrame(
                    {"Estado": list(estados.keys()), "Cantidad": list(estados.values())}
                ).set_index("Estado")
                st.bar_chart(df_estados)

        st.divider()

        # ── Diagnostico y edicion por unidad ────────────────
        if flota:
            st.subheader("Diagnostico y Edicion por Unidad")
            cols = st.columns(3)
            for i, m in enumerate(flota):
                diag = api_get(f"/api/v1/maquinaria/{m['id']}/diagnostico")
                if diag:
                    with cols[i % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{m['codigo_interno']}** &mdash; {m['marca']} {m['modelo']}")
                            c1, c2 = st.columns(2)
                            c1.metric("Horometro", f"{diag['horometro_actual']:,.0f} h")
                            c2.metric("Ultimo Mant.", f"{diag['ultimo_mant_horas']:,.0f} h")
                            c1.metric("Restantes Mant.", f"{diag['horas_restantes_mant']:,.0f} h")
                            c2.metric("Prob. Fallo", f"{diag['probabilidad_fallo']:.1f}%")
                            st.markdown(f"_{diag['diagnostico']}_")

                            # Notas de mantenimiento por rango de horas
                            horas_desde = m["horas_desde_ultimo_mant"]
                            intervalo = m["intervalo_mant_horas"]
                            st.caption("Proximas tareas de mantenimiento:")
                            task_lines = []
                            milestones = [
                                (10, "Inspeccion visual, nivel de fluidos, engrase"),
                                (50, "Engrase pasadores, revision cable/enganche"),
                                (100, "Cambio aceite motor (1er servicio), filtro aire"),
                                (250, "Cambio aceite + filtro motor, filtro hidraulico"),
                                (500, "Filtro combustible, aceite transmision"),
                                (1000, "Refrigerante, ajuste valvulas, aceite hidraulico"),
                                (2000, "Overhaul mayor, mangueras, rodamientos"),
                            ]
                            for hito_h, desc in milestones:
                                if hito_h > intervalo:
                                    break
                                if horas_desde < hito_h:
                                    faltan = hito_h - horas_desde
                                    task_lines.append(f"- A las {hito_h:.0f} h (faltan {faltan:.0f} h): {desc}")
                            if task_lines:
                                for t in task_lines[:4]:
                                    st.markdown(t)
                            else:
                                st.caption("Sin tareas programadas")

                            # ── Editar horometro y estado ─────────
                            with st.expander("Editar maquina"):
                                nuevo_horometro = st.number_input(
                                    "Horometro actual (h)",
                                    value=float(diag["horometro_actual"]),
                                    format="%.1f",
                                    key=f"horo_{m['id']}",
                                )
                                estado_actual = diag.get("estado_operativo", m["estado_operativo"])
                                idx_estado = ["OPERATIVA", "EN MANTENIMIENTO", "FUERA DE SERVICIO"].index(estado_actual) if estado_actual in ["OPERATIVA", "EN MANTENIMIENTO", "FUERA DE SERVICIO"] else 0
                                nuevo_estado = st.selectbox(
                                    "Estado",
                                    ["OPERATIVA (Disponible)", "EN MANTENIMIENTO", "FUERA DE SERVICIO (Baja)"],
                                    index=idx_estado,
                                    key=f"est_{m['id']}",
                                )
                                estado_map = {
                                    "OPERATIVA (Disponible)": "OPERATIVA",
                                    "EN MANTENIMIENTO": "EN MANTENIMIENTO",
                                    "FUERA DE SERVICIO (Baja)": "FUERA DE SERVICIO",
                                }
                                if m.get("en_trabajo"):
                                    st.caption("(Actualmente en obra - el estado se marcara como 'En Trabajo' en el panel)")

                                if st.button("Guardar cambios", key=f"save_{m['id']}"):
                                    payload = {}
                                    if nuevo_horometro != diag["horometro_actual"]:
                                        payload["horometro_actual"] = nuevo_horometro
                                    estado_final = estado_map[nuevo_estado]
                                    if estado_final != estado_actual:
                                        payload["estado_operativo"] = estado_final
                                    if payload:
                                        r = api_put(f"/api/v1/maquinaria/{m['id']}", payload)
                                        if r:
                                            st.success("Actualizado")
                                            st.rerun()
                                    else:
                                        st.info("Sin cambios")

    elif nav == "Registrar Orden":
        st.subheader("Registrar Nueva Orden de Servicio")

        maquinas = api_get("/api/v1/maquinaria")
        operadores = api_get("/api/v1/operadores")

        if maquinas is None or operadores is None:
            st.error("No se pudieron cargar los datos de la API")
            st.stop()

        col1, col2 = st.columns(2)

        with col1:
            numero_orden = st.text_input("Numero de Orden*")
            cliente = st.text_input("Cliente*")
            descripcion = st.text_area("Descripcion")
            monto = st.number_input("Monto (USD)", min_value=0.0, format="%.2f")

        with col2:
            fecha_inicio = st.date_input("Fecha de Inicio*", value=date.today())
            fecha_fin = st.date_input("Fecha de Fin", value=None)
            horas_estimadas = st.number_input("Horas Estimadas Totales", min_value=1, value=240)
            maq_options = {m["nombre_completo"]: m for m in maquinas}
            maquina_sel = st.selectbox("Seleccionar Grua*", list(maq_options.keys()))
            op_options = {o["nombre_completo"]: o["id"] for o in operadores}
            operador_sel = st.selectbox("Seleccionar Operador*", list(op_options.keys()))
            horometro_ingreso = st.number_input(
                "Horometro de Ingreso a Obra (h)",
                min_value=0.0, format="%.2f",
                value=float(maq_options[maquina_sel]["horometro_actual"]) if maquina_sel else 0.0,
                help="Lectura del horometro al momento de ingresar la maquina a obra"
            )

        # Advertencias si maquina u operador ya estan ocupados
        if maquina_sel:
            ordenes = api_get("/api/v1/ordenes")
            maq_id = maq_options[maquina_sel]["id"]
            op_id = op_options[operador_sel]
            if ordenes:
                maq_ocupada = any(o.get("maquina_id") == maq_id and o["estado"] in ("ACTIVA", "EN_PROGRESO") for o in ordenes)
                op_ocupado = any(o.get("operador_id") == op_id and o["estado"] in ("ACTIVA", "EN_PROGRESO") for o in ordenes)
                if maq_ocupada:
                    st.warning("Esta grua ya esta asignada a una orden activa")
                if op_ocupado:
                    st.warning("Este operador ya esta asignado a una orden activa")

        if st.button("Registrar Orden", type="primary", use_container_width=True):
            if not numero_orden or not cliente:
                st.error("Numero de Orden y Cliente son obligatorios")
            else:
                payload = {
                    "numero_orden": numero_orden,
                    "cliente": cliente,
                    "descripcion": descripcion,
                    "monto": monto,
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat() if fecha_fin else None,
                    "horas_estimadas": horas_estimadas,
                    "horometro_ingreso": horometro_ingreso,
                    "maquina_id": maq_options[maquina_sel]["id"],
                    "operador_id": op_options[operador_sel],
                }
                result = api_post("/api/v1/ordenes", payload)
                if result:
                    st.success(result["mensaje"])

    elif nav == "Ordenes Activas":
        st.subheader("Ordenes de Servicio Activas")
        ordenes = api_get("/api/v1/ordenes")
        if ordenes:
            for o in ordenes:
                with st.container(border=True):
                    cols = st.columns([2, 2, 2, 1, 2])
                    cols[0].markdown(f"**N {o['numero_orden']}**")
                    cols[1].markdown(f"*Cliente:* {o['cliente']}")
                    cols[2].markdown(f"*Grua:* {o['maquina']}")
                    cols[3].markdown(f"*Op:* {o['operador']}")
                    pct = o.get("porcentaje_avance", 0)
                    cols[4].progress(pct / 100, text=f"{pct:.0f}%")
                    with st.expander("Ver detalle"):
                        st.markdown(
                            f"**Estado:** {o['estado']}  |  "
                            f"**Inicio:** {o['fecha_inicio']}  |  "
                            f"**Fin:** {o['fecha_fin']}  |  "
                            f"**Monto:** $ {o['monto']:,.2f}"
                        )
                        st.markdown(
                            f"**Reportes diarios:** {o['cantidad_reportes']}  |  "
                            f"**Horas trabajadas:** {o['total_horas']:.1f} / {o['horas_estimadas']:.0f} h"
                        )
                        cols_acc = st.columns(2)
                        if cols_acc[0].button("Finalizar orden", key=f"fin_{o['id']}", use_container_width=True):
                            r = api_put(f"/api/v1/ordenes/{o['id']}/estado", {"estado": "COMPLETADA"})
                            if r:
                                st.success(r["mensaje"])
                                st.rerun()
                        if cols_acc[1].button("Cancelar orden", key=f"can_{o['id']}", use_container_width=True):
                            r = api_put(f"/api/v1/ordenes/{o['id']}/estado", {"estado": "CANCELADA"})
                            if r:
                                st.warning(r["mensaje"])
                                st.rerun()
        else:
            st.info("No hay ordenes activas registradas")

    elif nav == "Control de Combustible":
        st.subheader("Alertas de Consumo de Combustible")
        todos = api_get("/api/v1/reportes/valorizacion")
        if todos:
            rows = []
            for r in todos:
                gal_cons = max(r["galones_inicial"] - r["galones_final"], 0)
                horas = r["horas_trabajadas"]
                tasa = gal_cons / max(horas, 0.1)
                ct = r.get("consumo_teorico_gh", 5.0)
                esperado = horas * ct * 1.15
                alerta = gal_cons > esperado and horas > 0
                rows.append({
                    "Fecha": r["fecha"][:10],
                    "Orden": r["orden"],
                    "Horas": f"{horas:.1f}",
                    "Gal.Ini": f"{r['galones_inicial']:.1f}",
                    "Gal.Fin": f"{r['galones_final']:.1f}",
                    "Consumido": f"{gal_cons:.1f} gal",
                    "Tasa": f"{tasa:.2f} gal/h",
                    "Alerta": "SI" if alerta else "NO",
                })
            df = pd.DataFrame(rows)

            def highlight(row):
                if row["Alerta"] == "SI":
                    return ["background-color: #ffcccc"] * len(row)
                return [""] * len(row)

            styled = df.style.apply(highlight, axis=1)
            st.dataframe(styled, use_container_width=True, hide_index=True)

            total_alertas = sum(1 for r in rows if r["Alerta"] == "SI")
            if total_alertas > 0:
                st.warning(f"Se detectaron {total_alertas} reporte(s) con consumo inusual (alta carga de combustible en pocas horas).")
            else:
                st.info("No se detectaron anomalias de consumo.")
        else:
            st.info("No hay reportes registrados")

    elif nav == "Mantenimiento Predictivo":
        st.subheader("Estado de Mantenimiento de Flota")
        predictivo = api_get("/api/v1/reportes/predictivo")
        if predictivo:
            criticos = sum(1 for r in predictivo if r["criticidad"] == "CRITICO")
            medios = sum(1 for r in predictivo if r["criticidad"] == "MEDIO")
            bajos = sum(1 for r in predictivo if r["criticidad"] == "BAJO")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                    f"<div style='background:#ff4444; color:white; padding:15px; border-radius:8px; text-align:center'>"
                    f"<div style='font-size:28px; font-weight:bold'>{criticos}</div>"
                    f"<div style='font-size:12px'>Requieren Atencion Urgente</div></div>",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"<div style='background:#ffaa00; color:white; padding:15px; border-radius:8px; text-align:center'>"
                    f"<div style='font-size:28px; font-weight:bold'>{medios}</div>"
                    f"<div style='font-size:12px'>Programar Mantenimiento</div></div>",
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f"<div style='background:#44aa44; color:white; padding:15px; border-radius:8px; text-align:center'>"
                    f"<div style='font-size:28px; font-weight:bold'>{bajos}</div>"
                    f"<div style='font-size:12px'>En Condiciones Normales</div></div>",
                    unsafe_allow_html=True,
                )

            for r in predictivo:
                prob = r["probabilidad_fallo"]
                dias = r["dias_restantes_mant"]
                crit = r["criticidad"]

                if crit == "CRITICO":
                    bg = "#fff0f0"
                    border = "#ff4444"
                    badge = "CRITICO"
                    badge_bg = "#ff4444"
                elif crit == "MEDIO":
                    bg = "#fff8e6"
                    border = "#ffaa00"
                    badge = "ATENCION"
                    badge_bg = "#ffaa00"
                else:
                    bg = "#f0fff0"
                    border = "#44aa44"
                    badge = "OK"
                    badge_bg = "#44aa44"

                bar_color = "#ff4444" if prob > 70 else "#ffaa00" if prob > 30 else "#44aa44"
                dias_color = "#ff4444" if dias <= 2 else "#ffaa00" if dias <= 5 else "#44aa44"

                st.markdown(
                    f"""
<div style="background:{bg}; border-left:5px solid {border}; border-radius:6px; padding:14px 18px; margin-bottom:10px; display:flex; align-items:center; gap:20px; flex-wrap:wrap">
    <div style="min-width:100px">
        <div style="font-weight:bold; color:#003366">{r['orden']}</div>
        <div style="font-size:11px; color:#666">{r['fecha']}</div>
    </div>
    <div style="flex:1; min-width:150px">
        <div style="display:flex; justify-content:space-between; font-size:11px; color:#555; margin-bottom:3px">
            <span>Riesgo de fallo</span>
            <span>{prob:.1f}%</span>
        </div>
        <div style="background:#e0e0e0; border-radius:8px; height:10px; overflow:hidden">
            <div style="background:{bar_color}; width:{min(prob,100)}%; height:100%; border-radius:8px"></div>
        </div>
    </div>
    <div style="text-align:center; min-width:60px">
        <div style="font-size:20px; font-weight:bold; color:{dias_color}">{dias}</div>
        <div style="font-size:10px; color:#666">dias resto</div>
    </div>
    <div style="background:{badge_bg}; color:white; padding:4px 14px; border-radius:12px; font-size:11px; font-weight:bold">{badge}</div>
    <div style="font-size:12px; color:#444; flex:1; min-width:180px">{r['diagnostico']}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            st.divider()
            st.subheader("Accion Recomendada")
            if criticos > 0:
                st.error(
                    f"Hay {criticos} equipo(s) con criticidad ALTA. "
                    "Se recomienda detener operacion y realizar mantenimiento correctivo de inmediato."
                )
            elif medios > 0:
                st.warning(
                    f"Hay {medios} equipo(s) con criticidad MEDIA. "
                    "Programar mantenimiento preventivo en los proximos dias."
                )
            else:
                st.success("Todos los equipos se encuentran en condiciones optimas de operacion.")
        else:
            st.info("No hay predicciones disponibles")

        # ── Registrar Mantenimiento ────────────────────────
        st.divider()
        st.subheader("Registrar Mantenimiento Realizado")
        maquinas_list = api_get("/api/v1/maquinaria")
        if maquinas_list:
            mant_maq_opts = {m["nombre_completo"]: m["id"] for m in maquinas_list}
            mant_maq = st.selectbox("Seleccionar Grua", list(mant_maq_opts.keys()), key="mant_maq")
            maq_diag = api_get(f"/api/v1/maquinaria/{mant_maq_opts[mant_maq]}/diagnostico")
            col_a, col_b = st.columns(2)
            with col_a:
                mant_fecha = st.date_input("Fecha de Mantenimiento", value=date.today())
                mant_horas = st.number_input("Horometro Actual en Mant.", min_value=0.0, format="%.2f",
                    value=maq_diag["horometro_actual"] if maq_diag else 0)
            with col_b:
                mant_tipo = st.selectbox("Tipo", ["PREVENTIVO", "CORRECTIVO", "PREDICTIVO"])
                mant_costo = st.number_input("Costo (USD)", min_value=0.0, format="%.2f")
            mant_desc = st.text_area("Descripcion del mantenimiento realizado")
            if st.button("Registrar Mantenimiento", type="primary", use_container_width=True):
                payload = {
                    "maquina_id": mant_maq_opts[mant_maq],
                    "fecha": mant_fecha.isoformat(),
                    "horometro_actual": mant_horas,
                    "tipo": mant_tipo,
                    "descripcion": mant_desc,
                    "costo": mant_costo,
                }
                result = api_post("/api/v1/mantenimientos", payload)
                if result:
                    st.success(result["mensaje"])

    elif nav == "Alertas de Operador":
        st.subheader("Alertas Reportadas por Operadores")
        atencion = api_get("/api/v1/reportes/atencion")
        if atencion:
            for a in atencion:
                with st.container(border=True):
                    st.markdown(f"**{a['orden']}** - {a['fecha']}")
                    st.markdown(f"**Fallas reportadas:** {a['fallas_reportadas']}")
                    st.warning("Requiere atencion")
        else:
            st.info("No hay alertas de operadores pendientes")

        st.divider()
        st.subheader("Historial de Mantenimientos")
        mantenimientos = api_get("/api/v1/mantenimientos")
        if mantenimientos:
            df_mant = pd.DataFrame(mantenimientos)
            st.dataframe(df_mant, use_container_width=True, hide_index=True)
        else:
            st.info("No hay mantenimientos registrados")

    elif nav == "Exportar Valorizacion":
        st.subheader("Reporte de Valorizacion")

        valorizacion = api_get("/api/v1/reportes/valorizacion")
        if valorizacion:
            ordenes_sorted = sorted(set((r["orden"], r["cliente"], r["monto"]) for r in valorizacion))

            for orden_nro, cliente, monto in ordenes_sorted:
                reportes_orden = [r for r in valorizacion if r["orden"] == orden_nro]
                total_horas = sum(r["horas_trabajadas"] for r in reportes_orden)
                total_galones = sum(max(r["galones_inicial"] - r["galones_final"], 0) for r in reportes_orden)
                alertas = sum(1 for r in reportes_orden if r["alerta_robo"])
                fallas = sum(1 for r in reportes_orden if r.get("requiere_atencion"))
                consumo_prom = total_galones / max(total_horas, 0.1)
                tarifa = f"$ {monto / total_horas:,.2f} / h" if total_horas > 0 and monto > 0 else "-"

                st.divider()

                # Layout: contenido a la izquierda, acciones a la derecha
                col_data, col_acciones = st.columns([4, 1])

                with col_data:
                    st.markdown(
                        f"<div style='border:1px solid #003366; border-radius:5px; padding:15px; background:#f8f9fa'>"
                        f"<h3 style='color:#003366; margin:0 0 5px 0'>ORDEN DE SERVICIO N {orden_nro}</h3>"
                        f"<p style='margin:2px 0'><b>Cliente:</b> {cliente} &nbsp;|&nbsp; <b>Monto:</b> $ {monto:,.2f}</p>"
                        f"<p style='margin:2px 0'><b>Horas:</b> {total_horas:.1f} h &nbsp;|&nbsp; "
                        f"<b>Combustible:</b> {total_galones:.1f} gal &nbsp;|&nbsp; "
                        f"<b>Consumo:</b> {consumo_prom:.2f} gal/h &nbsp;|&nbsp; "
                        f"<b>Tarifa:</b> {tarifa}</p>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    st.markdown("**CUADRO DE TRABAJOS DIARIOS**")
                    cols_h = st.columns([2, 1, 1, 1, 1, 1, 2, 2, 1])
                    cols_h[0].markdown("**Fecha**")
                    cols_h[1].markdown("**H.Ini**")
                    cols_h[2].markdown("**H.Fin**")
                    cols_h[3].markdown("**Horas**")
                    cols_h[4].markdown("**Gal.Ini**")
                    cols_h[5].markdown("**Gal.Fin**")
                    cols_h[6].markdown("**Gal.Cons**")
                    cols_h[7].markdown("**Trabajo**")
                    cols_h[8].markdown("**Acc**")
                    for r in reportes_orden:
                        gal_cons = max(r["galones_inicial"] - r["galones_final"], 0)
                        cols_r = st.columns([2, 1, 1, 1, 1, 1, 2, 2, 1])
                        cols_r[0].markdown(f"**{r['fecha'][:10]}**")
                        cols_r[1].markdown(f"{r['horometro_inicio']:.1f}")
                        cols_r[2].markdown(f"{r['horometro_fin']:.1f}")
                        cols_r[3].markdown(f"{r['horas_trabajadas']:.1f}")
                        cols_r[4].markdown(f"{r['galones_inicial']:.1f}")
                        cols_r[5].markdown(f"{r['galones_final']:.1f}")
                        cols_r[6].markdown(f"{gal_cons:.1f}")
                        cols_r[7].markdown(r.get("descripcion", "")[:40] or "-")
                        if cols_r[8].button("X", key=f"del_{r['id']}", help="Eliminar este reporte"):
                            if api_delete(f"/api/v1/reportes/{r['id']}"):
                                st.success("Reporte eliminado. Recarga la pagina.")
                                st.rerun()
                            else:
                                st.error("No se pudo eliminar el reporte")
                    st.markdown("---")

                    st.markdown(
                        f"""
<div style="display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin:12px 0">
    <div style="background:#198754; border-radius:8px; padding:12px; color:white; text-align:center">
        <div style="font-size:18px; font-weight:700">{total_horas:.1f} h</div>
        <div style="font-size:10px; opacity:0.8">Total Horas</div>
    </div>
    <div style="background:#DC3545; border-radius:8px; padding:12px; color:white; text-align:center">
        <div style="font-size:18px; font-weight:700">{total_galones:.1f} gal</div>
        <div style="font-size:10px; opacity:0.8">Total Combustible</div>
    </div>
    <div style="background:#0D6EFD; border-radius:8px; padding:12px; color:white; text-align:center">
        <div style="font-size:18px; font-weight:700">{consumo_prom:.2f} gal/h</div>
        <div style="font-size:10px; opacity:0.8">Consumo Promedio</div>
    </div>
    <div style="background:#FD7E14; border-radius:8px; padding:12px; color:white; text-align:center">
        <div style="font-size:18px; font-weight:700">{alertas}</div>
        <div style="font-size:10px; opacity:0.8">Alertas Consumo</div>
    </div>
    <div style="background:#6F42C1; border-radius:8px; padding:12px; color:white; text-align:center">
        <div style="font-size:18px; font-weight:700">{fallas}</div>
        <div style="font-size:10px; opacity:0.8">Incidencias</div>
    </div>
</div>
""",
                        unsafe_allow_html=True,
                    )

                with col_acciones:
                    st.markdown(
                        "<div style='border:1px solid #ddd; border-radius:5px; padding:12px; background:white; text-align:center'>"
                        "<p style='font-weight:bold; color:#003366; margin:0 0 10px 0'>DESCARGAR</p>",
                        unsafe_allow_html=True,
                    )
                    pdf_bytes = api_get_raw("/api/v1/reportes/valorizacion/pdf")
                    st.download_button(
                        label="Descargar PDF",
                        data=pdf_bytes,
                        file_name=f"valorizacion_{orden_nro}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary",
                    )
                    html_content = _generar_html_valorizacion(orden_nro, cliente, monto, reportes_orden)
                    st.download_button(
                        label="Descargar Word",
                        data=html_content,
                        file_name=f"valorizacion_{orden_nro}.html",
                        mime="text/html",
                        use_container_width=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No hay reportes diarios registrados para valorizacion")


# ═══════════════════════════════════════════════════════════
#  PANEL OPERADOR
# ═══════════════════════════════════════════════════════════

if st.session_state.rol == "OPERADOR":
    operador_id = st.session_state.operador_id
    nav = st.session_state.nav_op

    if nav == "Mi Orden Asignada":
        st.subheader("Mi Orden de Servicio Asignada")
        orden = api_get(f"/api/v1/ordenes/operador/{operador_id}")
        if orden:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**N Orden:** {orden['numero_orden']}")
                st.markdown(f"**Cliente:** {orden['cliente']}")
                st.markdown(f"**Descripcion:** {orden.get('descripcion', '-')}")
                if orden.get("ultima_fecha_reporte"):
                    st.markdown(f"**Ultimo reporte:** {orden['ultima_fecha_reporte']}")
            with col2:
                st.markdown(f"**Grua Asignada:** {orden.get('maquina', '-')}")
                st.markdown(f"**Fecha Inicio:** {orden['fecha_inicio']}")
                st.markdown(f"**Monto:** $ {orden['monto']:,.2f}")
        else:
            st.warning("No tiene una orden activa asignada")

    elif nav == "Rellenar Parte Diario":
        st.subheader("Registrar Parte Diario")

        orden = api_get(f"/api/v1/ordenes/operador/{operador_id}")
        if not orden:
            st.warning("No tiene una orden activa para reportar")
            st.stop()

        orden_id = orden["id"]

        horometro_inicial = orden.get("horometro_inicial", 0)
        ultima_fecha = orden.get("ultima_fecha_reporte")
        fecha_inicio_orden = date.fromisoformat(orden["fecha_inicio"]) if orden.get("fecha_inicio") else None

        st.info(
            f"Horometro inicial bloqueado: {horometro_inicial:.2f} h  |  "
            f"Ultimo reporte: {ultima_fecha or 'Ninguno'}  |  "
            f"Orden iniciada: {orden['fecha_inicio']}"
        )

        col1, col2 = st.columns(2)

        with col1:
            fecha = st.date_input("Fecha del reporte", value=date.today())

            errores_fecha = []
            if fecha_inicio_orden and fecha < fecha_inicio_orden:
                errores_fecha.append(f"La fecha no puede ser anterior al inicio de la orden ({orden['fecha_inicio']})")
            if ultima_fecha:
                min_date = date.fromisoformat(ultima_fecha)
                if fecha <= min_date:
                    errores_fecha.append(f"La fecha debe ser posterior al ultimo reporte ({ultima_fecha})")
            for err in errores_fecha:
                st.error(err)

            st.number_input(
                "Horometro Inicial (automatico)",
                value=horometro_inicial,
                disabled=True,
                format="%.2f",
            )
            horometro_fin = st.number_input(
                "Horometro Final (ingrese lectura)",
                min_value=horometro_inicial + 0.1,
                format="%.2f",
            )

        with col2:
            galones_inicial = st.number_input(
                "Lectura Inicial de Combustible (gal)",
                min_value=0.0,
                format="%.2f",
            )
            galones_final = st.number_input(
                "Lectura Final de Combustible (gal)",
                min_value=0.0,
                format="%.2f",
            )
            descripcion = st.text_area("Descripcion del Trabajo Realizado")

        fallas = st.text_area(
            "Fallas o anomalias detectadas durante el servicio",
            placeholder="Ej: Sensor de temperatura con lectura intermitente, fuga de aceite hidraulico...",
            help="Si reporta algo aqui, se generara una alerta para el Administrador",
        )

        if horometro_fin > horometro_inicial:
            st.info(
                f"Horas trabajadas: {horometro_fin - horometro_inicial:.2f} h  |  "
                f"Galones consumidos: {max(galones_inicial - galones_final, 0):.2f} gal"
            )

        if st.button("Enviar Parte Diario", type="primary", use_container_width=True):
            if errores_fecha:
                st.error("Corrija los errores de fecha antes de enviar")
            elif ultima_fecha and fecha <= date.fromisoformat(ultima_fecha):
                st.error(f"Ya existe un reporte para la fecha {ultima_fecha} o posterior")
            else:
                payload = {
                    "orden_id": orden_id,
                    "fecha": fecha.isoformat(),
                    "horometro_inicio": horometro_inicial,
                    "horometro_fin": horometro_fin,
                    "galones_inicial": galones_inicial,
                    "galones_final": galones_final,
                    "descripcion": descripcion,
                    "fallas_reportadas": fallas if fallas.strip() else None,
                }
                result = api_post("/api/v1/reportes", payload)
                if result:
                    st.success("Parte diario registrado exitosamente")
                    if result["alerta_robo"]:
                        st.warning(
                            f"Alerta: Consumo de {result['galones_consumidos']:.2f} gal "
                            f"supera el umbral permitido"
                        )
                    if result["requiere_atencion"]:
                        st.warning("Se ha notificado al Administrador sobre las fallas reportadas")
                    st.info(
                        f"Diagnostico ML - Probabilidad de fallo: {result['probabilidad_fallo']:.1f}% | "
                        f"Dias para mantenimiento: {result['dias_restantes_mant']}"
                    )
