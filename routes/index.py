from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import select, Session

from config.database import get_session
from models.models import DataPabrikPembuat, LokasiBahanKimia, DataBahanKimia


router = APIRouter()

# Template Jinja untuk rendering HTML
templates = Jinja2Templates(directory="templates")

# Endpoint untuk menampilkan halaman Data Bahan Kimia
@router.get("/data_bahan_kimia", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    
    # Memanggil Data lokasi bahan kimia
    lokasi_bahan_kimia = session.exec(select(LokasiBahanKimia)).all()
    
    # Memanggil Data Pabrik Pembuat
    data_pabrik_pembuat = session.exec(select(DataPabrikPembuat)).all()
    
    return templates.TemplateResponse("data_bahan_kimia.html", 
    {"request":request, 
        "lokasi_bahan_kimia": {
            "data": lokasi_bahan_kimia}, 
        "data_pabrik_pembuat": {
            "data": data_pabrik_pembuat}
        })


# Endpoint untuk menampilkan halaman Data Pabrik Pembuat
@router.get("/data_pabrik_pembuat", response_class=HTMLResponse)
def data_pabrik_pembuat(request: Request):
    return templates.TemplateResponse("data_pabrik_pembuat.html", {"request":request})


# Endpoint untuk menampilkan halaman Data Penerimaan Penggunaan
@router.get("/data_penerimaan_penggunaan", response_class=HTMLResponse)
def data_penerimaan_penggunaan(request: Request, session: Session = Depends(get_session)):
    
    # Memanggil Data Pabrik Pembuat, Lokasi Bahan Kimia, dan Data Bahan Kimia 
    data_pabrik_pembuat = session.exec(select(DataPabrikPembuat)).all()
    lokasi_bahan_kimia = session.exec(select(LokasiBahanKimia)).all()
    data_bahan_kimia = session.exec(select(DataBahanKimia)).all()
    
    # Konversi ke bentuk dictionary
    data_bahan_kimia_serialized = [item.dict() for item in data_bahan_kimia]
    lokasi_bahan_kimia_serialized = [item.dict() for item in lokasi_bahan_kimia]
    data_pabrik_pembuat_serialized = [item.dict() for item in data_pabrik_pembuat]
    
    return templates.TemplateResponse("data_penerimaan_penggunaan.html", 
    {"request":request, 
        "data_bahan_kimia": {
            "data": data_bahan_kimia_serialized},
        "lokasi_bahan_kimia": {
            "data": lokasi_bahan_kimia_serialized}, 
        "data_pabrik_pembuat": {
            "data": data_pabrik_pembuat_serialized}})


# Endpoint untuk menampilkan halaman Data Lokasi Bahan Kimia
@router.get("/lokasi_bahan_kimia", response_class=HTMLResponse)
def lokasi_bahan_kimia(request: Request, session: Session = Depends(get_session)):
    
    return templates.TemplateResponse("lokasi_bahan_kimia.html", {
        "request":request,
        })


# Endpoint untuk menampilkan halaman Main Menu
@router.get("/main_menu", response_class=HTMLResponse)
def main_menu(request: Request):
    return templates.TemplateResponse("main_menu.html", {"request":request})
