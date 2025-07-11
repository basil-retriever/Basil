from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from fpdf import FPDF
import tempfile
import os

router = APIRouter()

class Attendee(BaseModel):
    name: str
    email: str

class PDFRequest(BaseModel):
    attendees: list[Attendee]

@router.post("/generate-ticket")
def generate_ticket(data: PDFRequest):
    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, "Your AI Meetup Tickets", ln=True)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        for person in data.attendees:
            pdf.cell(200, 10, f"{person.name} - {person.email}", ln=True)

        pdf.output(tmp_file.name)
        return FileResponse(tmp_file.name, filename="tickets.pdf", media_type='application/pdf')
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"PDF generation failed: {str(e)}"})
    finally:
        if os.path.exists(tmp_file.name):
            os.remove(tmp_file.name)
