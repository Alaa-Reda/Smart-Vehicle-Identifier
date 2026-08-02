def test_vehicle_crud(vehicle_collection):

    vehicle = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "White",
        "confidence": 0.99,
    }

    vehicle_id = vehicle_collection.insert(vehicle)

    assert vehicle_id is not None

    result = vehicle_collection.find_by_id(vehicle_id)

    assert result is not None
    assert result["brand"] == "Toyota"
    assert result["model"] == "Corolla"

    vehicle_collection.delete(vehicle_id)

    assert vehicle_collection.find_by_id(vehicle_id) is None

    # python -m pytest -v