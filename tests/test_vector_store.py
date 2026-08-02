import numpy as np

from data.database.faiss.vector_store import VectorStore


def test_vector_store():

    store = VectorStore(dimension=768)

    store.reset()

    vectors = np.random.rand(10, 768).astype(np.float32)

    store.add(vectors)

    assert store.count() == 10

    scores, indices = store.search(vectors[0], top_k=5)

    assert len(scores) == 5
    assert len(indices) == 5

    assert indices[0] == 0


def test_save_load():

    store = VectorStore(dimension=768)

    store.reset()

    vectors = np.random.rand(3, 768).astype(np.float32)

    store.add(vectors)

    store.save()

    new_store = VectorStore(dimension=768)

    assert new_store.count() == 3


def test_dimension():

    store = VectorStore(dimension=768)

    assert store.get_dimension() == 768
    # python -m pytest tests/test_vector_store.py -v