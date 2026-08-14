from datetime import date, timedelta

from services.token_expiry import TOKEN_TTL_DAYS, evaluate, expiry_dates, hash_token


def test_hash_token_is_stable_and_distinct() -> None:
    assert hash_token("abc") == hash_token("abc")
    assert hash_token("abc") != hash_token("abd")


def test_evaluate_no_token() -> None:
    assert evaluate(None, date(2026, 8, 14), None) == (None, None)


def test_evaluate_first_seen_initializes_state() -> None:
    state, action = evaluate("tok", date(2026, 8, 14), None)
    assert action is None
    assert state["token_hash"] == hash_token("tok")
    assert state["set_at"] == "2026-08-14"


def test_evaluate_rotation_resets_clock() -> None:
    old = {
        "token_hash": hash_token("old"),
        "set_at": "2026-06-01",
        "last_reminder_at": "2026-08-10",
    }
    state, action = evaluate("new", date(2026, 8, 14), old)
    assert action is None
    assert state["token_hash"] == hash_token("new")
    assert state["set_at"] == "2026-08-14"


def test_evaluate_silent_before_warning_window() -> None:
    state = {"token_hash": hash_token("tok"), "set_at": "2026-08-14"}
    _, action = evaluate("tok", date(2026, 9, 1), state)
    assert action is None


def test_evaluate_reminds_inside_window() -> None:
    set_at = date(2026, 8, 14)
    _, warning = expiry_dates(set_at)
    state = {"token_hash": hash_token("tok"), "set_at": set_at.isoformat()}
    _, action = evaluate("tok", warning, state)
    assert action == "remind"


def test_evaluate_remind_deduped_same_day() -> None:
    set_at = date(2026, 8, 14)
    _, warning = expiry_dates(set_at)
    state = {
        "token_hash": hash_token("tok"),
        "set_at": set_at.isoformat(),
        "last_reminder_at": warning.isoformat(),
    }
    _, action = evaluate("tok", warning, state)
    assert action is None


def test_evaluate_reminds_again_next_day() -> None:
    set_at = date(2026, 8, 14)
    _, warning = expiry_dates(set_at)
    state = {
        "token_hash": hash_token("tok"),
        "set_at": set_at.isoformat(),
        "last_reminder_at": warning.isoformat(),
    }
    _, action = evaluate("tok", warning + timedelta(days=1), state)
    assert action == "remind"


def test_evaluate_expired() -> None:
    set_at = date(2026, 8, 14)
    expiry, _ = expiry_dates(set_at)
    state = {"token_hash": hash_token("tok"), "set_at": set_at.isoformat()}
    _, action = evaluate("tok", expiry + timedelta(days=1), state)
    assert action == "expired"


def test_expiry_dates_window_is_7_days() -> None:
    expiry, warning = expiry_dates(date(2026, 8, 14))
    assert (expiry - warning).days == 7
    assert (expiry - date(2026, 8, 14)).days == TOKEN_TTL_DAYS
