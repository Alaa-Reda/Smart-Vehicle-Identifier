def test_comparison_crud(comparison_collection):

    comparison = {
        "session_id": "session_test",
        "vehicle_1": "Toyota",
        "vehicle_2": "Honda",
    }

    comparison_id = comparison_collection.insert(comparison)

    assert comparison_id is not None

    result = comparison_collection.find_by_id(comparison_id)

    assert result["vehicle_1"] == "Toyota"

    comparison_collection.delete(comparison_id)

    assert comparison_collection.find_by_id(comparison_id) is None

    # python -m pytest -v