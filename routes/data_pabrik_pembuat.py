from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session
from typing import List

from utils.utils import paginate_query, build_pagination_response
from models.models import DataPabrikPembuat, PaginationResponse
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


# Endpoint untuk membaca Data Pabrik Pembuat berdasarkan ID
@router.get("/read/{id}")
def read_data_pabrik_pembuat_by_id(
    id: int, 
    session: Session = Depends(get_session)):
    
    data_pabrik_pembuat = session.exec(select(DataPabrikPembuat).where(DataPabrikPembuat.id == id)).first()
    if data_pabrik_pembuat is None:
        raise HTTPException(status_code=404, detail="Data Pabrik Pembuat tidak ditemukan")
        
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
    
    updated_data = request.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_data_pabrik_pembuat, key, value)
    
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


@router.get(
    "/list_data_pabrik_pembuat",
    response_model=PaginationResponse[List[DataPabrikPembuat]]
)
def list_data_pabrik_pembuat(
    request: Request, page: int = 1, 
    limit: int = 10, search: str = '', 
    session: Session = Depends(get_session)):

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
        
    # Paginate query
    data, total_pages = paginate_query(
        statement=query, 
        session=session, 
        limit=limit, 
        page=page,
        )
    
    response = build_pagination_response(data, page, total_pages)
    
    if 'text/html' in request.headers['Accept']:
        # Mengembalikan data dan pagination
        return templates.TemplateResponse("list_data_pabrik_pembuat.html", {
            "request": request,
            "list_data_pabrik_pembuat": {
                "data": data,
                "page": page,
                "total_pages": total_pages        
                },
            "search_query": search
        })
    
    return response
