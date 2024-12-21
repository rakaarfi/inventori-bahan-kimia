from typing import List, Optional
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
    
    chemicals: List["DataBahanKimia"] = Relationship(back_populates="location")  # Forward Reference

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
    
    chemicals: List["DataBahanKimia"] = Relationship(back_populates="factory")  # Forward Reference


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
    
    receipt_usage : List["DataPenerimaanPenggunaan"] = Relationship(back_populates="chemical_material")
    
    
# Model untuk Data Penerimaan Penggunaan
class DataPenerimaanPenggunaan(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: str
    transaction_type: str
    id_chemical_material: int = Field(foreign_key="databahankimia.id")
    amount: int
    unit: str
    description: str
    
    chemical_material: Optional[DataBahanKimia] = Relationship(back_populates="receipt_usage")
    
class DataPenerimaanPenggunaanCreate(SQLModel):
    transactions: List[dict]
