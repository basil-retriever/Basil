from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from routers import ask, detect_intent, generate_ticket

app = FastAPI(title="BasilApi", version="1.0")

app.include_router(detect_intent.router)
app.include_router(generate_ticket.router)
app.include_router(ask.router)
app.include_router(site_scanner.router)
