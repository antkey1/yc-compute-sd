Changelog
===

# 0.2.0
* Added new way to explore exporters ports (via yc instance labels)

# 0.1.2
bugfix:
* In k8s node service discovery fix cases, when node hasn't public ip\
* Fix tests (tox<4) issue: https://github.com/tox-dev/tox-pyenv/issues/22

# 0.1.1
* `node_exporter` default port (`9100`) in `GET /api/v1/discover` response

# 0.1.0
* Managed-k8s instances discovery

# 0.0.3
* Fix prometheus labels (instead of values)

# 0.0.2
* Fix prometheus labels (replace dashes with underscores)

# 0.0.1
* MVP