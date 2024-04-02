# prefect2-prometheus-exporter
Python module to emit prefect2 metrics that are scraped by prometheus \
[Merged PR in Prometheus](https://github.com/prometheus/docs/pull/2427)

Metrics naming [convention](https://prometheus.io/docs/practices/naming/)

## How to run

### As helm chart(default)
Set prefect2 url in values, then: \
`helm3 upgrade prefect2 . --install --values values.yaml --namespace prefect2`

### As module:
Set env vars:
```
bash
export PREFECT_UI_API_URL=https://prefect2/api
export EXPORTER_PORT=30042
export EXPORTER_VERSION=1.0.0
```

### As docker container
Create new Dockerfile and use my as BASE, e.g.:
```
Dockerfile
FROM pathfinder177/prefect2-prometheus-exporter:tag
ENV PREFECT_UI_API_URL 
ENV EXPORTER_PORT 30042
ENV EXPORTER_VERSION 1.0.0 https://prefect2/api
CMD ["python3", "exporter.py"]
```

## Metrics
It exports on port 30042 by default:
1. Flow runs for 1h and 24h in TERMINAL, FAILED, CANCELLED states

## TBA
1. Exporter status as metric
2. Healthcheck

## Docker image
[Repository](https://hub.docker.com/repository/docker/pathfinder177/prefect2-prometheus-exporter/tags?page=1&ordering=last_updated)
