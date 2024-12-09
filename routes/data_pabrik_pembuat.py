from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session

from models.models import DataPabrikPembuat
from config.database import get_session


router = APIRouter()

# Template Jinja untuk rendering HTML
templates = Jinja2Templates(directory="templates")

# Endpoint untuk membuat Data Pabrik Pembuat baru
@router.post("/create_data_pabrik_pembuat/")
def create_data_pabrik_pembuat(
    session: Session = Depends(get_session), 
    name: str = Form(...), 
    address: str = Form(...), 
    phone: str = Form(...)
    ):
    
    new_data_pabrik_pembuat = DataPabrikPembuat(
        name=name, 
        address=address, 
        phone=phone
        )
    
    session.add(new_data_pabrik_pembuat)
    session.commit()
    session.refresh(new_data_pabrik_pembuat)
    
    return new_data_pabrik_pembuat
    
    # return RedirectResponse(url="/data_pabrik_pembuat/list_data_pabrik_pembuat", status_code=303)

# Endpoint untuk membaca semua Data Pabrik Pembuat
@router.get("/read_data_pabrik_pembuat/")
def read_data_pabrik_pembuat(session: Session = Depends(get_session)):
    data_pabrik_pembuat = session.exec(select(DataPabrikPembuat)).all()
    return data_pabrik_pembuat

# Endpoint untuk memperbarui Data Pabrik Pembuat
@router.post("/update_data_pabrik_pembuat/{id}")
def update_data_pabrik_pembuat(
    id: int, 
    session: Session = Depends(get_session), 
    name: str = Form(...), 
    address: str = Form(...), 
    phone: str = Form(...)):
    
    db_data_pabrik_pembuat = session.exec(select(DataPabrikPembuat).where(DataPabrikPembuat.id == id)).first()
    if db_data_pabrik_pembuat is None:
        raise HTTPException(status_code=404, detail="Data Pabrik Pembuat tidak ditemukan")
    
    db_data_pabrik_pembuat.name = name
    db_data_pabrik_pembuat.address = address
    db_data_pabrik_pembuat.phone = phone
    
    session.add(db_data_pabrik_pembuat)
    session.commit()
    session.refresh(db_data_pabrik_pembuat)
    
    return RedirectResponse(url="/data_pabrik_pembuat/list_data_pabrik_pembuat", status_code=303)

# Endpoint untuk menghapus Data Pabrik Pembuat
@router.post("/delete_data_pabrik_pembuat/{id}")
def delete_data_pabrik_pembuat(
    id: int, 
    session: Session = Depends(get_session)):
    
    db_data_pabrik_pembuat = session.exec(select(DataPabrikPembuat).where(DataPabrikPembuat.id == id)).first()
    
    if db_data_pabrik_pembuat is None:
        raise HTTPException(status_code=404, detail="Data Pabrik Pembuat tidak ditemukan")
    
    session.delete(db_data_pabrik_pembuat)
    session.commit()
    
    return RedirectResponse(url="/data_pabrik_pembuat/list_data_pabrik_pembuat", status_code=303)

@router.get("/list_data_pabrik_pembuat")
def list_data_pabrik_pembuat(
    request: Request, page: int = 1, 
    limit: int = 10, search: str = '', 
    session: Session = Depends(get_session)):

    # Hitung offset berdasarkan halaman yang diminta
    offset = (page - 1) * limit

    # Query untuk mencari data dengan pencarian di nama, alamat, atau telepon
    query = select(DataPabrikPembuat).offset(offset).limit(limit)
    
    condition = (DataPabrikPembuat.name.ilike(f'%{search}%') |
                DataPabrikPembuat.address.ilike(f'%{search}%') |
                DataPabrikPembuat.phone.ilike(f'%{search}%'))
    
    if search:
        query = query.where(condition)
    
    # Ambil data dengan pagination berdarsarkan query
    data = session.exec(query).all()
    
    # Hitung total jumlah data yang sesuai dengan query pencarian
    total_data = len(session.exec(select(DataPabrikPembuat).where(condition)).all())
    
    # Menghitung jumlah halaman
    total_pages = (total_data + limit - 1) // limit  # Membulatkan ke atas
    
    # Mengembalikan data dan pagination
    return templates.TemplateResponse("list_data_pabrik_pembuat.html", {
        "request": request,
        "list_data_pabrik_pembuat": {
            "data": data,
            "page": page,
            "total_pages": total_pages,
            "total_data": total_data
        },
        "search_query": search # Menyertakan query pencarian dalam template
    })
