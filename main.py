from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config.database import create_db_and_tables, drop_table
from routes.departement import router as departement_router
from routes.index import router as index_router
from routes.data_pabrik_pembuat import router as data_pabrik_pembuat_router
from routes.lokasi_bahan_kimia import router as lokasi_bahan_kimia_router


app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Menyajikan file statis
app.mount("/static", StaticFiles(directory="static"), name="static")

# Menjalankan setup database pada startup
@app.on_event("startup")
def on_startup():
    # drop_table()
    create_db_and_tables()

# Menambahkan router ke aplikasi FastAPI
app.include_router(departement_router, prefix="/departement", tags=["Departemen"])

app.include_router(lokasi_bahan_kimia_router, prefix="/lokasi_bahan_kimia", tags=["Lokasi Bahan Kimia"])

app.include_router(data_pabrik_pembuat_router, prefix="/data_pabrik_pembuat", tags=["Data Pabrik Pembuat"])

app.include_router(index_router, prefix="", tags=["Index"])