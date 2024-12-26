from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session, func, alias

from models.models import DataBahanKimia, DataPabrikPembuat, LokasiBahanKimia
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
    
    db_data_bahan_kimia.name = request.name
    db_data_bahan_kimia.trade_name = request.trade_name
    db_data_bahan_kimia.chemical_formula = request.chemical_formula
    db_data_bahan_kimia.characteristic = request.characteristic
    db_data_bahan_kimia.max_amount = request.max_amount
    db_data_bahan_kimia.unit = request.unit
    db_data_bahan_kimia.description = request.description
    db_data_bahan_kimia.id_factory = request.id_factory
    db_data_bahan_kimia.id_location = request.id_location
    
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
@router.get("/list_data_bahan_kimia/")
def list_data_bahan_kimia(
    request: Request, page: int = 1, 
    limit: int = 10, search: str = '', 
    session: Session = Depends(get_session)):
    
    # Hitung offset berdasarkan halaman yang diminta
    offset = (page - 1) * limit

    # Query untuk SELECT
    query = select(
        DataPabrikPembuat.name, 
        LokasiBahanKimia.room, 
        DataBahanKimia
    ).join(
        DataPabrikPembuat, DataBahanKimia.id_factory == DataPabrikPembuat.id
    ).join(
        LokasiBahanKimia, DataBahanKimia.id_location == LokasiBahanKimia.id
    )
    
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

    # Pagination: Ambil data sesuai offset dan limit
    paginated_query = query.offset(offset).limit(limit)
    raw_data = session.exec(paginated_query).all()

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
    
    # Hitung total data yang sesuai dengan pencarian
    query_count = select(func.count()).select_from(query.subquery())
    """ 
        SELECT COUNT(*) FROM (subquery)
        atau
        SELECT COUNT(*) FROM (
            SELECT ... FROM ... WHERE ...
        )
        Membuat query untuk menghitung jumlah total baris dari hasil subquery
    """
    result_count = session.exec(query_count)
    """
        Mengeksekusi query COUNT ke database dan mengembalikan hasil sebagai objek ScalarResult.
    """
    total_data = result_count.one()
    """
        Mengambil hasil tunggal (jumlah total baris) dari ScalarResult. 
        Dalam konteks COUNT, hasilnya selalu berupa satu angka.
    """
    
    # Menghitung jumlah halaman
    total_pages = (total_data + limit - 1) // limit  # Membulatkan ke atas

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
                "total_data": total_data
            },
            "search_query": search,
            "lokasi_bahan_kimia": {
                "data": lokasi_bahan_kimia}, 
            "data_pabrik_pembuat": {
                "data": data_pabrik_pembuat},
            "characteristics": characteristics
        })
    
    return {
        "list_data_bahan_kimia": {
            "data": data,
            "page": page,
            "total_pages": total_pages,
        },
        "search_query": search
    }
