from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from config.database import get_session
from models.models import DataPenerimaanPenggunaan, DataBahanKimia, DataPabrikPembuat, InventoriBahanKimiaResponse, DaftarBahanKimiaResponse, DaftarDataBahanKimiaResponse, PaginationResponse, LokasiBahanKimia
from typing import List
from fastapi.exceptions import HTTPException
from utils.utils import paginate_query, build_pagination_response

router = APIRouter()

# Endpoint untuk membaca daftar Inventori Bahan Kimia
@router.get(
    "/inventori_bahan_kimia/",
    response_model=PaginationResponse[List[InventoriBahanKimiaResponse]]
)
def get_inventori_bahan_kimia(
    page: int = 1, 
    limit: int = 20, 
    search: str = "", 
    session: Session = Depends(get_session)
):
    
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
        .join(DataBahanKimia.factory)
        .join(DataBahanKimia.receipt_usage)
    )
    """
    SELECT 
        COLUMNS
    FROM databahankimia #-> Because the first query is column from databahankimia <-#
    JOIN datapabrikpembuat ON databahankimia.id_factory = datapabrikpembuat.id
    JOIN datapenerimaanpenggunaan ON databahankimia.id = datapenerimaanpenggunaan.id_chemical_material
    """
    
    # Tambahkan filter pencarian
    if search:
        statement = statement.where(
            DataBahanKimia.name.ilike(f"%{search}%") | 
            DataPabrikPembuat.name.ilike(f"%{search}%")
        )
        
    # Paginate query
    raw_data, total_pages = paginate_query(statement, session, page, limit)
    
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

    # Return standardized pagination response
    return build_pagination_response(data, page, total_pages)

# Endpoint untuk membaca daftar Bahan Kimia
@router.get(
    "/daftar_bahan_kimia/",
    response_model=PaginationResponse[List[DaftarBahanKimiaResponse]]
)
def get_daftar_bahan_kimia(
    page: int = 1, 
    limit: int = 20, 
    search: str = "", 
    session: Session = Depends(get_session)
):

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
        .join(DataBahanKimia.factory)
    )

    # Search filter
    if search:
        statement = statement.where(
            DataBahanKimia.name.ilike(f"%{search}%") | 
            DataPabrikPembuat.name.ilike(f"%{search}%")
        )

    # Paginate query
    raw_data, total_pages = paginate_query(statement, session, page, limit)

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

    # Return standardized pagination response
    return build_pagination_response(data, page, total_pages)
    
# Endpoint untuk membaca report Data Bahan Kimia
@router.get(
    "/report_data_bahan_kimia/",
    response_model=PaginationResponse[List[DaftarDataBahanKimiaResponse]]
)
def get_report_data_bahan_kimia(
    page: int = 1, 
    limit: int = 1, 
    search: str = "", 
    session: Session = Depends(get_session)
):

    statement = (
        select(
            DataBahanKimia.name.label("nama_bahan_kimia"),
            DataBahanKimia.characteristic.label("karakteristik"),
            DataBahanKimia.max_amount.label("jumlah_inventori_maksimum"),
            DataPabrikPembuat.name.label("nama_pabrik"),
            DataPabrikPembuat.address.label("alamat_pabrik"),
            DataPabrikPembuat.city.label("kota_pabrik"),
            DataPabrikPembuat.zipcode.label("kodepos_pabrik"),
            DataPabrikPembuat.province.label("provinsi_pabrik"),
            DataPabrikPembuat.contact_person.label("kontak_pabrik"),
            DataPabrikPembuat.phone.label("telepon_pabrik"),
            DataPabrikPembuat.extension.label("extension_pabrik"),
            DataPabrikPembuat.mobile.label("mobile_pabrik"),
            DataPabrikPembuat.email.label("email_pabrik"),
            LokasiBahanKimia.room.label("ruang_lokasi"),
            LokasiBahanKimia.location.label("lokasi_lokasi"),
            LokasiBahanKimia.building.label("bangunan_lokasi"),
            LokasiBahanKimia.department_name.label("departemen_lokasi"),
            LokasiBahanKimia.contact_person.label("kontak_lokasi"),
            LokasiBahanKimia.phone.label("telepon_lokasi"),
            LokasiBahanKimia.extension.label("extension_lokasi"),
            LokasiBahanKimia.mobile.label("mobile_lokasi"),
            LokasiBahanKimia.email.label("email_lokasi"),
        )
        .join(DataBahanKimia.factory)
        .join(DataBahanKimia.location)
    )
    
    if search:
        statement = statement.where(
            DataBahanKimia.name.ilike(f"%{search}%") | 
            DataPabrikPembuat.name.ilike(f"%{search}%") |
            LokasiBahanKimia.room.ilike(f"%{search}%") |
            LokasiBahanKimia.location.ilike(f"%{search}%") |
            LokasiBahanKimia.building.ilike(f"%{search}%") |
            LokasiBahanKimia.department_name.ilike(f"%{search}%")
        )
    
    # Paginate query
    raw_data, total_pages = paginate_query(statement, session, page, limit)
    
    data = [
        {
            "nama_bahan_kimia": row.nama_bahan_kimia,
            "karakteristik": row.karakteristik,
            "jumlah_inventori_maksimum": row.jumlah_inventori_maksimum,
            "nama_pabrik": row.nama_pabrik,
            "alamat_pabrik": row.alamat_pabrik,
            "kota_pabrik": row.kota_pabrik,
            "kodepos_pabrik": row.kodepos_pabrik,
            "provinsi_pabrik": row.provinsi_pabrik,
            "kontak_pabrik": row.kontak_pabrik, 
            "telepon_pabrik": row.telepon_pabrik,
            "extension_pabrik": row.extension_pabrik,
            "mobile_pabrik": row.mobile_pabrik,
            "email_pabrik": row.email_pabrik,
            "ruang_lokasi": row.ruang_lokasi,
            "lokasi_lokasi": row.lokasi_lokasi,
            "bangunan_lokasi": row.bangunan_lokasi,
            "departemen_lokasi": row.departemen_lokasi,
            "kontak_lokasi": row.kontak_lokasi,
            "telepon_lokasi": row.telepon_lokasi,
            "extension_lokasi": row.extension_lokasi,
            "mobile_lokasi": row.mobile_lokasi,
            "email_lokasi": row.email_lokasi,
        }
        for row in raw_data
    ]
    
    if not raw_data:
        return {
            "data": [],
            "total_data": 0,
            "total_pages": 0,
            "current_page": page,
        }
    
    # Return standardized pagination response
    return build_pagination_response(data, page, total_pages)