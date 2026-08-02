from data.database.mongodb.vector_index import VectorIndexCollection


def test_vector_index_crud():

    collection = VectorIndexCollection()

    document = {
        "vector_id": 0,
        "vehicle_id": "vehicle_001",
        "embedding_model": "clip-vit-base-patch32",
    }

    document_id = collection.insert(document)

    assert document_id is not None

    result = collection.find_by_vector_id(0)

    assert result is not None
    assert result["vehicle_id"] == "vehicle_001"

    collection.delete(document_id)

    assert collection.find_by_vector_id(0) is None
    # python -m pytest tests/test_vector_index.py -v