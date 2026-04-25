from chronolattice.hashing import stable_hash


def test_stable_hash_dict_key_order():
    a = {"b": 2, "a": 1, "nested": {"y": 2, "x": 1}}
    b = {"nested": {"x": 1, "y": 2}, "a": 1, "b": 2}
    assert stable_hash(a) == stable_hash(b)
