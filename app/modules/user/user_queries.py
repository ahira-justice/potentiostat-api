from typing import Optional

from app.common.data.queries import BaseQuery


class SearchUsersQuery(BaseQuery):
    username: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
