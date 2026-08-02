def test_connection(mongodb):
    assert mongodb.health_check() is True
    # python -m pytest -v