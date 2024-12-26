from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session, func, SQLModel

from typing import List, Optional

from models.models import DataPenerimaanPenggunaan, DataBahanKimia
from config.database import get_session

# Define a new model to allow the creation of multiple entries in a single API request
class DataPenerimaanPenggunaanBase(SQLModel):
    date: str
    transaction_type: str
    id_chemical_material: int
    amount: int
    unit: str
    description: Optional[str] = None

class DataPenerimaanPenggunaanCreate(SQLModel):
    transactions: List[DataPenerimaanPenggunaanBase]


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
        # Ambil data bahan kimia terkait
        chemical = session.exec(
            select(DataBahanKimia).where(DataBahanKimia.id == transaction.id_chemical_material)
        ).first()

        if not chemical:
            raise HTTPException(
                status_code=404,
                detail=f"Chemical material with ID {transaction.id_chemical_material} not found"
            )

        # Panggil fungsi get_total_inventory untuk mendapatkan total penerimaan dan penggunaan
        inventory = get_total_inventory(transaction.id_chemical_material, session)
        total_received = inventory["total_received"]
        total_used = inventory["total_used"]

        # Hitung total inventori saat ini
        current_inventory = total_received - total_used

        # Validasi apakah transaksi baru melebihi max_amount
        if transaction.transaction_type == "Penerimaan":
            if current_inventory + transaction.amount > chemical.max_amount:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Total amount after this transaction ({current_inventory + transaction.amount}) "
                        f"exceeds max amount {chemical.max_amount} for chemical {chemical.name}"
                    )
                )

        # Tambahkan data ke database jika validasi berhasil
        new_data = DataPenerimaanPenggunaan(**transaction.dict())
        session.add(new_data)
        created_data.append(new_data)

    session.commit()
    return created_data

    return RedirectResponse(url="/data_penerimaan_penggunaan/list_data_penerimaan_penggunaan", status_code=303)

@router.get("/total/{id_chemical_material}")
def get_total_inventory(
    id_chemical_material: int, 
    session: Session = Depends(get_session)
):
    total_received = (
        session.exec(
            select(func.sum(DataPenerimaanPenggunaan.amount))
            .where(DataPenerimaanPenggunaan.id_chemical_material == id_chemical_material)
            .where(DataPenerimaanPenggunaan.transaction_type == "Penerimaan")
        ).one_or_none()
        or 0
    )
    total_used = (
        session.exec(
            select(func.sum(DataPenerimaanPenggunaan.amount))
            .where(DataPenerimaanPenggunaan.id_chemical_material == id_chemical_material)
            .where(DataPenerimaanPenggunaan.transaction_type == "Penggunaan")
        ).one_or_none()
        or 0
    )
    return {"total_received": total_received, "total_used": total_used}

# Endpoint untuk membaca Data Penerimaan Penggunaan
@router.get("/read/")
def read_data_penerimaan_penggunaan(session: Session = Depends(get_session)):
    data_penerimaan_penggunaan = session.exec(select(DataPenerimaanPenggunaan)).all()
    return data_penerimaan_penggunaan

# Endpoint untuk membaca Data Penerimaan Penggunaan berdasarkan ID
@router.get("/read/{id}")
def read_data_penerimaan_penggunaan_by_id(
    id: int, 
    session: Session = Depends(get_session)):
    
    data_penerimaan_penggunaan = session.exec(select(DataPenerimaanPenggunaan).where(DataPenerimaanPenggunaan.id == id)).first()
    if data_penerimaan_penggunaan is None:
        raise HTTPException(status_code=404, detail="Data Penerimaan Penggunaan tidak ditemukan")
    
    chemical_material_name = session.exec(select(DataBahanKimia.name).where(DataBahanKimia.id == data_penerimaan_penggunaan.id_chemical_material)).first()
    
    return {
        "data_penerimaan_penggunaan": data_penerimaan_penggunaan,
        "chemical_material_name": chemical_material_name,
    }

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
    paginated_query = query.offset(offset).limit(limit)
    raw_data = session.exec(paginated_query).all()
    
    # Format data ke JSON-friendly format
    data = []
    for chemical_material_name, penerimaan_penggunaan in raw_data:
        data.append({
            "id": penerimaan_penggunaan.id,
            "date": penerimaan_penggunaan.date,
            "transaction_type": penerimaan_penggunaan.transaction_type,
            "id_chemical_material": penerimaan_penggunaan.id_chemical_material,
            "amount": penerimaan_penggunaan.amount,
            "unit": penerimaan_penggunaan.unit,
            "description": penerimaan_penggunaan.description,
            "name": chemical_material_name,
        })
    
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
    
    if 'text/html' in request.headers['Accept']:
        return templates.TemplateResponse("list_data_penerimaan_penggunaan.html",{
            "request": request,
            "list_data_penerimaan_penggunaan": {
                "data": data,
                "page": page,
                "total_pages": total_pages,
            },
            "search_query": search,
            "data_bahan_kimia": {
                "data": data_bahan_kimia},
            "transactions_type": transactions_type
        })
        
    return {
        "list_data_penerimaan_penggunaan": {
            "data": data,
            "page": page,
            "total_pages": total_pages,
        },
        "search_query": search
    }