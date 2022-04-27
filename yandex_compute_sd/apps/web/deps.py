from yandex_compute_sd.apps.settings import settings
from yandex_compute_sd.libs.yandex import get_yc_iam_token


IAM = None


async def yc_iam_token():
    global IAM

    if not IAM:
        IAM = get_yc_iam_token(
            service_account_id=settings.service_account_id,
            key_id=settings.key_id,
            private_key=settings.private_key,
        )

    yield IAM
