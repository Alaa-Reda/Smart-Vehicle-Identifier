def test_session_crud(session_collection):

    session = {
        "status": "active"
    }

    session_id = session_collection.insert(session)

    assert session_id is not None

    result = session_collection.find_by_id(session_id)

    assert result["status"] == "active"

    session_collection.delete(session_id)

    assert session_collection.find_by_id(session_id) is None

    # python -m pytest -v