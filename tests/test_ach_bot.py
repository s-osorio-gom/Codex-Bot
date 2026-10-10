import json

import pytest

from ach_bot import run_bot
from ach_services import (
    clean_account_number,
    load_routing_lookup,
    lookup_routing,
    simulate_submission,
    validate_account_type,
    validate_amount,
)
from ach_state import SessionState

HAPPY_PATH = ["Bank of America", "Texas", "checking", "Jane Doe", "123456789", "2500", "si"]


@pytest.fixture(scope="module")
def routing_df():
    return load_routing_lookup()


def scripted(answers):
    it = iter(answers)
    return lambda _prompt: next(it)


def test_routing_numbers_keep_leading_zeros(routing_df):
    assert routing_df["routing_number"].str.len().eq(9).all()
    td = routing_df.loc[routing_df["bank"] == "TD Bank", "routing_number"].item()
    assert td == "067014822"


@pytest.mark.parametrize(
    "bank, state, expected",
    [
        ("Bank of America", "Texas", "111000025"),
        ("  bank of america ", "TEXAS", "111000025"),
        ("Wells Fargo", "California", "121000248"),
        ("U.S. Bank", "California", "121122676"),
        ("Capital One 360", "Ohio", "031176110"),  # nationwide entry
    ],
)
def test_lookup_routing_matches(routing_df, bank, state, expected):
    result = lookup_routing(bank, state, routing_df)
    assert result["found"]
    assert result["routing_number"] == expected


def test_lookup_routing_rejects_unknown_and_too_short_inputs(routing_df):
    assert not lookup_routing("Unknown Bank", "Texas", routing_df)["found"]
    assert not lookup_routing("Chase", "Alaska", routing_df)["found"]
    # Single letters used to match any bank/state by substring.
    assert not lookup_routing("a", "Texas", routing_df)["found"]
    assert not lookup_routing("Bank of America", "a", routing_df)["found"]


def test_validators():
    assert validate_account_type("Ahorros") == "savings"
    assert validate_account_type("CHECKING") == "checking"
    assert validate_account_type("brokerage") is None
    assert clean_account_number("12-34 56") == "123456"
    assert clean_account_number("123") is None
    assert validate_amount("2,500.555") == 2500.56
    assert validate_amount("-1") is None
    assert validate_amount("abc") is None
    assert validate_amount("nan") is None
    assert validate_amount("inf") is None


@pytest.mark.parametrize("scenario, code", [("success", None), ("r01", "R01"), ("r03", "R03")])
def test_simulate_submission(scenario, code):
    session = SessionState(scenario=scenario, amount=10.0)
    assert simulate_submission(scenario, session)["code"] == code


def test_simulate_submission_unknown_scenario():
    with pytest.raises(ValueError):
        simulate_submission("r99", SessionState(amount=1.0))


@pytest.mark.parametrize("scenario, code", [("success", None), ("r01", "R01"), ("r03", "R03")])
def test_full_conversation_writes_masked_transcripts(tmp_path, scenario, code):
    session = run_bot(scenario, input_fn=scripted(HAPPY_PATH), output_fn=lambda _m: None, output_dir=tmp_path)

    assert session.routing_number == "111000025"
    assert session.outcome_code == code

    files = sorted(tmp_path.iterdir())
    assert [f.suffix for f in files] == [".json", ".txt"]
    for f in files:
        assert "123456789" not in f.read_text(encoding="utf-8")

    saved = json.loads(files[0].read_text(encoding="utf-8"))
    assert saved["account_number"] == "****6789"


def test_invalid_answers_are_reprompted(tmp_path):
    answers = ["Unknown Bank", "Texas", *HAPPY_PATH[:2], "brokerage", *HAPPY_PATH[2:5], "-5", "2500", "no"]
    session = run_bot("success", input_fn=scripted(answers), output_fn=lambda _m: None, output_dir=tmp_path)

    assert session.amount == 2500.0
    # Declining the confirmation ends the session without submitting.
    assert session.outcome_code is None and session.outcome_message is None
