import json

from ably import AblyRest, AblyException
from fastapi.encoders import jsonable_encoder

from app.common.domain.config import ABLY_API_KEY
from app.common.exceptions.app_exceptions import UpstreamServerException
from app.common.models import Notification


async def notify(channel_name: str, notification: Notification) -> None:
    ably_rest = AblyRest(ABLY_API_KEY)

    payload = json.dumps(jsonable_encoder(notification.payload))

    try:
        channel = ably_rest.channels.get(channel_name)
        await channel.publish(notification.event, payload)
    except AblyException:
        raise UpstreamServerException("An error occurred while attempting to reach ably")
