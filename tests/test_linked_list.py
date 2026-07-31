from src.engine.linked_list import DoublyLinkedList


def test_rpush_and_to_list():
    dll = DoublyLinkedList()
    dll.rpush(1)
    dll.rpush(2)
    dll.rpush(3)
    assert dll.to_list() == [1, 2, 3]


def test_lpush_prepends_to_head():
    dll = DoublyLinkedList()
    dll.lpush("a")
    dll.lpush("b")
    assert dll.to_list() == ["b", "a"]


def test_lpop_removes_from_head():
    dll = DoublyLinkedList()
    dll.rpush(1)
    dll.rpush(2)
    assert dll.lpop() == 1
    assert dll.to_list() == [2]


def test_rpop_removes_from_tail():
    dll = DoublyLinkedList()
    dll.rpush(1)
    dll.rpush(2)
    assert dll.rpop() == 2
    assert dll.to_list() == [1]


def test_pop_on_empty_list_returns_none():
    dll = DoublyLinkedList()
    assert dll.lpop() is None
    assert dll.rpop() is None


def test_mixed_push_and_pop():
    dll = DoublyLinkedList()
    dll.rpush("a")
    dll.lpush("b")
    dll.rpush("c")
    assert dll.to_list() == ["b", "a", "c"]
    assert dll.rpop() == "c"
    assert dll.lpop() == "b"
    assert dll.to_list() == ["a"]


def test_fully_popped_list_resets_head_and_tail():
    dll = DoublyLinkedList()
    dll.rpush(1)
    assert dll.lpop() == 1
    assert dll.head is None
    assert dll.tail is None
