import pandas as pd
import pytest

from withdrawal_engine import EJ3_DIR, decide, load_inputs, main, parse_flag, run_engine

SEVERITY = {"KYC_NOT_VERIFIED": 100, "DUPLICATE_REQUEST": 70, "URGENT_RISK_TIER": 35}


def test_decide_approves_when_no_rule_fires():
    assert decide([], SEVERITY)["decision"] == "APPROVE"


def test_decide_highest_severity_wins():
    result = decide(["DUPLICATE_REQUEST", "KYC_NOT_VERIFIED"], SEVERITY)
    assert result["decision"] == "REJECT"
    assert result["reason_code"] == "KYC_NOT_VERIFIED"

    result = decide(["URGENT_RISK_TIER", "DUPLICATE_REQUEST"], SEVERITY)
    assert result["decision"] == "HOLD"
    assert result["reason_code"] == "DUPLICATE_REQUEST"


def test_decide_rejects_unclassified_reason():
    with pytest.raises(ValueError):
        decide(["NEW_RULE"], {"NEW_RULE": 1})


def _request(**overrides):
    row = {
        "request_id": "W1",
        "created_at": "2026-03-06 00:00:00+00:00",
        "client_id": "C1",
        "account_id": "A1",
        "amount": 100.0,
        "currency": "USD",
        "destination_type": "bank",
        "destination_id": "D1",
        "requested_speed": "standard",
        "channel": "app",
        "snapshot_account_status": "active",
        "snapshot_kyc_status": "verified",
        "snapshot_aml_risk_tier": "low",
        "snapshot_available_cash": 1000.0,
        "snapshot_settled_cash": 1000.0,
        "snapshot_unsettled_cash": 0.0,
        "available_cash_after_request": 900.0,
        "settled_cash_after_request": 900.0,
        "dest_is_whitelisted": True,
        "dest_days_since_change": 300.0,
        "dest_changed_recently_flag": False,
        "urgent_risk_flag": False,
        "duplicate_candidate_flag": False,
        "duplicate_pair_request_id": None,
        "mins_from_prev": None,
        "mins_to_next": None,
    }
    row.update(overrides)
    return row


@pytest.mark.parametrize(
    "overrides, decision, reason",
    [
        ({}, "APPROVE", None),
        ({"snapshot_kyc_status": " Pending "}, "REJECT", "KYC_NOT_VERIFIED"),
        ({"snapshot_aml_risk_tier": "high", "dest_is_whitelisted": False}, "REJECT", "UNWHITELISTED_HIGH_AML"),
        ({"snapshot_aml_risk_tier": "high", "dest_is_whitelisted": True}, "APPROVE", None),
        ({"amount": 0}, "REJECT", "INVALID_AMOUNT"),
        ({"settled_cash_after_request": 49.99}, "HOLD", "INSUFFICIENT_SETTLED_AFTER_BUFFER"),
        ({"settled_cash_after_request": 50.0}, "APPROVE", None),
        ({"dest_changed_recently_flag": "True"}, "HOLD", "DEST_CHANGED_RECENTLY"),
        ({"urgent_risk_flag": 1}, "HOLD", "URGENT_RISK_TIER"),
        ({"snapshot_aml_risk_tier": "high", "dest_is_whitelisted": 1}, "APPROVE", None),
        ({"snapshot_aml_risk_tier": "high", "dest_is_whitelisted": None}, "REJECT", "UNWHITELISTED_HIGH_AML"),
    ],
)
def test_rules_on_synthetic_requests(overrides, decision, reason):
    _, rules, severity = load_inputs()
    out = run_engine(pd.DataFrame([_request(**overrides)]), rules, severity)["final_decisions"].iloc[0]
    assert out["decision"] == decision
    assert (pd.isna(out["reason_code"]) and reason is None) or out["reason_code"] == reason


@pytest.mark.parametrize(
    "name", ["final_decisions", "review_queue", "rule_hits", "decision_summary", "decision_counts"]
)
def test_reproduces_published_outputs(tmp_path, name):
    """Regression guard: the module must reproduce the notebook's published results exactly."""
    main(["--output-dir", str(tmp_path)])
    produced = pd.read_csv(tmp_path / f"ejercicio_3_{name}.csv")
    published = pd.read_csv(EJ3_DIR / f"ejercicio_3_{name}.csv")
    pd.testing.assert_frame_equal(produced, published)


def test_review_queue_only_holds_sorted_by_severity():
    queue = run_engine(*load_inputs())["review_queue"]
    assert queue["decision"].eq("HOLD").all()
    assert queue["severity"].is_monotonic_decreasing


def test_empty_batch_returns_empty_outputs():
    base, rules, severity = load_inputs()
    out = run_engine(base.iloc[0:0], rules, severity)
    assert out["final_decisions"].empty
    assert out["review_queue"].empty
    assert out["rule_hits"]["hit_count"].eq(0).all()


def test_parse_flag_accepts_common_encodings_and_rejects_garbage():
    parsed = parse_flag(pd.Series(["True", " false ", "1", "0", 1, 0, "yes", None, ""], name="f", dtype=object))
    assert parsed.tolist()[:7] == [True, False, True, False, True, False, True]
    assert parsed.isna().tolist()[7:] == [True, True]
    with pytest.raises(ValueError, match="maybe"):
        parse_flag(pd.Series(["maybe"], name="f"))
