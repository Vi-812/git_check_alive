import asyncio
import pytest
from datetime import datetime
from app.backend.analytic.functions import to_date


@pytest.mark.parametrize('str_date, datetime', [('2023-01-01T12:00:00Z', datetime(2023, 1, 1, 12, 0)),
                                                ('1999-12-31T23:59:59Z', datetime(1999, 12, 31, 23, 59, 59)),
                                                ('2050-06-15T00:01:02Z', datetime(2050, 6, 15, 0, 1, 2)),
                                                ])
def test_to_date(str_date, datetime):
    assert asyncio.run(to_date(str_date)) == datetime


@pytest.mark.parametrize('str_date, error', [('2050-06-15', ValueError),
                                             ('text_message', ValueError),
                                             (12233445, TypeError),
                                             ])
def test_error_to_date(str_date, error):
    with pytest.raises(error):
        asyncio.run(to_date(str_date))
