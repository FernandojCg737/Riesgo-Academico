from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "branding"

LOGO_ALTURA = 1.3 * cm


def _logo(nombre_archivo: str) -> Image:
    ruta = ASSETS_DIR / nombre_archivo
    img = Image(str(ruta))
    proporcion = img.imageWidth / img.imageHeight
    img.drawHeight = LOGO_ALTURA
    img.drawWidth = LOGO_ALTURA * proporcion
    return img


class ReportPdfService:
    def generar_reporte_metricas(
        self,
        dataset_nombre: str,
        resumen: Dict[str, Any],
        mejor_modelo: Dict[str, Any] | None,
        metricas: List[Dict[str, Any]],
    ) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
        )

        estilos = getSampleStyleSheet()
        titulo_style = ParagraphStyle(
            "TituloReporte", parent=estilos["Title"], fontSize=16, spaceAfter=2
        )
        subtitulo_style = ParagraphStyle(
            "SubtituloReporte", parent=estilos["Normal"], fontSize=10, textColor=colors.grey
        )
        seccion_style = ParagraphStyle(
            "SeccionReporte", parent=estilos["Heading2"], fontSize=12, spaceBefore=14, spaceAfter=6
        )
        cuerpo_style = ParagraphStyle("CuerpoReporte", parent=estilos["Normal"], fontSize=10, leading=14)

        elementos = []

        encabezado_logos = Table(
            [[_logo("mascota-robot.png"), _logo("logo-uagrm.png"), _logo("logo-iicct.png")]],
            colWidths=[doc.width / 3] * 3,
        )
        encabezado_logos.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                    ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        elementos.append(encabezado_logos)
        elementos.append(Spacer(1, 0.4 * cm))

        elementos.append(Paragraph("Reporte de Riesgo Académico Estudiantil", titulo_style))
        elementos.append(
            Paragraph(
                f"Dataset: {dataset_nombre} — Generado el "
                f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
                subtitulo_style,
            )
        )
        elementos.append(Spacer(1, 0.3 * cm))

        elementos.append(Paragraph("Resumen Ejecutivo", seccion_style))
        elementos.append(
            Paragraph(
                f"Se analizaron <b>{resumen.get('total_registros', 0):,}</b> registros estudiante-materia "
                f"correspondientes a <b>{resumen.get('estudiantes_unicos', 0):,}</b> estudiantes únicos en "
                f"<b>{resumen.get('materias_unicas', 0)}</b> materias. La tasa de riesgo académico observada "
                f"es del <b>{resumen.get('tasa_riesgo_porcentaje', 0)}%</b> "
                f"({resumen.get('registros_en_riesgo', 0):,} registros en riesgo).",
                cuerpo_style,
            )
        )

        if mejor_modelo:
            m = mejor_modelo["metricas"]
            elementos.append(Spacer(1, 0.2 * cm))
            elementos.append(
                Paragraph(
                    f"El modelo seleccionado automáticamente es <b>{mejor_modelo['nombre_modelo']}</b>, con un "
                    f"Recall de <b>{m['recall_clase_1'] * 100:.2f}%</b> sobre la clase de riesgo, Precision de "
                    f"<b>{m['precision_clase_1'] * 100:.2f}%</b> y Accuracy general de "
                    f"<b>{m['accuracy'] * 100:.2f}%</b>. La selección prioriza el Recall para minimizar los "
                    f"falsos negativos (estudiantes en riesgo no detectados).",
                    cuerpo_style,
                )
            )

        elementos.append(Paragraph("Métricas Comparativas (6 modelos)", seccion_style))

        celda_modelo_style = ParagraphStyle("CeldaModelo", parent=estilos["Normal"], fontSize=8.5, leading=10)

        encabezados = ["Modelo", "Config.", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "FN"]
        filas = [encabezados]
        for met in metricas:
            nombre_modelo = met["nombre_legible"] + (" ★" if met.get("es_modelo_final") else "")
            filas.append(
                [
                    Paragraph(nombre_modelo, celda_modelo_style),
                    met["configuracion"].capitalize(),
                    f"{met['accuracy_test'] * 100:.2f}%",
                    f"{met['precision_clase_1'] * 100:.2f}%",
                    f"{met['recall_clase_1'] * 100:.2f}%",
                    f"{met['f1_clase_1']:.4f}",
                    f"{met['roc_auc_test']:.4f}",
                    str(met["falsos_negativos"]),
                ]
            )

        tabla = Table(filas, repeatRows=1, colWidths=[doc.width * w for w in (0.28, 0.11, 0.105, 0.105, 0.105, 0.105, 0.105, 0.085)])
        estilo_tabla = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ALIGN", (2, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
        ]
        for i, met in enumerate(metricas, start=1):
            if met.get("es_modelo_final"):
                estilo_tabla.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#cfe8d8")))
        tabla.setStyle(TableStyle(estilo_tabla))
        elementos.append(tabla)

        elementos.append(Spacer(1, 0.3 * cm))
        elementos.append(
            Paragraph(
                "★ Modelo ganador, seleccionado automáticamente por mayor Recall sobre la clase de riesgo.",
                ParagraphStyle("Nota", parent=estilos["Normal"], fontSize=8, textColor=colors.grey),
            )
        )

        doc.build(elementos)
        return buffer.getvalue()
