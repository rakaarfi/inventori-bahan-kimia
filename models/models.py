from sqlmodel import Field, SQLModel

# Model untuk Departemen
class Departement(SQLModel, table=True):
    name: str = Field(primary_key=True)

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
