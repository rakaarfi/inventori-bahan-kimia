# from fastapi import APIRouter, Depends, HTTPException, Form, Request
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from sqlmodel import select, Session
# from typing import List

# from models.models import Departement
# from config.database import get_session


# router = APIRouter()

# # Template Jinja untuk rendering HTML
# templates = Jinja2Templates(directory="templates")

# # Endpoint untuk membuat Departemen baru
# @router.post("/create_departement/")
# def create_departement(session: Session = Depends(get_session), departement: str = Form(...)) -> Departement:
#     new_departemen = Departement(name=departement)
#     session.add(new_departemen)
#     session.commit()
#     session.refresh(new_departemen)
#     return RedirectResponse(url="/departement/departement_list", status_code=303)

# # Endpoint untuk membaca daftar Departemen
# @router.get("/read_departement/", response_model=List[Departement])
# def read_departement(session: Session = Depends(get_session)):
#     names = session.exec(select(Departement)).all()
#     return names

# # Endpoint untuk memperbarui Departemen
# @router.post("/update_departement/{departement}")
# def update_departement(departement: str, session: Session = Depends(get_session), new_name: str = Form(...)):
#     db_departement = session.exec(select(Departement).where(Departement.name == departement)).first()
#     if db_departement is None:
#         raise HTTPException(status_code=404, detail="Departemen tidak ditemukan")
#     db_departement.name = new_name
#     session.add(db_departement)
#     session.commit()
#     session.refresh(db_departement)
#     return RedirectResponse(url="/departement/departement_list", status_code=303)

# # Endpoint untuk menghapus Departemen
# @router.post("/delete_departement/{departement}")
# def delete_departement(departement: str, session: Session = Depends(get_session)):
#     db_departement = session.exec(select(Departement).where(Departement.name == departement)).first()
#     if db_departement is None:
#         raise HTTPException(status_code=404, detail="Departemen tidak ditemukan")
#     session.delete(db_departement)
#     session.commit()
#     return RedirectResponse(url="/departement/departement_list", status_code=303)

# # # Endpoint untuk menampilkan halaman Daftar Departemen
# # @router.get("/departement_list", response_class=HTMLResponse)
# # def departement_list(request: Request, session: Session = Depends(get_session)):
# #     departement_list = session.exec(select(Departement)).all()
# #     return templates.TemplateResponse("departement_list.html", {"request": request, "departement_list": departement_list})

# # Endpoint untuk menampilkan halaman Daftar Departemen
# @router.get("/departement_list", response_class=HTMLResponse)
# def departement_list(
#     request: Request, 
#     page: int = 1,
#     limit: int = 10,
#     session: Session = Depends(get_session)):
    
#     # Hitung offset berdasarkan halaman yang diminta
#     offset = (page - 1) * limit

#     # Ambil data dengan pagination berdasarkan query
#     data = session.exec(select(Departement).offset(offset).limit(limit)).all()

#     # Hitung total jumlah data yang sesuai dengan query pencarian
#     total_data = len(session.exec(select(Departement)).all())

#     # Menghitung jumlah halaman
#     total_pages = (total_data + limit - 1) // limit  # Membulatkan ke atas

#     # Mengembalikan data dan pagination
#     return templates.TemplateResponse("departement_list.html", {
#         "request": request,
#         "departement_list": {
#             'data': data,
#             "page": page,
#             "total_pages": total_pages
#             }
#     })
    