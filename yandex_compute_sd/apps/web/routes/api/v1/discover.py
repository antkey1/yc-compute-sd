from pydantic import BaseModel
from fastapi import APIRouter, Depends

from yandex_compute_sd.libs.yandex import IAMToken, ComputeCloud
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
    cc = ComputeCloud(
        iam_token=iam.iamToken,
        folder_id=settings.folder_id,
    )
    instances = cc.list_instances()

    response = []
    for instance in instances:
        address = instance.networkInterfaces[0].primaryV4Address.address

        labels = dict(
            yc_id=instance.id,
            yc_folder_id=instance.folderId,
            yc_zone_id=instance.zoneId,
            yc_fqdn=instance.fqdn,
        )

        if instance.name:
            labels['hostname'] = instance.name

        exporter_ports = []
        job_name = None
        if instance.labels:
            for label_key, label_value in instance.labels.items():
                # Get exporters ports
                if all([
                    label_key.startswith('prometheus_'),
                    label_key.endswith('_port'),
                ]):
                    label_value_int = None
                    try:
                        label_value_int = int(label_value)
                    except ValueError:
                        pass

                    if label_value_int in range(0, 65537):
                        exporter_ports.append(label_value)

                # Get job name
                if label_key == 'prometheus_job':
                    job_name = label_value

        if job_name:
            labels['job'] = job_name
        else:
            continue

        # if instance.metadata:
        #     labels.update(instance.metadata)

        # Clean label names (replace "-" by "_")
        keys_to_pop = []
        new_items = dict()
        for k, v in labels.items():
            new_key = k.replace('-', '_')
            new_items[new_key] = v
            keys_to_pop.append(k)
        for key in keys_to_pop:
            labels.pop(key)
        labels.update(new_items)

        # Build targets list
        targets = [
            f'{address}:{exporter_port}' for exporter_port in exporter_ports
        ]

        if targets:
            response.append(
                GetDiscoverResponse(
                    targets=targets,
                    labels=labels,
                )
            )

    return response
