import time

from src.engine.ratelimit import RateLimit


def test_allows_requests_within_limit():
    rl = RateLimit(MAX_RATELIMIT=3, TIM_WINDOW=10)
    now = time.time()
    assert rl.rateLimit(now) is True
    assert rl.rateLimit(now + 1) is True
    assert rl.rateLimit(now + 2) is True


def test_rejects_requests_over_limit():
    rl = RateLimit(MAX_RATELIMIT=3, TIM_WINDOW=10)
    now = time.time()
    for i in range(3):
        assert rl.rateLimit(now + i) is True
    assert rl.rateLimit(now + 3) is False


def test_window_slides_and_allows_new_requests():
    rl = RateLimit(MAX_RATELIMIT=2, TIM_WINDOW=10)
    now = time.time()
    assert rl.rateLimit(now) is True
    assert rl.rateLimit(now + 1) is True
    assert rl.rateLimit(now + 2) is False
    assert rl.rateLimit(now + 11) is True
