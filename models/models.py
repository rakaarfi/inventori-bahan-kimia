from typing import List, Optional, Generic, TypeVar
from sqlmodel import Field, SQLModel, Relationship


# Model untuk Lokasi Bahan Kimia
class LokasiBahanKimia(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    room: str
    location: str
    building: str
    department_name: str
    contact_person: str
    phone: str
    extension: str
    mobile: str
    email: str
    
    """This is a forward reference to the DataBahanKimia model"""
    chemicals: List["DataBahanKimia"] = Relationship(back_populates="location")


# Model untuk Data Pabrik Pembuat
class DataPabrikPembuat(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    address: str
    city: str
    zipcode: str
    province: str
    contact_person: str
    phone: str
    extension: str
    mobile: str
    email: str
    description: str
    
    """
    This establishes a relationship with the DataBahanKimia model
    The 'chemicals' field represents a list of chemical data associated with this factory
    The 'back_populates' attribute links this relationship to the 'factory' attribute in DataBahanKimia
    """
    chemicals: List["DataBahanKimia"] = Relationship(back_populates="factory")


# Model untuk Data Bahan Kimia
class DataBahanKimia(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str 
    trade_name: str
    chemical_formula: str
    characteristic: str
    max_amount: int
    unit: str
    description: str
    id_factory : int = Field(foreign_key="datapabrikpembuat.id")
    id_location : int = Field(foreign_key="lokasibahankimia.id")
    
    factory: Optional[DataPabrikPembuat] = Relationship(back_populates="chemicals")
    location: Optional[LokasiBahanKimia] = Relationship(back_populates="chemicals")
    
    """
    This is a reverse relationship with the DataPenerimaanPenggunaan model
    The 'receipt_usage' field represents a list of receipt and usage data associated with this chemical material
    """
    receipt_usage : List["DataPenerimaanPenggunaan"] = Relationship(back_populates="chemical_material")
    
    
# Model untuk Data Penerimaan Penggunaan
class DataPenerimaanPenggunaan(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: str
    transaction_type: str
    id_chemical_material: int = Field(foreign_key="databahankimia.id")
    amount: float
    description: str
    
    """
    The chemical material associated with this receipt or usage data
    The 'chemical_material' field represents the chemical material that was received or used
    The 'Relationship' attribute links this field to the 'receipt_usage' field in the DataBahanKimia model
    The 'back_populates' attribute means that the DataBahanKimia model has a field called 'receipt_usage' that is a list of DataPenerimaanPenggunaan models
    """
    chemical_material: Optional[DataBahanKimia] = Relationship(back_populates="receipt_usage")

# ======================================================
# API Response Models (Custom Schemas for API Responses)
# ======================================================
    
# Model untuk Report Inventori Bahan Kimia
class InventoriBahanKimiaResponse(SQLModel):
    """
    Represents the response schema for the inventory of chemical materials.
    Used to structure the API response for endpoints requiring inventory details.
    """
    nama_bahan: str
    nama_pabrik: str
    karakteristik: str
    max_amount: int
    unit_bahan: str
    tanggal: str
    jumlah: float
    unit_penerimaan: str


# Model untuk Report Daftar Bahan Kimia
class DaftarBahanKimiaResponse(SQLModel):
    """
    Represents the response schema for the list of chemical materials.
    Used to structure the API response for endpoints listing chemical materials.
    """
    nama_bahan: str
    nama_pabrik: str
    karakteristik: str
    max_amount: int
    unit_bahan: str
    deskripsi: str
    

# Model untuk Report Daftar Data Bahan Kimia
class DaftarDataBahanKimiaResponse(SQLModel):
    """
    Represents the response schema for detailed reports of chemical materials.
    This schema includes detailed information about chemical materials, 
    manufacturers, and storage locations.
    """
    id_bahan_kimia: int
    nama_bahan: str
    karakteristik: str
    max_amount: int
    nama_pabrik: str
    alamat_pabrik: str
    kota_pabrik: str
    kodepos_pabrik: str
    provinsi_pabrik: str
    kontak_pabrik: str
    telepon_pabrik: str
    extension_pabrik: str
    mobile_pabrik: str
    email_pabrik: str
    ruang_lokasi: str
    lokasi_lokasi: str
    bangunan_lokasi: str
    departemen_lokasi: str
    kontak_lokasi: str
    telepon_lokasi: str
    extension_lokasi: str
    mobile_lokasi: str
    email_lokasi: str

# Model untuk Pagination

# T is a TypeVar that acts as a placeholder for a generic type. 
# It allows this model to be used with any type of data, ensuring flexibility.
# For example:
# - If the response contains a list of chemical inventory items, T can be List[InventoriBahanKimiaResponse].
# - If the response contains a list of factories, T can be List[DataPabrikPembuat].
T = TypeVar("T")
class PaginationResponse(SQLModel, Generic[T]):
    """
    A generic response schema for paginated data. 
    Used to standardize the structure of API responses with pagination.
    
    Attributes:
    - data: A generic type (T), which allows this model to handle any type of data (e.g., lists of specific models).
    """
    data: T
    current_page: int
    total_pages: int
