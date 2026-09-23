"""Reporting queries."""
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Book, Order, OrderItem, OrderStatus
from app.schemas import TopBook


def top_books(db: Session, limit: int = 5) -> List[TopBook]:
    """Best-selling books.

    Rules: copies_sold sums quantities over ``paid`` orders only; books with no sales are
    excluded; sorted by copies_sold desc, then title asc; at most ``limit`` rows.
    """
    stmt = (
        select(
            Book.id.label("book_id"),
            Book.title.label("title"),
            func.sum(OrderItem.quantity).label("copies_sold"),
        )
        .join(OrderItem, OrderItem.book_id == Book.id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status == OrderStatus.PAID.value)
        .group_by(Book.id, Book.title)
        .order_by(func.sum(OrderItem.quantity).desc(), Book.title.asc())
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    return [
        TopBook(book_id=r.book_id, title=r.title, copies_sold=r.copies_sold)
        for r in rows
    ]
