from app.common import utils
from app.common.data.models import Client
from app.modules.client.client_dtos import ClientResponse, ClientCreateRequest


def client_to_client_response(client: Client) -> ClientResponse:
    result = ClientResponse(
        id=client.id,
        identifier=client.identifier
    )

    return result


def client_create_to_client(request: ClientCreateRequest) -> Client:
    secret_hash, secret_salt = utils.generate_hash_and_salt(request.secret)

    result = Client(
        identifier=request.identifier,
        secret_hash=secret_hash,
        secret_salt=secret_salt
    )

    return result
