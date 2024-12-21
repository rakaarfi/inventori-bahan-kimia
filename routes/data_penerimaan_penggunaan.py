from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session, func, SQLModel

from typing import List, Optional

from models.models import DataPenerimaanPenggunaan, DataBahanKimia, DataPenerimaanPenggunaanCreate
from config.database import get_session


# Template Jinja untuk rendering HTML
templates = Jinja2Templates(directory="templates")

router = APIRouter()

# Endpoint untuk membuat Data Penerimaan Penggunaan baru
@router.post("/create/")
def create_data_penerimaan_penggunaan(
    request: DataPenerimaanPenggunaanCreate,
    session: Session = Depends(get_session)
    ):
    
    created_data = []
    for transaction in request.transactions:
        new_data = DataPenerimaanPenggunaan(**transaction)
        session.add(new_data)
        created_data.append(new_data)
    
    session.commit()
        
    return created_data
    
    return RedirectResponse(url="/data_penerimaan_penggunaan/list_data_penerimaan_penggunaan", status_code=303)

# Endpoint untuk membaca Data Penerimaan Penggunaan
@router.get("/read/")
def read_data_penerimaan_penggunaan(session: Session = Depends(get_session)):
    data_penerimaan_penggunaan = session.exec(select(DataPenerimaanPenggunaan)).all()
    return data_penerimaan_penggunaan

# Endpoint untuk mengupdate Data Penerimaan Penggunaan    
@router.post("/update/{id}")
def update_data_penerimaan_penggunaan(
    request: DataPenerimaanPenggunaan,
    id: int, 
    session: Session = Depends(get_session), 
    ):
    
    db_data_penerimaan_penggunaan = session.exec(select(DataPenerimaanPenggunaan).where(DataPenerimaanPenggunaan.id == id)).first()
    if db_data_penerimaan_penggunaan is None:
        raise HTTPException(status_code=404, detail="Data Penerimaan Penggunaan tidak ditemukan")
    
    db_data_penerimaan_penggunaan.date = request.date
    db_data_penerimaan_penggunaan.transaction_type = request.transaction_type
    db_data_penerimaan_penggunaan.id_chemical_material = request.id_chemical_material
    db_data_penerimaan_penggunaan.amount = request.amount
    db_data_penerimaan_penggunaan.unit = request.unit
    db_data_penerimaan_penggunaan.description = request.description
    
    session.add(db_data_penerimaan_penggunaan)
    session.commit()
    session.refresh(db_data_penerimaan_penggunaan)
    
    return RedirectResponse(url="/data_penerimaan_penggunaan/list_data_penerimaan_penggunaan", status_code=303
)
    
# Endpoint untuk menghapus Data Penerimaan Penggunaan
@router.post("/delete/{id}")
def delete_data_penerimaan_penggunaan(
    id: int, 
    session: Session = Depends(get_session)):
    
    db_data_penerimaan_penggunaan = session.exec(select(DataPenerimaanPenggunaan).where(DataPenerimaanPenggunaan.id == id)).first()
    
    if db_data_penerimaan_penggunaan is None:
        raise HTTPException(status_code=404, detail="Data Penerimaan Penggunaan tidak ditemukan")
    
    session.delete(db_data_penerimaan_penggunaan)
    session.commit()
    
    return RedirectResponse(url="/data_penerimaan_penggunaan/list_data_penerimaan_penggunaan", status_code=303)

# Endpoint untuk menampilkan halaman Daftar Data Penerimaan Penggunaan
@router.get("/list_data_penerimaan_penggunaan")
def list_data_penerimaan_penggunaan(
    request: Request, page: int = 1, 
    limit: int = 10, search: str = '', 
    session: Session = Depends(get_session)):
    
    # Hitung offset berdasarkan halaman yang diminta
    offset = (page - 1) * limit
    
    # Query untuk mencari data dengan pencarian di nama, alamat, atau telepon
    query = select(
        DataBahanKimia.name, 
        DataPenerimaanPenggunaan
        ).join(
            DataBahanKimia, DataBahanKimia.id == DataPenerimaanPenggunaan.id_chemical_material)
    
    # Filter berdasarkan pencarian
    if search:
        condition = (
            DataPenerimaanPenggunaan.date.ilike(f'%{search}%') |
            DataPenerimaanPenggunaan.transaction_type.ilike(f'%{search}%') |
            DataPenerimaanPenggunaan.id_chemical_material.ilike(f'%{search}%') |
            DataPenerimaanPenggunaan.amount.ilike(f'%{search}%') |
            DataPenerimaanPenggunaan.unit.ilike(f'%{search}%') |
            DataPenerimaanPenggunaan.description.ilike(f'%{search}%')
        )
        
        query = query.where(condition)
    
    # Pagination: Ambil data dengan limit dan offset
    query = query.offset(offset).limit(limit)
    data = session.exec(query).all()
    
    # Hitung total data yang sesuai dengan pencarian
    query_count = select(func.count()).select_from(query.subquery())
    result_count = session.exec(query_count)
    total_data = result_count.one()
    
    # Hitung jumlah halaman
    total_pages = (total_data + limit - 1) // limit
    
    # Jenis Transaksi
    transactions_type = ["Penerimaan", "Penggunaan"]
    
    # Memanggil Data Bahan Kimia
    data_bahan_kimia = session.exec(select(DataBahanKimia)).all()
    
    return templates.TemplateResponse("list_data_penerimaan_penggunaan.html",{
            "request": request,
            "list_data_penerimaan_penggunaan": {
                "data": data,
                "page": page,
                "total_pages": total_pages,
                "total_data": total_data
            },
            "data_bahan_kimia": {
                "data": data_bahan_kimia},
            "transactions_type": transactions_type
        })