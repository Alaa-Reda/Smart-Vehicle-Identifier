def test_history_crud(history_collection):

    history = {
        "session_id": "session_test",
        "role": "user",
        "message": "Hello"
    }

    history_id = history_collection.insert(history)

    assert history_id is not None

    result = history_collection.find_by_id(history_id)

    assert result["message"] == "Hello"

    history_collection.delete(history_id)

    assert history_collection.find_by_id(history_id) is None
    # python -m pytest -v