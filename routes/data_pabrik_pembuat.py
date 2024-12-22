from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session, func

from models.models import DataPabrikPembuat
from config.database import get_session


# Template Jinja untuk rendering HTML
templates = Jinja2Templates(directory="templates")

router = APIRouter()

# Endpoint untuk membuat Data Pabrik Pembuat baru
@router.post("/create/")
def create_data_pabrik_pembuat(
    request: DataPabrikPembuat,
    session: Session = Depends(get_session), 
    ):
    
    new_data_pabrik_pembuat = DataPabrikPembuat(**request.model_dump())
    
    session.add(new_data_pabrik_pembuat)
    session.commit()
    session.refresh(new_data_pabrik_pembuat)
    
    # return new_data_pabrik_pembuat
    
    return RedirectResponse(url="/data_pabrik_pembuat/list_data_pabrik_pembuat", status_code=303)

# Endpoint untuk membaca semua Data Pabrik Pembuat
@router.get("/read/")
def read_data_pabrik_pembuat(session: Session = Depends(get_session)):
    data_pabrik_pembuat = session.exec(select(DataPabrikPembuat)).all()
    return data_pabrik_pembuat

# Endpoint untuk memperbarui Data Pabrik Pembuat
@router.post("/update/{id}")
def update_data_pabrik_pembuat(
    request: DataPabrikPembuat,
    id: int, 
    session: Session = Depends(get_session), 
    ):
    
    db_data_pabrik_pembuat = session.exec(select(DataPabrikPembuat).where(DataPabrikPembuat.id == id)).first()
    if db_data_pabrik_pembuat is None:
        raise HTTPException(status_code=404, detail="Data Pabrik Pembuat tidak ditemukan")
    
    db_data_pabrik_pembuat.name = request.name
    db_data_pabrik_pembuat.address = request.address
    db_data_pabrik_pembuat.city = request.city
    db_data_pabrik_pembuat.zipcode = request.zipcode
    db_data_pabrik_pembuat.province = request.province
    db_data_pabrik_pembuat.contact_person = request.contact_person
    db_data_pabrik_pembuat.phone = request.phone
    db_data_pabrik_pembuat.extension = request.extension
    db_data_pabrik_pembuat.mobile = request.mobile
    db_data_pabrik_pembuat.email = request.email
    db_data_pabrik_pembuat.description = request.description
    
    session.add(db_data_pabrik_pembuat)
    session.commit()
    session.refresh(db_data_pabrik_pembuat)
    
    return RedirectResponse(url="/data_pabrik_pembuat/list_data_pabrik_pembuat", status_code=303)

# Endpoint untuk menghapus Data Pabrik Pembuat
@router.post("/delete/{id}")
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

    # Query untuk menampilkan data DataPabrikPembuat
    query = select(DataPabrikPembuat)
    
    # Filter berdasarkan pencarian
    if search:
        condition = (
            DataPabrikPembuat.name.ilike(f'%{search}%') |
            DataPabrikPembuat.address.ilike(f'%{search}%') |
            DataPabrikPembuat.city.ilike(f'%{search}%') |
            DataPabrikPembuat.zipcode.ilike(f'%{search}%') |
            DataPabrikPembuat.province.ilike(f'%{search}%') |
            DataPabrikPembuat.contact_person.ilike(f'%{search}%') |
            DataPabrikPembuat.phone.ilike(f'%{search}%') |
            DataPabrikPembuat.extension.ilike(f'%{search}%') |
            DataPabrikPembuat.mobile.ilike(f'%{search}%') |
            DataPabrikPembuat.email.ilike(f'%{search}%') |
            DataPabrikPembuat.description.ilike(f'%{search}%')
        )
        query = query.where(condition)
        
    # Pagination: Ambil data sesuai offset dan limit
    paginated_query = query.offset(offset).limit(limit)
    
    # Ambil data dengan pagination berdarsarkan query
    data = session.exec(paginated_query).all()
    
    # Hitung total jumlah data yang sesuai dengan query pencarian
    query_count = select(func.count()).select_from(query.subquery())
    result_count = session.exec(query_count)
    total_data = result_count.one()
    
    # Menghitung jumlah halaman
    total_pages = (total_data + limit - 1) // limit  # Membulatkan ke atas
    
    # Mengembalikan data dan pagination
    return templates.TemplateResponse("list_data_pabrik_pembuat.html", {
        "request": request,
        "list_data_pabrik_pembuat": {
            "data": data,
            "page": page,
            "total_pages": total_pages        
            },
        "search_query": search # Menyertakan query pencarian dalam template
    })
