import pytest


@pytest.fixture(autouse=True)
def clean_testing_list():
    with open('testing_list.txt', 'w'):
        pass
