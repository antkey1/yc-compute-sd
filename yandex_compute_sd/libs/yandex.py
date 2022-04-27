import time
import datetime

import jwt
import requests
from pydantic import BaseModel


class IAMToken(BaseModel):
    iamToken: str
    expiresAt: datetime.datetime

    def __bool__(self):
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        return self.expiresAt > now


def get_yc_iam_token(
        service_account_id: str,
        key_id: str,
        private_key: str,
) -> IAMToken:
    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 360
    }
    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id},
    )

    response = requests.post(
        url='https://iam.api.cloud.yandex.net/iam/v1/tokens',
        json={
            'jwt': encoded_token,
        }
    )
    if not response.ok:
        print(response.text)
        raise Exception('IAM token fetching error')

    response_data = response.json()
    return IAMToken(**response_data)


class V4Address(BaseModel):
    address: str = None


class NetworkInterface(BaseModel):
    primaryV4Address: V4Address = None


class Instance(BaseModel):
    id: str
    folderId: str
    name: str = None
    labels: dict[str, str] = None
    zoneId: str
    metadata: dict[str, str] = None
    fqdn: str
    networkInterfaces: list[NetworkInterface] = None


class ListInstancesResponse(BaseModel):
    instances: list[Instance]
    nextPageToken: str = None


def list_instances(
        iam_token: str,
        folder_id: str,
        page_token: str = None
) -> list[Instance]:
    instances = []

    response = requests.get(
        url='https://compute.api.cloud.yandex.net/compute/v1/instances',
        headers={
            'Authorization': f'Bearer {iam_token}'
        },
        json={
            'folderId': folder_id,
            'pageSize': 1000,
            'pageToken': page_token,
        },
    )
    if not response.ok:
        print(response.text)
        raise Exception('List instances error')

    response = ListInstancesResponse(**response.json())
    instances.extend(response.instances)

    if response.nextPageToken:
        instances.extend(list_instances(
            iam_token=iam_token,
            folder_id=folder_id,
            page_token=response.nextPageToken,
        ))

    return instances
