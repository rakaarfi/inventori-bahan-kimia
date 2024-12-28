from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session, func
from typing import List

from models.models import DataBahanKimia, DataPabrikPembuat, LokasiBahanKimia, PaginationResponse
from utils.utils import paginate_query, build_pagination_response
from config.database import get_session

router = APIRouter()

# Template Jinja untuk rendering HTML
templates = Jinja2Templates(directory="templates")

# Endpoint untuk membuat Data Bahan Kimia baru
@router.post("/create/")
def create_data_bahan_kimia(
    request: DataBahanKimia, 
    session: Session = Depends(get_session)):
    
    new_data_bahan_kimia = DataBahanKimia(**request.model_dump(exclude_unset=True))
    
    session.add(new_data_bahan_kimia)
    session.commit()
    session.refresh(new_data_bahan_kimia)
    
    return RedirectResponse(url="/data_bahan_kimia", status_code=303)


# Endpoint untuk membaca semua Data Bahan Kimia
@router.get("/read/")
def read_data_bahan_kimia(session: Session = Depends(get_session)):
    data_bahan_kimia = session.exec(select(DataBahanKimia)).all()
    return data_bahan_kimia


# Endpoint untuk membaca Data Bahan Kimia berdasarkan ID
@router.get("/read/{id}")
def read_data_bahan_kimia_by_id(
    id: int, 
    session: Session = Depends(get_session)):
    
    data_bahan_kimia = session.exec(select(DataBahanKimia).where(DataBahanKimia.id == id)).first()
    if data_bahan_kimia is None:
        raise HTTPException(status_code=404, detail="Data Bahan Kimia tidak ditemukan")
    
    factory_name = session.exec(select(DataPabrikPembuat.name).where(DataPabrikPembuat.id == data_bahan_kimia.id_factory)).first()
    location_room = session.exec(select(LokasiBahanKimia.room).where(LokasiBahanKimia.id == data_bahan_kimia.id_location)).first()
        
    return {
        "data_bahan_kimia": data_bahan_kimia,
        "factory_name": factory_name,
        "location_room": location_room,
    }


# Endpoint untuk memperbarui Data Bahan Kimia
@router.post("/update/{id}")
def update_data_bahan_kimia(
    request: DataBahanKimia,
    id: int,
    session: Session = Depends(get_session)):
    
    db_data_bahan_kimia = session.exec(select(DataBahanKimia).where(DataBahanKimia.id == id)).first()
    if db_data_bahan_kimia is None:
        raise HTTPException(status_code=404, detail="Data Bahan Kimia tidak ditemukan")
    
    updated_data = request.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_data_bahan_kimia, key, value)
    
    # Save the updated Data Bahan Kimia
    session.add(db_data_bahan_kimia)
    session.commit()
    session.refresh(db_data_bahan_kimia)
    
    return RedirectResponse(url="/data_bahan_kimia/list_data_bahan_kimia", status_code=303)


# Endpoint untuk menghapus Data Bahan Kimia
@router.post("/delete/{id}")
def delete_data_bahan_kimia(
    id: int, 
    session: Session = Depends(get_session)):
    
    db_data_bahan_kimia = session.exec(select(DataBahanKimia).where(DataBahanKimia.id == id)).first()
    
    if db_data_bahan_kimia is None:
        raise HTTPException(status_code=404, detail="Data Bahan Kimia tidak ditemukan")
    
    session.delete(db_data_bahan_kimia)
    session.commit()
    
    return RedirectResponse(url="/data_bahan_kimia", status_code=303)


# Endpoint untuk membaca daftar Data Bahan Kimia
@router.get(
    "/list_data_bahan_kimia/",
    response_model=PaginationResponse[List[DataBahanKimia]]
)
def list_data_bahan_kimia(
    request: Request, page: int = 1, 
    limit: int = 10, search: str = '', 
    session: Session = Depends(get_session)):

    # Query untuk SELECT
    query = select(
        DataPabrikPembuat.name, 
        LokasiBahanKimia.room, 
        DataBahanKimia
    ).join(DataBahanKimia.factory
    ).join(DataBahanKimia.location)
    
    # Filter berdasarkan pencarian
    if search:
        condition = (
            DataBahanKimia.name.ilike(f'%{search}%') |
            DataBahanKimia.trade_name.ilike(f'%{search}%') |
            DataBahanKimia.chemical_formula.ilike(f'%{search}%') |
            DataBahanKimia.characteristic.ilike(f'%{search}%') |
            DataBahanKimia.max_amount.ilike(f'%{search}%') |
            DataBahanKimia.unit.ilike(f'%{search}%') |
            DataBahanKimia.description.ilike(f'%{search}%') |
            func.lower(DataPabrikPembuat.name).like(f"%{search.lower()}%") |
            func.lower(LokasiBahanKimia.room).like(f"%{search.lower()}%")
        )
        query = query.where(condition)

    # Paginate query
    raw_data, total_pages = paginate_query(
        statement=query, 
        session=session, 
        limit=limit, 
        page=page,
        )
    
    # Format data ke JSON-friendly format
    data = []
    for factory_name, location_room, bahan_kimia in raw_data:
        data.append({
            "id": bahan_kimia.id,
            "name": bahan_kimia.name,
            "trade_name": bahan_kimia.trade_name,
            "chemical_formula": bahan_kimia.chemical_formula,
            "characteristic": bahan_kimia.characteristic,
            "max_amount": bahan_kimia.max_amount,
            "unit": bahan_kimia.unit,
            "description": bahan_kimia.description,
            "id_factory": bahan_kimia.id_factory,
            "id_location": bahan_kimia.id_location,
            "factory_name": factory_name,
            "location_room": location_room,
        })
    
    response = build_pagination_response(data, page, total_pages)

    # Daftar karakteristik
    characteristics = ["Flammable", "Toxic", "Corrosive", "Explosive", "Carcinogen", "Iritating"]

    # Memanggil Data lokasi bahan kimia dan data pabrik pembuat
    lokasi_bahan_kimia = session.exec(select(LokasiBahanKimia)).all()
    data_pabrik_pembuat = session.exec(select(DataPabrikPembuat)).all()
    
    if 'text/html' in request.headers['Accept']:
        return templates.TemplateResponse("list_data_bahan_kimia.html", {
            "request": request, 
            "list_data_bahan_kimia": {
                "data": data,
                "page": page,
                "total_pages": total_pages,
            },
            "search_query": search,
            "lokasi_bahan_kimia": {
                "data": lokasi_bahan_kimia}, 
            "data_pabrik_pembuat": {
                "data": data_pabrik_pembuat},
            "characteristics": characteristics
        })
    
    return response
