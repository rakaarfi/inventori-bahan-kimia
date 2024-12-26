from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from config.database import get_session
from models.models import DataPenerimaanPenggunaan, DataBahanKimia, DataPabrikPembuat, InventoriBahanKimiaResponse, DaftarBahanKimiaResponse, PaginationResponse
from typing import List
from fastapi.exceptions import HTTPException

router = APIRouter()

@router.get(
    "/inventori_bahan_kimia/",
    response_model=PaginationResponse[List[InventoriBahanKimiaResponse]]
)
def get_inventori_bahan_kimia(
    page: int = 1, 
    limit: int = 10, 
    search: str = "", 
    session: Session = Depends(get_session)
):
    
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be greater than 0")
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")
    
    # Hitung offset berdasarkan halaman yang diminta
    offset = (page - 1) * limit
    
    statement = (
        select(
            DataBahanKimia.name.label("nama_bahan"),
            DataPabrikPembuat.name.label("nama_pabrik"),
            DataBahanKimia.characteristic.label("karakteristik"),
            DataBahanKimia.max_amount.label("max_amount"),
            DataBahanKimia.unit.label("unit_bahan"),
            DataPenerimaanPenggunaan.date.label("tanggal"),
            DataPenerimaanPenggunaan.amount.label("jumlah"),
            DataPenerimaanPenggunaan.unit.label("unit_penerimaan"),
        )
        .join(DataPenerimaanPenggunaan, DataPenerimaanPenggunaan.id_chemical_material == DataBahanKimia.id)
        .join(DataPabrikPembuat, DataBahanKimia.id_factory == DataPabrikPembuat.id)
    )
    
    # Tambahkan filter pencarian
    if search:
        statement = statement.where(
            DataBahanKimia.name.ilike(f"%{search}%") | 
            DataPabrikPembuat.name.ilike(f"%{search}%")
        )
        
    # Pagination: Ambil data dengan limit dan offset
    paginated_query = statement.offset(offset).limit(limit)
    raw_data = session.exec(paginated_query).all()

    # Hitung total data
    query_count = select(func.count()).select_from(statement.subquery())
    total_data = session.exec(query_count).one()

    # Hitung jumlah halaman
    total_pages = (total_data + limit - 1) // limit
    
    data = [
        {
            "nama_bahan": row.nama_bahan,
            "nama_pabrik": row.nama_pabrik,
            "karakteristik": row.karakteristik,
            "max_amount": row.max_amount,
            "unit_bahan": row.unit_bahan,
            "tanggal": row.tanggal,
            "jumlah": row.jumlah,
            "unit_penerimaan": row.unit_penerimaan,
        }
        for row in raw_data
    ]
    
    if not raw_data:
        return {
            "data": [],
            "current_page": page,
            "total_pages": 0,
            "total_data": 0,
        }

    return {
        "data": data,
        "current_page": page,
        "total_pages": total_pages,
        "total_data": total_data,
    }

@router.get(
    "/daftar_bahan_kimia/",
    response_model=PaginationResponse[List[DaftarBahanKimiaResponse]]
)
def get_daftar_bahan_kimia(
    page: int = 1, 
    limit: int = 10, 
    search: str = "", 
    session: Session = Depends(get_session)
):
    
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be greater than 0")
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")
    
    # Hitung offset berdasarkan halaman yang diminta
    offset = (page - 1) * limit

    # Query utama
    statement = (
        select(
            DataBahanKimia.name.label("nama_bahan"),
            DataPabrikPembuat.name.label("nama_pabrik"),
            DataBahanKimia.characteristic.label("karakteristik"),
            DataBahanKimia.max_amount.label("max_amount"),
            DataBahanKimia.unit.label("unit_bahan"),
            DataBahanKimia.description.label("deskripsi")
        )
        .join(DataPabrikPembuat, DataBahanKimia.id_factory == DataPabrikPembuat.id)
    )

    # Search filter
    if search:
        statement = statement.where(
            DataBahanKimia.name.ilike(f"%{search}%") | 
            DataPabrikPembuat.name.ilike(f"%{search}%")
        )

    # Pagination
    paginated_query = statement.offset(offset).limit(limit)
    raw_data = session.exec(paginated_query).all()

    # Count total data
    query_count = select(func.count()).select_from(statement.subquery())
    total_data = session.exec(query_count).one()

    # Count total pages
    total_pages = (total_data + limit - 1) // limit

    data = [
        {
            "nama_bahan": row.nama_bahan,
            "nama_pabrik": row.nama_pabrik,
            "karakteristik": row.karakteristik,
            "max_amount": row.max_amount,
            "unit_bahan": row.unit_bahan,
            "deskripsi": row.deskripsi,
        }
        for row in raw_data
    ]
    
    if not raw_data:
        return {
            "data": [],
            "current_page": page,
            "total_pages": 0,
            "total_data": 0,
        }

    return {
        "data": data,
        "current_page": page,
        "total_pages": total_pages,
        "total_data": total_data,
    }