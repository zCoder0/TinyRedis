# TinyRedis

A lightweight in-memory key-value store with Redis-like list operations, TTL-based expiry, and JSON persistence — implemented in pure Python (~560 lines, no external dependencies).

## Quick Start

```sh
python main.py
```

```
Text (Eg. SET name age): SET name premraj
Successfully saved!...
True
Text (Eg. SET name age): GET name
{'type': 'string', 'value': 'premraj'}
Text (Eg. SET name age): RPUSH tasks Python Django Redis
Successfully saved!...
True
Text (Eg. SET name age): LRANGE tasks 0 -1
['python', 'django', 'redis']
Text (Eg. SET name age): exit
Bye!
```

## Architecture

```
main.py               REPL loop, input → parser → engine
  |
  |-- Parser          Tokenizes & validates commands (whitelist-based)
  |
  |-- StorageEngine   Command dispatch, data structures, persistence, TTL
  |     |-- DoublyLinkedList   O(1) head/tail push/pop for list ops
  |     |-- RedisValue         Type wrapper (string/integer/float/list)
  |     |-- load / save        JSON file I/O
  |
  |-- RateLimit       Sliding window rate limiter (5 req / 10s)
```

## Commands

### Strings & General

| Command | Example | Behavior |
|---|---|---|
| `SET key value [EX seconds]` | `SET name premraj EX 60` | Store key-value (supports `EX` for TTL) |
| `GET key` | `GET name` | Retrieve value dict `{type, value}` |
| `DEL key` | `DEL name` | Delete key from all stores |
| `KEYS` | `KEYS` | List all keys |
| `FLUSHALL` | `FLUSHALL` | Clear all data |
| `EXISTS key` | `EXISTS name` | Returns `True`/`False` |
| `TYPE key` | `TYPE name` | Returns type string |
| `TTL key` | `TTL name` | Returns remaining seconds, `-1` (persistent), or `-2` (missing) |
| `EXPIRE key seconds` | `EXPIRE name 30` | Set TTL on any existing key |
| `APPEND key value` | `APPEND name raj` | Concatenate to string value |
| `STRLEN key` | `STRLEN name` | Length of string value |

### Numeric

| Command | Example | Behavior |
|---|---|---|
| `INCR key` | `INCR count` | Increment integer by 1 |
| `DECR key` | `DECR count` | Decrement integer by 1 |

### Lists (backed by DoublyLinkedList)

| Command | Example | Behavior |
|---|---|---|
| `RPUSH key value [EX seconds]` | `RPUSH tasks Python EX 10` | Append to tail |
| `LPUSH key value [EX seconds]` | `LPUSH tasks First` | Prepend to head |
| `LPOP key` | `LPOP tasks` | Remove & return from head |
| `RPOP key` | `RPOP tasks` | Remove & return from tail |
| `LRANGE key start stop` | `LRANGE tasks 0 -1` | Returns slice (inclusive, supports negative indices) |

## Internal Design

### List Architecture

List keys maintain **two representations**:

```
redis_data["tasks"]        list_values["tasks"]
    ↓                              ↓
{"type": "list",            DoublyLinkedList
 "value": ["a","b","c"]}    a <-> b <-> c
```

- **At runtime:** All push/pop operations mutate the `DoublyLinkedList` in `list_values` (O(1) head/tail).
- **On save:** `save_all()` converts every DLL to a Python list via `to_list()` before writing JSON.
- **On startup:** Stored arrays are reconstructed into DLLs by iterating and `rpush`-ing each element.

### Persistence

Data is stored in `db/` as JSON files (gitignored).

| File | Format |
|---|---|
| `redis_data.json` | `{key: {"type": "...", "value": ...}}` |
| `expiry_data.json` | `{key: [seconds, start_timestamp]}` |

### Expiry / TTL

A background thread checks expired keys every ~1 second and removes them from all three stores (`redis_data`, `redis_expiry_data`, `list_values`), then silently persists the cleaned state.

## Data Type Detection

Values are auto-coerced: `int` attempt → `float` attempt → `str` fallback.

```
"25"    → 25   (int)
"3.14"  → 3.14 (float)
"hello" → "hello" (str)
```

## Project Structure

```
TinyRedis/
├── main.py                      # Entry point
├── requirements.txt             # No external deps
├── db/                          # Persistence files (gitignored)
│   ├── redis_data.json
│   └── expiry_data.json
└── src/
    ├── config.py                # Settings & db/ auto-creation
    ├── exception.py             # Error formatting utility
    ├── engine/
    │   ├── linked_list.py       # DoublyLinkedList + Node
    │   ├── redis_value.py       # RedisValue type wrapper
    │   ├── storage_engine.py    # Core logic (~370 lines)
    │   └── ratelimit.py         # Sliding window rate limiter
    └── parser/
        ├── parser.py            # Input tokenizer & command validator
        └── load_save_parser.py  # JSON load/save helpers
```
