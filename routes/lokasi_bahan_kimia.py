from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session, func

from models.models import LokasiBahanKimia
from config.database import get_session


# Template Jinja untuk rendering HTML
templates = Jinja2Templates(directory="templates")

router = APIRouter()

# Endpoint untuk membuat Lokasi Bahan Kimia baru
@router.post("/create/")
def create_lokasi_bahan_kimia(
    request: LokasiBahanKimia,
    session: Session = Depends(get_session), 
    ):
    
    new_lokasi_bahan_kimia = LokasiBahanKimia(**request.model_dump())
    
    session.add(new_lokasi_bahan_kimia)
    session.commit()
    session.refresh(new_lokasi_bahan_kimia)
    
    # return new_lokasi_bahan_kimia
    return new_lokasi_bahan_kimia
    return RedirectResponse(url="/lokasi-bahan-kimia", status_code=303)
    return RedirectResponse(url="/lokasi_bahan_kimia/list_lokasi_bahan_kimia", status_code=303)


# Endpoint untuk membaca semua Lokasi Bahan Kimia
@router.get("/read/")
def read_lokasi_bahan_kimia(session: Session = Depends(get_session)):
    lokasi_bahan_kimia = session.exec(select(LokasiBahanKimia)).all()
    return lokasi_bahan_kimia

# Endpoint untuk membaca semua Lokasi Bahan Kimia
@router.get("/read/{id}")
def read_lokasi_bahan_kimia_by_id(
    id: int,
    session: Session = Depends(get_session)):
    
    lokasi_bahan_kimia = session.exec(select(LokasiBahanKimia).where(LokasiBahanKimia.id == id)).first()
    if lokasi_bahan_kimia is None:
        raise HTTPException(status_code=404, detail="Lokasi Bahan Kimia tidak ditemukan")
        
    return lokasi_bahan_kimia

# Endpoint untuk memperbarui Lokasi Bahan Kimia
@router.post("/update/{id}")
def update_lokasi_bahan_kimia(
    request: LokasiBahanKimia,
    id: int, 
    session: Session = Depends(get_session),
    ):
    
    db_lokasi_bahan_kimia = session.exec(select(LokasiBahanKimia).where(LokasiBahanKimia.id == id)).first()
    if db_lokasi_bahan_kimia is None:
        raise HTTPException(status_code=404, detail="Lokasi Bahan Kimia tidak ditemukan")
    
    db_lokasi_bahan_kimia.room = request.room
    db_lokasi_bahan_kimia.location = request.location
    db_lokasi_bahan_kimia.building = request.building
    db_lokasi_bahan_kimia.department_name = request.department_name
    db_lokasi_bahan_kimia.contact_person = request.contact_person
    db_lokasi_bahan_kimia.phone = request.phone
    db_lokasi_bahan_kimia.extension = request.extension
    db_lokasi_bahan_kimia.mobile = request.mobile
    db_lokasi_bahan_kimia.email = request.email
    
    session.add(db_lokasi_bahan_kimia)
    session.commit()
    session.refresh(db_lokasi_bahan_kimia)
    
    # return db_lokasi_bahan_kimia
    return RedirectResponse(url="/lokasi_bahan_kimia/list_lokasi_bahan_kimia", status_code=303)


# Endpoint untuk menghapus Lokasi Bahan Kimia
@router.post("/delete/{id}")
def delete_lokasi_bahan_kimia(
    id: int, 
    session: Session = Depends(get_session)):
    
    db_lokasi_bahan_kimia = session.exec(select(LokasiBahanKimia).where(LokasiBahanKimia.id == id)).first()
    
    if db_lokasi_bahan_kimia is None:
        raise HTTPException(status_code=404, detail="Lokasi Bahan Kimia tidak ditemukan")
    
    session.delete(db_lokasi_bahan_kimia)
    session.commit()
    
    return RedirectResponse(url="/lokasi_bahan_kimia/list_lokasi_bahan_kimia", status_code=303)


@router.get("/list_lokasi_bahan_kimia/")
def list_lokasi_bahan_kimia(
    request: Request, page: int = 1, 
    limit: int = 10, search: str = '', 
    session: Session = Depends(get_session)):

    # Hitung offset berdasarkan halaman yang diminta
    offset = (page - 1) * limit

    # Query untuk menampilkan data LokasiBahanKimia
    query = select(LokasiBahanKimia)
    
    # Filter berdasarkan pencarian
    if search:
        condition = (
            LokasiBahanKimia.room.ilike(f'%{search}%') |
            LokasiBahanKimia.location.ilike(f'%{search}%') |
            LokasiBahanKimia.building.ilike(f'%{search}%') |
            LokasiBahanKimia.department_name.ilike(f'%{search}%') |
            LokasiBahanKimia.contact_person.ilike(f'%{search}%') |
            LokasiBahanKimia.phone.ilike(f'%{search}%') |
            LokasiBahanKimia.extension.ilike(f'%{search}%') |
            LokasiBahanKimia.mobile.ilike(f'%{search}%') |
            LokasiBahanKimia.email.ilike(f'%{search}%')
        )
        query = query.where(condition)
        
    # Paginated: Ambil data sesuai offset dan limit
    paginated_query = query.offset(offset).limit(limit)
    
    # Ambil data dengan pagination berdarsarkan query
    data = session.exec(paginated_query).all()
    
    # Hitung total jumlah data yang sesuai dengan query pencarian
    query_count = select(func.count()).select_from(query.subquery())
    result_count = session.exec(query_count)
    total_data = result_count.one()
    
    # Menghitung jumlah halaman
    total_pages = (total_data + limit - 1) // limit  # Membulatkan ke atas


    if 'text/html' in request.headers['Accept']:
        # Mengembalikan data dan pagination
        return templates.TemplateResponse("list_lokasi_bahan_kimia.html", {
            "request": request,
            "list_lokasi_bahan_kimia": {
                "data": data,
                "page": page,
                "total_pages": total_pages
            },
            "search_query": search
        })
    
    return {
        "list_lokasi_bahan_kimia": {
            "data": data,
            "page": page,
            "total_pages": total_pages,
        },
        "search_query": search
    }