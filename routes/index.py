from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import select, Session

from config.database import get_session
from models.models import Departement


router = APIRouter()

# Template Jinja untuk rendering HTML
templates = Jinja2Templates(directory="templates")

# Endpoint untuk menampilkan halaman form Departemen
@router.get("/departement", response_class=HTMLResponse)
def departement(request: Request):
    return templates.TemplateResponse("departement.html", {"request":request})

# Endpoint untuk menampilkan halaman Data Bahan Kimia
@router.get("/data_bahan_kimia", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("data_bahan_kimia.html", {"request":request})

# Endpoint untuk menampilkan halaman Data Pabrik Pembuat
@router.get("/data_pabrik_pembuat", response_class=HTMLResponse)
def data_pabrik_pembuat(request: Request):
    return templates.TemplateResponse("data_pabrik_pembuat.html", {"request":request})

# Endpoint untuk menampilkan halaman Data Penerimaan Penggunaan
@router.get("/penerimaan_penggunaan", response_class=HTMLResponse)
def penerimaan_penggunaan(request: Request):
    return templates.TemplateResponse("data_penerimaan_penggunaan.html", {"request":request})

# Endpoint untuk menampilkan halaman Data Lokasi Bahan Kimia
@router.get("/lokasi_bahan_kimia", response_class=HTMLResponse)
def lokasi_bahan_kimia(request: Request, session: Session = Depends(get_session)):
    
    # Memanggil list departement
    departement_list = session.exec(select(Departement)).all()
    
    return templates.TemplateResponse("lokasi_bahan_kimia.html", {
        "request":request,
        "departement_list": {
            'data': departement_list}
        })

# Endpoint untuk menampilkan halaman Main Menu
@router.get("/main_menu", response_class=HTMLResponse)
def main_menu(request: Request):
    return templates.TemplateResponse("main_menu.html", {"request":request})
