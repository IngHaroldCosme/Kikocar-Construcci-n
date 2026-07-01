from io import BytesIO
from typing import List

from fpdf import FPDF


class ReporteValorizacionPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 8, "KIKOCAR CONSTRUCCION S.A.C.", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 9)
        self.cell(0, 5, "RUC: 20605478921 | Av. Industrial 450, Lima - Peru", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, "Tel: (01) 555-0456 | Email: proyectos@kikocar.com", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def titulo(self, texto: str):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, texto, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def subtitulo(self, texto: str):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 7, f"  {texto}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

    def par(self, label: str, valor: str):
        self.set_font("Helvetica", "", 9)
        ancho_label = 50
        self.cell(ancho_label, 5, f"  {label}:", align="R")
        self.set_font("Helvetica", "B", 9)
        self.cell(0, 5, f"  {valor}", new_x="LMARGIN", new_y="NEXT")

    def tabla_reportes(self, headers: List[str], data: List[List[str]], col_widths: List[float]):
        self.set_font("Helvetica", "B", 7)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 6, h, border=1, align="C", fill=True)
        self.ln()
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "", 7)
        for row in data:
            for i, val in enumerate(row):
                self.cell(col_widths[i], 5, val, border=1, align="C")
            self.ln()
        self.ln(3)


def generar_pdf_valorizacion(datos: List[dict]) -> bytes:
    pdf = ReporteValorizacionPDF(orientation="L", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    if not datos:
        pdf.add_page()
        pdf.titulo("INFORME DE VALORIZACION")
        pdf.subtitulo("No hay datos registrados")
        return pdf.output()

    # Agrupar por orden
    grupos = {}
    for r in datos:
        key = r["orden"]
        if key not in grupos:
            grupos[key] = {
                "orden": r["orden"],
                "cliente": r["cliente"],
                "monto": r["monto"],
                "reportes": [],
            }
        grupos[key]["reportes"].append(r)

    for g in grupos.values():
        pdf.add_page()
        pdf.titulo("INFORME DE VALORIZACION")

        # Datos del servicio
        pdf.subtitulo("1. DATOS DEL SERVICIO")
        pdf.par("Orden de Servicio", g["orden"])
        pdf.par("Cliente", g["cliente"])
        pdf.par("Monto Contrato", f"$ {g['monto']:,.2f}")

        reportes = g["reportes"]
        total_horas = sum(r["horas_trabajadas"] for r in reportes)
        total_galones = sum(max(r["galones_inicial"] - r["galones_final"], 0) for r in reportes)
        alertas = sum(1 for r in reportes if r["alerta_robo"])
        fallas = sum(1 for r in reportes if r.get("requiere_atencion"))

        pdf.par("Total Horas Trabajadas", f"{total_horas:.1f} h")
        pdf.par("Total Combustible", f"{total_galones:.1f} gal")
        consumo_prom = total_galones / max(total_horas, 0.1)
        pdf.par("Consumo Promedio", f"{consumo_prom:.2f} gal/h")

        pct_avance = 0
        horas_estimadas = 240
        if reportes:
            horas_estimadas = 240
            pct_avance = min(100, round(total_horas / max(horas_estimadas, 1) * 100, 1))
        pdf.par("% Avance", f"{pct_avance}%")

        alerta_texto = "SI" if alertas > 0 else "NO"
        pdf.par("Alertas de Consumo", alerta_texto)

        # Cuadro de trabajos diarios
        pdf.subtitulo("2. CUADRO DE TRABAJOS DIARIOS")
        headers = ["Fecha", "H. Inicio", "H. Fin", "Horas", "Gal. Inicial", "Gal. Final", "Gal. Cons.", "Trabajo Realizado", "Observaciones"]
        col_widths = [22, 16, 16, 14, 16, 16, 16, 70, 40]

        rows = []
        for r in reportes:
            gal_cons = max(r["galones_inicial"] - r["galones_final"], 0)
            desc = r.get("descripcion", "") or "-"
            if len(desc) > 40:
                desc = desc[:38] + ".."
            falla = r.get("fallas_reportadas", "") or "-"
            if len(falla) > 25:
                falla = falla[:23] + ".."
            rows.append([
                r["fecha"][:10],
                f"{r['horometro_inicio']:.1f}",
                f"{r['horometro_fin']:.1f}",
                f"{r['horas_trabajadas']:.1f}",
                f"{r['galones_inicial']:.1f}",
                f"{r['galones_final']:.1f}",
                f"{gal_cons:.1f}",
                desc,
                falla,
            ])
        pdf.tabla_reportes(headers, rows, col_widths)

        # Resumen
        pdf.subtitulo("3. RENTABILIDAD")
        if total_horas > 0:
            tarifa = g["monto"] / total_horas
            pdf.par("Tarifa Efectiva", f"$ {tarifa:,.2f} / h")
        pdf.par("Total Facturado", f"$ {g['monto']:,.2f}")

        pdf.ln(10)
        pdf.line(40, pdf.get_y(), 170, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 5, "INGENIERO DE PROYECTOS", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 4, "KIKOCAR CONSTRUCCION S.A.C.", new_x="LMARGIN", new_y="NEXT", align="C")

    return bytes(pdf.output())
