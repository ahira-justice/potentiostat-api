from typing import Optional

from app.common.data.queries import BaseQuery


class SearchClientsQuery(BaseQuery):
    identifier: Optional[str]
