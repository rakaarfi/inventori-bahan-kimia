from sqlmodel import create_engine, SQLModel, Session
from models.models import DataPabrikPembuat, LokasiBahanKimia, DataBahanKimia, DataPenerimaanPenggunaan

# Konfigurasi database SQLite
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

# Fungsi untuk menghapus tabel
def drop_table():
    # DataPabrikPembuat.__table__.drop(bind=engine)
    # LokasiBahanKimia.__table__.drop(bind=engine)
    # DataBahanKimia.__table__.drop(bind=engine)
    DataPenerimaanPenggunaan.__table__.drop(bind=engine)
    print("Tabel telah dihapus.")

# Fungsi untuk membuat database dan tabel
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency untuk session
def get_session():
    with Session(engine) as session:
        yield session