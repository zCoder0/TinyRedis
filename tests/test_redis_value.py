from src.engine.redis_value import RedisValue


def test_string_type():
    assert RedisValue("hello").to_dict() == {"type": "string", "value": "hello"}


def test_integer_type():
    assert RedisValue(25).to_dict() == {"type": "integer", "value": 25}


def test_float_type():
    assert RedisValue(3.14).to_dict() == {"type": "float", "value": 3.14}


def test_list_type():
    assert RedisValue([1, 2, 3]).to_dict() == {"type": "list", "value": [1, 2, 3]}


def test_unknown_type():
    assert RedisValue(None).to_dict() == {"type": "unknown", "value": None}
