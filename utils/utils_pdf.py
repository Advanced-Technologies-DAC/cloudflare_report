"""
V4 functions neccesary to run the pdf creation
"""

__version__ = "4.0.0"

import os
from datetime import datetime

from fpdf.fpdf import FPDF


def create_pdf_report(client_name: str) -> None:
    """
    Creates a PDF report with sections and manually placed images.

        Args:
            client_name (str): Name of the client.

    PDF will be saved as "<client_name>_<creation_date>.pdf".
    """
    BASE_FOLDER = "../assets"
    PARENT_LOGO = os.path.join(BASE_FOLDER, "logo_sinhap.png")
    client_logo = os.path.join(BASE_FOLDER, f"logo_{client_name}.png")
    pdf = FPDF()
    pdf.add_page()
    creation_date = datetime.today().strftime("%d-%m-%y")

    # Title
    pdf.set_font("Arial", size=16, style="B")
    pdf.cell(0, 10, txt=f"Reporte de red: {client_name}", ln=True, align="C")
    pdf.cell(0, 10, txt=f"{creation_date}", ln=True, align="C")
    pdf.image(PARENT_LOGO, x=10, y=10, w=50)
    pdf.image(client_logo, x=160, y=10, w=30)
    pdf.ln(10)

    # Section: HTTP Traffic
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(0, 10, txt="Http Traffic", ln=True, align="l")
    pdf.set_font("Arial", size=12, style="I")
    pdf.multi_cell(
        0,
        5,
        txt="Facilita la identificación de patrones de tráfico, la eficiencia del caché y la distribución de visitantes, ayudando a optimizar el rendimiento y la capacidad de respuesta de la infraestructura.",
        align="L",
    )
    pdf.image(os.path.join(BASE_FOLDER, "report_requests.png"), x=10, y=60, w=95)
    pdf.image(os.path.join(BASE_FOLDER, "report_bandwidth.png"), x=105, y=60, w=95)
    pdf.image(os.path.join(BASE_FOLDER, "report_visits.png"), x=10, y=120, w=95)
    pdf.image(os.path.join(BASE_FOLDER, "report_map.png"), x=30, y=185, w=150)

    # Section: Protocol & Content delivery
    pdf.add_page()
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(0, 10, txt="Protocol & Content delivery", ln=True, align="l")
    pdf.set_font("Arial", size=12, style="I")
    pdf.multi_cell(
        0,
        5,
        txt="Muestra los protocolos usados por el clienre, asegurando compatibilidad y eficiencia en la entrega de contenido, asi como información sobre el tipo de contenido más demandado, optimizando el uso de caché.",
        align="L",
    )
    pdf.image(os.path.join(BASE_FOLDER, "report_versions.png"), x=20, y=40, w=180)
    pdf.ln(60)

    # Section: Security Events
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(0, 10, txt="Security Events", ln=True, align="l")
    pdf.set_font("Arial", size=12, style="I")
    pdf.multi_cell(
        0,
        5,
        txt="Muestra las amenazas detectadas en la red, país de origen y tipo de ataque más. Asi como la actividad de bots/crawlers, ayudando a reforzar la seguridad y minimizar riesgos de tráfico malicioso.",
        align="L",
    )

    # Save the PDF
    folder = os.path.join(BASE_FOLDER, "reports")
    os.makedirs(folder, exist_ok=True)
    file_name = os.path.join(folder, f"{client_name}_{creation_date}.pdf")
    pdf.output(file_name)