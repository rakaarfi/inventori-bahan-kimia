from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session

from models.models import LokasiBahanKimia
from config.database import get_session


router = APIRouter()

# Template Jinja untuk rendering HTML
templates = Jinja2Templates(directory="templates")

# Endpoint untuk membuat Lokasi Bahan Kimia baru
@router.post("/create_lokasi_bahan_kimia/")
def create_lokasi_bahan_kimia(
    session: Session = Depends(get_session), 
    room: str = Form(...), 
    location: str = Form(...), 
    building: str = Form(...),
    departement_name: str = Form(...),
    contact_person: str = Form(...),
    phone: str = Form(...)
    ):
    
    new_lokasi_bahan_kimia = LokasiBahanKimia(
        room=room, 
        location=location, 
        building=building, 
        departement_name=departement_name,
        contact_person=contact_person, 
        phone=phone
        )
    
    session.add(new_lokasi_bahan_kimia)
    session.commit()
    session.refresh(new_lokasi_bahan_kimia)
    
    return new_lokasi_bahan_kimia
    # return RedirectResponse(url="/data_pabrik_pembuat/list_data_pabrik_pembuat", status_code=303)

# Endpoint untuk membaca semua Lokasi Bahan Kimia
@router.get("/read_lokasi_bahan_kimia/")
def read_lokasi_bahan_kimia(session: Session = Depends(get_session)):
    lokasi_bahan_kimia = session.exec(select(LokasiBahanKimia)).all()
    return lokasi_bahan_kimia

# Endpoint untuk memperbarui Lokasi Bahan Kimia
@router.post("/update_lokasi_bahan_kimia/{id}")
def update_lokasi_bahan_kimia(
    id: int, 
    session: Session = Depends(get_session), 
    room: str = Form(...), 
    location: str = Form(...), 
    building: str = Form(...),
    departement_name: str = Form(...),
    contact_person: str = Form(...),
    phone: str = Form(...)
    ):
    
    db_lokasi_bahan_kimia = session.exec(select(LokasiBahanKimia).where(LokasiBahanKimia.id == id)).first()
    if db_lokasi_bahan_kimia is None:
        raise HTTPException(status_code=404, detail="Data Pabrik Pembuat tidak ditemukan")
    
    db_lokasi_bahan_kimia.room = room
    db_lokasi_bahan_kimia.location = location
    db_lokasi_bahan_kimia.building = building
    db_lokasi_bahan_kimia.departement_name = departement_name
    db_lokasi_bahan_kimia.contact_person = contact_person
    db_lokasi_bahan_kimia.phone = phone
    
    session.add(db_lokasi_bahan_kimia)
    session.commit()
    session.refresh(db_lokasi_bahan_kimia)
    
    return db_lokasi_bahan_kimia
    # return RedirectResponse(url="/data_pabrik_pembuat/list_data_pabrik_pembuat", status_code=303)

# Endpoint untuk menghapus Lokasi Bahan Kimia
@router.post("/delete_lokasi_bahan_kimia/{id}")
def delete_lokasi_bahan_kimia(
    id: int, 
    session: Session = Depends(get_session)):
    
    db_lokasi_bahan_kimia = session.exec(select(LokasiBahanKimia).where(LokasiBahanKimia.id == id)).first()
    
    if db_lokasi_bahan_kimia is None:
        raise HTTPException(status_code=404, detail="Data Pabrik Pembuat tidak ditemukan")
    
    session.delete(db_lokasi_bahan_kimia)
    session.commit()
    
    return RedirectResponse(url="/lokasi_bahan_kimia/read_lokasi_bahan_kimia", status_code=303)

# @router.get("/list_data_pabrik_pembuat")
# def list_data_pabrik_pembuat(
#     request: Request, page: int = 1, 
#     limit: int = 10, search: str = '', 
#     session: Session = Depends(get_session)):

#     # Hitung offset berdasarkan halaman yang diminta
#     offset = (page - 1) * limit

#     # Query untuk mencari data dengan pencarian di nama, alamat, atau telepon
#     query = select(DataPabrikPembuat).offset(offset).limit(limit)
    
#     condition = (DataPabrikPembuat.name.ilike(f'%{search}%') |
#                 DataPabrikPembuat.address.ilike(f'%{search}%') |
#                 DataPabrikPembuat.phone.ilike(f'%{search}%'))
    
#     if search:
#         query = query.where(condition)
    
#     # Ambil data dengan pagination berdarsarkan query
#     data = session.exec(query).all()
    
#     # Hitung total jumlah data yang sesuai dengan query pencarian
#     total_data = len(session.exec(select(DataPabrikPembuat).where(condition)).all())
    
#     # Menghitung jumlah halaman
#     total_pages = (total_data + limit - 1) // limit  # Membulatkan ke atas
    
#     # Mengembalikan data dan pagination
#     return templates.TemplateResponse("list_data_pabrik_pembuat.html", {
#         "request": request,
#         "list_data_pabrik_pembuat": {
#             "data": data,
#             "page": page,
#             "total_pages": total_pages,
#             "total_data": total_data
#         },
#         "search_query": search # Menyertakan query pencarian dalam template
#     })
