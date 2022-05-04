from pydantic import BaseModel
from fastapi import APIRouter, Depends

from yandex_compute_sd.libs.yandex import IAMToken, list_instances
from yandex_compute_sd.apps.web.deps import yc_iam_token
from yandex_compute_sd.apps.settings import settings


router = APIRouter()


class GetDiscoverResponse(BaseModel):
    targets: list[str]
    labels: dict[str, str]


@router.get(
    path='/',
    response_model=list[GetDiscoverResponse],
)
async def get_discover(
        iam: IAMToken = Depends(yc_iam_token),
) -> list[GetDiscoverResponse]:
    instances = list_instances(
        iam_token=iam.iamToken,
        folder_id=settings.folder_id,
    )

    response = []
    for instance in instances:
        address = instance.networkInterfaces[0].primaryV4Address.address
        labels = dict(
            id=instance.id,
            folder_id=instance.folderId,
            zone_id=instance.zoneId,
            fqdn=instance.fqdn,
        )

        if instance.name:
            labels['name'] = instance.name

        if instance.labels:
            labels.update(instance.labels)

        if instance.metadata:
            labels.update(instance.metadata)

        keys_to_pop = []
        new_items = dict()
        for k, v in labels.items():
            new_key = k.replace('-', '_')
            new_items[new_key] = v
            keys_to_pop.append(k)

        for key in keys_to_pop:
            labels.pop(key)

        labels.update(new_items)

        response.append(
            GetDiscoverResponse(
                targets=[address],
                labels=labels,
            )
        )

    return response
