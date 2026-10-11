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
    assert validate_amount("1e400") is None
    assert validate_amount("0.001") is None  # rounds to 0.00
    assert validate_amount("2,5") is None  # ambiguous decimal comma, not 25
    assert validate_amount("2,500.00") == 2500.0


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
    answers = [
        "Unknown Bank", "Texas",          # no routing match -> back to bank
        "Bank of America", "Texas",
        "brokerage", "savings",           # invalid then valid account type
        "", "Jane Doe",                   # empty holder
        "12", "987654321",                # too-short account number
        "-5", "2,5", "2500",              # invalid amounts
        "no",
    ]
    session = run_bot("success", input_fn=scripted(answers), output_fn=lambda _m: None, output_dir=tmp_path)

    assert session.account_type == "savings"
    assert session.account_holder_name == "Jane Doe"
    assert session.masked_account_number == "****4321"
    assert session.amount == 2500.0
    bot_messages = [t.message for t in session.history if t.speaker == "bot"]
    for expected in [
        "No encontré una coincidencia",
        "Respuesta no válida",
        "Necesito el nombre del titular",
        "al menos 4 dígitos",
        "El monto debe ser un número positivo",
    ]:
        assert any(expected in m for m in bot_messages), expected
    assert sum("El monto debe ser" in m for m in bot_messages) == 2
    # Declining the confirmation ends the session without submitting.
    assert session.outcome_code is None and session.outcome_message is None


def test_eof_ends_session_and_still_saves_transcript(tmp_path):
    answers = iter(["Bank of America", "Texas"])

    def eof_after_two(_prompt):
        try:
            return next(answers)
        except StopIteration:
            raise EOFError from None

    session = run_bot("success", input_fn=eof_after_two, output_fn=lambda _m: None, output_dir=tmp_path)
    assert session.outcome_code is None
    assert "interrumpida" in session.history[-1].message
    assert len(list(tmp_path.glob("*.json"))) == 1
