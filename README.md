Yandex Cloud Compute Instance Prometheus service discovery
===

Web service for discovery of computer instances in Yandex.Сloud

Environment variables:
* `YC_COMPUTE_SD_FOLDER_ID` - Folder ID
* `YC_COMPUTE_SD_SERVICE_ACCOUNT_ID` - Service account ID with `compute.viewer` role
* `YC_COMPUTE_SD_KEY_ID` - Key ID in service account
* `YC_COMPUTE_SD_PRIVATE_KEY` - Private part of key

# Setup instances for service discovery

Add following labels to yandex.cloud instances:
* `prometheus_*_port=*`: e.g. `prometheus_node_exporter_port=9100`
* `prometheus_job=*`: e.g. `prometheus_job=my_awesome_service`

Without at least one `prometheus_*_port` label and `prometheus_job` label targets will be not discovered by service

Example response (`GET /api/v1/discover`) with following labels on yc instance:
* `prometheus_node_exporter_port=9100`
* `prometheus_awesome_service_exporter_port=8080`
* `prometheus_job=awesome-service`
```json
[
  {
    "targets": [
      "127.0.0.1:9100",
      "127.0.0.1:8080"
    ],
    "labels": {
      "yc_id": "1234567890",
      "yc_folder_id": "1234567890",
      "yc_zone_id": "ru-central1-a",
      "yc_fqdn": "awesome-service-app-1.ru-central1.internal",
      "hostname": "awesome-service-app-1",
      "job": "awesome-service"
    }
  }
]
```
