from fastapi.exceptions import HTTPException
from sqlmodel import select, Session, func

from typing import Tuple, List, Any


def paginate_query(
    statement, 
    session: Session, 
    page: int, 
    limit: int
) -> Tuple[list, int, int]:
    """
    Paginates a SQLAlchemy query and returns a tuple of (paginated data, total data, total pages).

    Args:
        statement (Select): The SQLAlchemy query to be paginated.
        session (Session): The SQLAlchemy session to use.
        page (int): The page number to retrieve.
        limit (int): The limit of items per page.

    Returns:
        Tuple[list, int, int]: A tuple of (paginated data, total data, total pages).
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be greater than 0")
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")

    offset = (page - 1) * limit
    paginated_query = statement.offset(offset).limit(limit)
    raw_data = session.exec(paginated_query).all()

    query_count = select(func.count()).select_from(statement.subquery())
    """ 
        SELECT COUNT(*) FROM (subquery)
        atau
        SELECT COUNT(*) FROM (
            SELECT ... FROM ... WHERE ...
        )
        Membuat query untuk menghitung jumlah total baris dari hasil subquery
    """
    result_count = session.exec(query_count) # Mengeksekusi query COUNT ke database dan mengembalikan hasil sebagai objek ScalarResult.
    total_data = result_count.one() # Mengambil hasil tunggal (jumlah total baris) dari ScalarResult. Dalam konteks COUNT, hasilnya selalu berupa satu angka.

    total_pages = (total_data + limit - 1) // limit
    return raw_data, total_pages


def build_pagination_response(
    data: List[Any], 
    page: int, 
    total_pages: int
) -> dict:
    """
    Build a standardized response for paginated data.

    :param data: Paginated data list.
    :param page: Current page number.
    :param total_pages: Total number of pages.
    :return: Pagination response dictionary.
    """
    return {
        "data": data,
        "current_page": page,
        "total_pages": total_pages,
    }
