import asyncio
import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from time import sleep

import aiohttp
import prometheus_client
from prometheus_client import Gauge

EXPORTER_VERSION = os.getenv("EXPORTER_VERSION")
EXPORTER_PORT = int(os.getenv("EXPORTER_PORT"))

PREFECT_UI_API_URL = os.getenv("PREFECT_UI_API_URL")

SCRAPE_PERIOD_IN_SECONDS = 900


# TODO get TERMINAL_STATES from prefect
class Prefect2FlowStates(Enum):
    """Enumeration of state types."""

    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    CRASHED = "CRASHED"


class Prefect2Endpoints(Enum):
    """endpoints to get metrics, see https://docs.prefect.io/latest/api-ref/rest-api-reference"""

    FLOWS_RUNS_COUNT = "flow_runs/count"


METRICS = {
    Prefect2Endpoints.FLOWS_RUNS_COUNT.value: (
        Gauge("prefect2_flows_runs_1h", "Prefect2 flows for 1h", ["state"]),
        Gauge("prefect2_flows_runs_24h", "Prefect2 flows for 24h", ["state"]),
    ),
}


async def get_metric(url, filter):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=filter) as response:
            return await response.json()


async def get_flows_runs(calculated_period, state, url):
    # Define the filter to count the flow runs with the specific state for a period
    filter = {
        "flow_runs": {
            "state": {
                "type": {"any_": [state]},
            },
            "start_time": {"after_": calculated_period},
        }
    }

    return await get_metric(url, filter)


async def set_metric(calculated_period, metric, url):
    for label in Prefect2FlowStates:
        state = label.value

        # did not find a way to break down chain of calls into apart calls
        metric.labels(state).set(await get_flows_runs(calculated_period, state, url))


def get_period(metric_name):
    period = metric_name.split("_")[-1]
    formatted_period = int("".join(num for num in period if num.isdigit()))
    period_ago = datetime.utcnow() - timedelta(hours=formatted_period)
    calculated_period = period_ago.strftime("%Y-%m-%dT%H")

    return calculated_period


def expose_metrics():
    for endpoint, metrics in METRICS.items():
        url = f"{PREFECT_UI_API_URL}/{endpoint}"

        for metric in metrics:
            calculated_period = get_period(metric._name)
            asyncio.run(set_metric(calculated_period, metric, url))


class Exporter:
    def __init__(self, port):
        self.port = port
        self.up = 0

    def run(self):
        prometheus_client.start_http_server(self.port)
        # TODO when could not get metrics, set to 0
        self.up = 1

    @staticmethod
    def setup_logger():
        # Create a logger
        logger = logging.getLogger(__name__)

        # Set the logging level (you can adjust it based on your needs)
        logger.setLevel(logging.INFO)

        # Create a console handler and set the level to INFO
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create a formatter and add it to the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        ch.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(ch)

        return logger

    @staticmethod
    def disable_inner_py_metrics():
        disabled_metrics = [
            prometheus_client.GC_COLLECTOR,
            prometheus_client.PLATFORM_COLLECTOR,
            prometheus_client.PROCESS_COLLECTOR,
        ]

        for d_m in disabled_metrics:
            prometheus_client.REGISTRY.unregister(d_m)


def main():
    exporter = Exporter(port=EXPORTER_PORT)
    exporter.disable_inner_py_metrics()

    logger = exporter.setup_logger()
    logger.info("Exporter starts")
    logger.info(f"Version is {EXPORTER_VERSION}")

    exporter.run()

    while True:
        expose_metrics()
        sleep(SCRAPE_PERIOD_IN_SECONDS)


if __name__ == "__main__":
    main()
