import math
from typing import List, Optional

from pydantic import BaseModel

from app.common.generics import T


class PageResponse(BaseModel):
    content: List[T]
    previous_page: Optional[int]
    next_page: Optional[int]
    has_previous: bool
    has_next: bool
    total: int
    pages: int


class Page:
    def __init__(self, content, page, page_size, total):
        super().__init__()

        self.content = content
        self.previous_page = None
        self.next_page = None
        self.has_previous = page > 0
        if self.has_previous:
            self.previous_page = page - 1
        previous_items = page * page_size
        self.has_next = previous_items + len(content) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(math.ceil(total / float(page_size)))


def page_to_page_response(page: Page) -> PageResponse:
    return PageResponse(
        content=page.content,
        previous_page=page.previous_page,
        next_page=page.next_page,
        has_previous=page.has_previous,
        has_next=page.has_next,
        total=page.total,
        pages=page.pages
    )


def paginate(query, page, size):
    if page < 0:
        raise AttributeError("page must be greater than or equal to 0")
    if size <= 0:
        raise AttributeError("size must be greater than 0")

    content = query.limit(size).offset(page * size).all()

    total = query.order_by(None).count()
    return Page(content, page, size, total)
