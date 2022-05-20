from pydantic import BaseModel
from fastapi import APIRouter, Depends

from yandex_compute_sd.libs.yandex import IAMToken, ComputeCloud, ManagedK8s
from yandex_compute_sd.apps.web.deps import yc_iam_token
from yandex_compute_sd.apps.settings import settings


router = APIRouter()


class NodeNetworkInterface(BaseModel):
    private: str = None
    public: str = None


class K8sNode(BaseModel):
    clusterId: str
    nodeGroupId: str
    nodeGroupName: str
    nodeGroupStatus: str
    nodeStatus: str
    nodeCloudId: str
    nodeCloudStatus: str
    nodeCloudStatusMessage: str = None
    instanceName: str
    networkInterfaces: list[NodeNetworkInterface]


class GetK8sNodesResponse(BaseModel):
    nodes: list[K8sNode]


@router.get(
    path='/instances',
    response_model=GetK8sNodesResponse,
)
def get_instances(
        node_group_name: str = None,
        iam: IAMToken = Depends(yc_iam_token),
) -> GetK8sNodesResponse:
    nodes = []
    cc = ComputeCloud(iam_token=iam.iamToken, folder_id=settings.folder_id)
    k8s = ManagedK8s(iam_token=iam.iamToken, folder_id=settings.folder_id)

    node_groups = k8s.get_node_groups(node_group_name=node_group_name)

    for node_group in node_groups:
        for node in k8s.list_nodes(node_group_id=node_group.id):
            instance = cc.get_instance(instance_id=node.cloudStatus.id)

            network_interfaces = []
            for network_interface in instance.networkInterfaces:
                primary_v4 = network_interface.primaryV4Address
                network_interfaces.append(NodeNetworkInterface(
                    private=primary_v4.address,
                    public=primary_v4.oneToOneNat.address,
                ))

            nodes.append(
                K8sNode(
                    clusterId=node_group.clusterId,
                    nodeGroupId=node_group.id,
                    nodeGroupName=node_group.name,
                    nodeGroupStatus=node_group.status,
                    nodeStatus=node.status,
                    nodeCloudId=node.cloudStatus.id,
                    nodeCloudStatus=node.cloudStatus.status,
                    nodeCloudStatusMessage=node.cloudStatus.statusMessage,
                    instanceName=instance.name,
                    networkInterfaces=network_interfaces,
                )
            )

    return GetK8sNodesResponse(
        nodes=nodes,
    )
