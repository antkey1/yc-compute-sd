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


class OneToOneNat(BaseModel):
    address: str = None


class V4Address(BaseModel):
    address: str = None
    oneToOneNat: OneToOneNat = None


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


class K8sNodeGroup(BaseModel):
    id: str
    name: str
    clusterId: str
    status: str


class ListK8sNodeGroupResponse(BaseModel):
    nodeGroups: list[K8sNodeGroup]
    nextPageToken: str = None


class K8sNodeCloudStatus(BaseModel):
    id: str
    status: str
    statusMessage: str = None


class K8sNode(BaseModel):
    status: str
    cloudStatus: K8sNodeCloudStatus


class ListK8sNodeResponse(BaseModel):
    nodes: list[K8sNode]
    nextPageToken: str = None


class YandexCloudApi:
    def __init__(
            self,
            iam_token: str,
            folder_id: str,
            base_url: str,
            api_version: str,
    ):
        self.iam_token = iam_token
        self.folder_id = folder_id
        self.base_url = base_url
        self.api_version = api_version

        if not all([base_url, api_version]):
            raise Exception('Base url and api version are not specified')

    def build_api_endpoint(self, postfix: str) -> str:
        return f'{self.base_url}/{self.api_version}{postfix}'

    def do_request(self, method: str, postfix: str, params: dict = None):
        url = self.build_api_endpoint(postfix)
        headers = {
            'Authorization': f'Bearer {self.iam_token}',
        }
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
        )
        if not response.ok:
            error_message = f'Request to {url} failed with ' \
                            f'status:{response.status_code} ' \
                            f'and message: {response.text}'
            print(error_message)
            raise Exception(f'Request to {url} failed')

        return response.json()


class ComputeCloud(YandexCloudApi):
    def __init__(self, iam_token: str, folder_id: str,):
        super().__init__(
            iam_token=iam_token,
            folder_id=folder_id,
            base_url='https://compute.api.cloud.yandex.net/compute',
            api_version='v1',
        )

    def list_instances(self, page_token: str = None) -> list[Instance]:
        instances = []
        raw_response = self.do_request(
            method='get',
            postfix='/instances',
            params={
                'folderId': self.folder_id,
                'pageSize': 1000,
                'pageToken': page_token,
            },
        )
        response = ListInstancesResponse(**raw_response)
        instances.extend(response.instances)

        if response.nextPageToken:
            instances.extend(self.list_instances(
                page_token=response.nextPageToken,
            ))

        return instances

    def get_instance(self, instance_id: str) -> Instance:
        raw_response = self.do_request(
            method='get',
            postfix=f'/instances/{instance_id}',
        )
        instance = Instance(**raw_response)
        return instance


class ManagedK8s(YandexCloudApi):
    def __init__(self, iam_token: str, folder_id: str):
        super().__init__(
            iam_token=iam_token,
            folder_id=folder_id,
            base_url='https://mks.api.cloud.yandex.net/managed-kubernetes',
            api_version='v1',
        )

    def get_node_groups(
            self,
            node_group_name: str = None,
            page_token: str = None
    ) -> list[K8sNodeGroup]:
        node_groups = []
        params = {
            'folderId': self.folder_id,
            'pageSize': 1000,
            'pageToken': page_token,
        }

        raw_response = self.do_request(
            method='get',
            postfix='/nodeGroups',
            params=params,
        )
        response = ListK8sNodeGroupResponse(**raw_response)

        for node_group in response.nodeGroups:
            if node_group_name:
                if node_group.name == node_group_name:
                    node_groups.append(node_group)
            else:
                node_groups.append(node_group)

        if response.nextPageToken:
            node_groups.extend(self.get_node_groups(
                page_token=response.nextPageToken,
            ))

        return node_groups

    def list_nodes(
            self, node_group_id: str, page_token: str = None
    ) -> list[K8sNode]:
        nodes = []
        raw_response = self.do_request(
            method='get',
            postfix='/nodes',
            params={
                'nodeGroupId': node_group_id,
                'pageSize': 1000,
                'pageToken': page_token,
            },
        )
        response = ListK8sNodeResponse(**raw_response)
        nodes.extend(response.nodes)

        if response.nextPageToken:
            nodes.extend(self.list_nodes(
                node_group_id=node_group_id,
                page_token=response.nextPageToken,
            ))

        return nodes
