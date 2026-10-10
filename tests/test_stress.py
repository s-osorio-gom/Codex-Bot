"""Randomised stress tests: large batches for the engine, fuzzed conversations for the bot."""

import json
import random

import numpy as np
import pandas as pd
import pytest

from ach_bot import run_bot
from withdrawal_engine import REJECT_REASON_CODES, load_inputs, run_engine

FUZZ_ANSWERS = [
    "", " ", "Bank of America", "Chase", "Texas", "texas", "a", "checking", "ahorros", "x",
    "123456789", "12", "-1", "2500", "1e400", "nan", "si", "no", "ñandú", "🙂", "0" * 500,
]


def test_engine_invariants_on_large_random_batch():
    base, rules, severity = load_inputs()
    rng = np.random.default_rng(0)
    n = 20_000
    big = base.sample(n, replace=True, random_state=0).reset_index(drop=True)
    big["request_id"] = [f"S{i:06d}" for i in range(n)]
    big["amount"] = rng.choice([-5, 0, np.nan, 10, 5000, 1e9], n)
    big["settled_cash_after_request"] = rng.normal(100, 500, n)
    big["snapshot_kyc_status"] = rng.choice(["verified", " VERIFIED ", "pending", None], n)
    big["dest_is_whitelisted"] = rng.choice(["True", "False", None], n)

    out = run_engine(big, rules, severity)
    final = out["final_decisions"]

    assert len(final) == n and final["request_id"].is_unique
    assert out["decision_counts"]["request_count"].sum() == n
    for _, row in final.iterrows():
        if pd.isna(row["triggered_rules"]):
            assert row["decision"] == "APPROVE"
            continue
        top = max(row["triggered_rules"].split(" | "), key=severity.get)
        assert row["reason_code"] == top
        assert (row["decision"] == "REJECT") == (top in REJECT_REASON_CODES)


@pytest.mark.parametrize("seed", range(5))
def test_bot_survives_random_input(tmp_path, seed):
    rnd = random.Random(seed)
    for _ in range(100):
        answers = iter(rnd.choice(FUZZ_ANSWERS) for _ in range(40))

        def scripted(_prompt, answers=answers):
            try:
                return next(answers)
            except StopIteration:
                raise EOFError from None  # the bot must handle running out of input

        session = run_bot(
            rnd.choice(["success", "r01", "r03"]), input_fn=scripted, output_fn=lambda _m: None, output_dir=tmp_path
        )
        assert session.current_state.value == "end"

    for f in tmp_path.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data["account_number"] is None or data["account_number"].startswith("****")
        for turn in data["history"]:
            if turn["speaker"] == "user" and turn["state"] == "ask_account_number" and turn["message"]:
                assert turn["message"].startswith("****")
