from typing import Optional

from app.common.data.queries import BaseQuery


class SearchExperimentsQuery(BaseQuery):
    experiment_status: Optional[str]
    username: Optional[str]
    client_id: Optional[str]
