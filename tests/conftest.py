import pytest

from data.database.mongodb.mongodb import MongoDBManager
from data.database.mongodb.vehicle import VehicleCollection
from data.database.mongodb.session import SessionCollection
from data.database.mongodb.history import HistoryCollection
from data.database.mongodb.comparison import ComparisonCollection


@pytest.fixture(scope="session")
def mongodb():
    db = MongoDBManager()
    db.connect()

    yield db

    db.disconnect()


@pytest.fixture
def vehicle_collection(mongodb):
    return VehicleCollection()


@pytest.fixture
def session_collection(mongodb):
    return SessionCollection()


@pytest.fixture
def history_collection(mongodb):
    return HistoryCollection()


@pytest.fixture
def comparison_collection(mongodb):
    return ComparisonCollection()
# python -m pytest -v