"""
===========================================================
Smart Vehicle Identifier
PDF Export
===========================================================

Builds a downloadable PDF report for one or more vehicles
that the user discussed with the AI assistant.

Responsibilities
----------------
- Render a clean, readable vehicle comparison/report
- Fail with a clear, actionable error if the PDF backend
  (fpdf2) is not installed

No Streamlit / UI code lives here.

Requires:
    pip install fpdf2
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def build_vehicle_pdf(
    vehicles: list[dict[str, Any]],
    title: str = "Vehicle Report - Smart Vehicle Identifier",
) -> bytes:
    """
    Build a PDF report for the given vehicles.

    Parameters
    ----------
    vehicles:
        List of vehicle dicts (make, model, year, confidence,
        description, ...).

    Returns
    -------
    bytes
        The PDF file content.
    """

    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError(
            "PDF export requires the 'fpdf2' package. "
            "Install it with: pip install fpdf2"
        ) from exc

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, title, ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, f"Generated: {datetime.now():%Y-%m-%d %H:%M}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    if not vehicles:
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, "No vehicles to report.", ln=True)
        return bytes(pdf.output(dest="S"))

    for vehicle in vehicles:

        make = vehicle.get("make", "Unknown")
        model = vehicle.get("model", "Unknown")
        year = vehicle.get("year") or "-"
        confidence = vehicle.get("confidence")
        description = vehicle.get("description")

        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"{make} {model}", ln=True)

        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"Year: {year}", ln=True)

        if confidence is not None:
            confidence_text = (
                f"{confidence:.1%}"
                if isinstance(confidence, float)
                else str(confidence)
            )
            pdf.cell(0, 7, f"Confidence: {confidence_text}", ln=True)

        if description:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, description)

        pdf.ln(3)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(6)

    return bytes(pdf.output(dest="S"))
