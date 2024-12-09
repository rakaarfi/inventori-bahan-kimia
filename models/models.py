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
    departement_name: str
    contact_person: str
    phone: str

# Model untuk Data Pabrik Pembuat
class DataPabrikPembuat(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    address: str
    phone: str
