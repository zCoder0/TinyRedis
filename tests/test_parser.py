from src.parser.parser import Parser


def test_clean_text_lowercases_and_strips():
    parser = Parser()
    assert parser._clean_text("  SET name premraj  ") == "set name premraj"


def test_split_data_returns_tokens_for_valid_command():
    parser = Parser()
    assert parser.split_data("set name premraj") == ["set", "name", "premraj"]


def test_split_data_returns_empty_for_unknown_command():
    parser = Parser()
    assert parser.split_data("badcmd foo") == []


def test_process_full_pipeline():
    parser = Parser()
    assert parser.process("  SET name premraj ") == ["set", "name", "premraj"]


def test_process_rejects_unknown_command():
    parser = Parser()
    assert parser.process("notacommand foo bar") == []


def test_process_lowercases_command():
    parser = Parser()
    assert parser.process("GET name")[0] == "get"


def test_all_commands_are_whitelisted():
    parser = Parser()
    for cmd in ["set", "get", "del", "keys", "flushall", "exists", "incr",
                "decr", "ttl", "append", "strlen", "type", "persist",
                "rpush", "lpush", "lpop", "rpop", "lrange"]:
        assert parser.split_data(cmd) == [cmd]
