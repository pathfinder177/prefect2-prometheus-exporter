import asyncio
import pytest
from datetime import datetime, timedelta
from exporter import get_metric, get_period, PREFECT_UI_API_URL

@pytest.fixture
def setup_url():
    return "flow_runs/count"

@pytest.fixture
def setup_filter():
    filter = filter = {
            "flow_runs": {
                "state": {
                    "type": {"any_": ["FAILED"]},
                },
            }
    }
    return filter

@pytest.fixture
def setup_metric_name():
    return "metric_1h"

def test_get_period(setup_metric_name):
    test_period = datetime.utcnow() - timedelta(hours=1)
    period = get_period(setup_metric_name)
    assert period == (test_period.strftime("%Y-%m-%dT%H"))

@pytest.mark.asyncio
async def test_get_metric(setup_url, setup_filter):
    url = f"{PREFECT_UI_API_URL}/{setup_url}"
    metric = await get_metric(url, setup_filter)

    assert isinstance(metric, int)
    assert metric >= 0
