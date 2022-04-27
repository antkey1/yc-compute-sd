FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY yandex_compute_sd yandex_compute_sd

CMD ["uvicorn", "yandex_compute_sd.apps.web:app", "--host", "0.0.0.0", "--port", "80"]