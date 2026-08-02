import numpy as np

from data.database.faiss.faiss_manager import FAISSManager


def test_create_index():

    manager = FAISSManager(dimension=768)

    manager.create_index()

    assert manager.index is not None
    assert manager.count() == 0


def test_add_vectors():

    manager = FAISSManager(dimension=768)

    manager.create_index()

    vectors = np.random.rand(3, 768).astype(np.float32)

    manager.add_vectors(vectors)

    assert manager.count() == 3


def test_search():

    manager = FAISSManager(dimension=768)

    manager.create_index()

    vectors = np.random.rand(5, 768).astype(np.float32)

    manager.add_vectors(vectors)

    scores, indices = manager.search(vectors[0], top_k=3)

    assert len(scores) == 3
    assert len(indices) == 3

    # أول نتيجة لازم تكون نفس الـ vector أو الأقرب ليه
    assert indices[0] == 0
# python -m pytest tests/test_faiss_manager.py -v