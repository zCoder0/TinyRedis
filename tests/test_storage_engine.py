import pytest

from src.config import Settings
from src.engine.storage_engine import StorageEngine


@pytest.fixture
def engine(tmp_path, monkeypatch):
    redis_path = tmp_path / "redis_data.json"
    expiry_path = tmp_path / "expiry_data.json"
    redis_path.touch()
    expiry_path.touch()
    monkeypatch.setattr(Settings, "redis_data_path", str(redis_path))
    monkeypatch.setattr(Settings, "expiry_data_path", str(expiry_path))

    e = StorageEngine()
    e.flushall()
    yield e
    e.shutdown()


def test_set_and_get(engine):
    engine.process(["set", "name", "premraj"])
    assert engine.process(["get", "name"]) == {"type": "string", "value": "premraj"}


def test_set_normalizes_numeric_values(engine):
    engine.process(["set", "age", "25"])
    assert engine.process(["get", "age"]) == {"type": "integer", "value": 25}
    engine.process(["set", "pi", "3.14"])
    assert engine.process(["get", "pi"]) == {"type": "float", "value": 3.14}


def test_get_missing_key_returns_minus_two(engine):
    assert engine.process(["get", "missing"]) == -2


def test_set_with_ex_sets_expiry(engine):
    engine.process(["set", "temp", "val", "ex", "60"])
    assert engine.is_key_exist("temp") is True
    assert engine.ttl("temp") > 0


def test_del_removes_key(engine):
    engine.process(["set", "name", "premraj"])
    assert engine.process(["del", "name"]) is True
    assert engine.process(["get", "name"]) == -2


def test_del_missing_key_returns_minus_two(engine):
    assert engine.process(["del", "missing"]) == -2


def test_exists(engine):
    engine.process(["set", "name", "premraj"])
    assert engine.process(["exists", "name"]) is True
    assert engine.process(["exists", "missing"]) is False


def test_type(engine):
    engine.process(["set", "name", "premraj"])
    engine.process(["set", "count", "5"])
    assert engine.process(["type", "name"]) == "string"
    assert engine.process(["type", "count"]) == "integer"
    assert engine.process(["type", "missing"]) == -2


def test_keys_and_flushall(engine):
    engine.process(["set", "a", "1"])
    engine.process(["set", "b", "2"])
    assert set(engine.process(["keys"])) == {"a", "b"}
    assert engine.process(["flushall"]) is True
    assert set(engine.process(["keys"])) == set()


def test_incr_decr(engine):
    engine.process(["set", "count", "5"])
    assert engine.process(["incr", "count"]) is True
    assert engine.process(["get", "count"]) == {"type": "integer", "value": 6}
    assert engine.process(["decr", "count"]) is True
    assert engine.process(["get", "count"]) == {"type": "integer", "value": 5}


def test_incr_non_integer_returns_minus_two(engine):
    engine.process(["set", "name", "premraj"])
    assert engine.process(["incr", "name"]) == -2
    assert engine.process(["incr", "missing"]) == -2


def test_append(engine):
    engine.process(["set", "name", "premraj"])
    assert engine.process(["append", "name", "raj"]) is True
    assert engine.process(["get", "name"]) == {"type": "string", "value": "premrajraj"}


def test_append_creates_key_if_missing(engine):
    assert engine.process(["append", "new", "hello"]) is True
    assert engine.process(["get", "new"]) == {"type": "string", "value": "hello"}


def test_strlen(engine):
    engine.process(["set", "name", "premraj"])
    assert engine.process(["strlen", "name"]) == 7
    assert engine.process(["strlen", "missing"]) == -2


def test_ttl_missing_and_persistent(engine):
    engine.process(["set", "name", "premraj"])
    assert engine.process(["ttl", "name"]) == -1
    assert engine.process(["ttl", "missing"]) == -2


def test_rpush_and_lrange(engine):
    assert engine.process(["rpush", "tasks", "python", "django", "redis"]) is True
    assert engine.process(["lrange", "tasks", "0", "-1"]) == ["python", "django", "redis"]


def test_lpush_prepends(engine):
    assert engine.process(["rpush", "tasks", "python", "django"]) is True
    assert engine.process(["lpush", "tasks", "first"]) is True
    assert engine.process(["lrange", "tasks", "0", "-1"]) == ["first", "python", "django"]


def test_lpop_rpop(engine):
    assert engine.process(["rpush", "tasks", "a", "b", "c"]) is True
    assert engine.process(["lpop", "tasks"]) == "a"
    assert engine.process(["rpop", "tasks"]) == "c"
    assert engine.process(["lrange", "tasks", "0", "-1"]) == ["b"]


def test_list_wrong_type_returns_error(engine):
    engine.process(["set", "name", "premraj"])
    assert "WRONG_TYPE" in engine.process(["rpush", "name", "x"])
    assert "WRONG_TYPE" in engine.process(["lpop", "name"])


def test_lrange_negative_indices(engine):
    engine.process(["rpush", "tasks", "a", "b", "c", "d"])
    assert engine.process(["lrange", "tasks", "1", "2"]) == ["b", "c"]
    assert engine.process(["lrange", "tasks", "-2", "-1"]) == ["c", "d"]


def test_data_persists_between_instances(tmp_path, monkeypatch):
    redis_path = tmp_path / "redis_data.json"
    expiry_path = tmp_path / "expiry_data.json"
    redis_path.touch()
    expiry_path.touch()
    monkeypatch.setattr(Settings, "redis_data_path", str(redis_path))
    monkeypatch.setattr(Settings, "expiry_data_path", str(expiry_path))

    e1 = StorageEngine()
    e1.process(["set", "name", "premraj"])
    e1.shutdown()

    e2 = StorageEngine()
    assert e2.process(["get", "name"]) == {"type": "string", "value": "premraj"}
    e2.shutdown()
