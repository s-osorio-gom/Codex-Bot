"""Rule-based decision engine for withdrawal requests (Ejercicio 3).

Classifies each request as APPROVE, HOLD or REJECT. When several rules fire,
the one with the highest severity decides. The logic is the same as the one in
notebooks/Ejercicio3.ipynb, extracted so it can be run and tested without
Jupyter.

Usage:
    python src/withdrawal_engine.py --output-dir /tmp/ejercicio_3
"""

import argparse
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EJ3_DIR = PROJECT_ROOT / "outputs" / "ejercicio_3"

REJECT_REASON_CODES = {
    "KYC_NOT_VERIFIED",
    "ACCOUNT_NOT_ACTIVE",
    "UNWHITELISTED_HIGH_AML",
    "INVALID_AMOUNT",
}

HOLD_REASON_CODES = {
    "DUPLICATE_REQUEST",
    "INSUFFICIENT_SETTLED_AFTER_BUFFER",
    "INSUFFICIENT_AVAILABLE_AFTER_BUFFER",
    "DEST_CHANGED_RECENTLY",
    "URGENT_RISK_TIER",
}

DATETIME_COLS = ["created_at", "snapshot_as_of", "dest_last_changed_at", "next_expected_settle_at"]

BOOL_COLS = [
    "dest_is_whitelisted",
    "snapshot_margin_enabled",
    "dest_changed_recently_flag",
    "urgent_risk_flag",
    "duplicate_candidate_flag",
]

NUMERIC_COLS = [
    "amount",
    "snapshot_available_cash",
    "snapshot_settled_cash",
    "snapshot_unsettled_cash",
    "pending_items_count",
    "pending_amount_net",
    "pending_amount_abs",
    "available_cash_after_request",
    "settled_cash_after_request",
    "dest_days_since_change",
    "mins_from_prev",
    "mins_to_next",
]

OUTPUT_COLS = [
    "request_id",
    "decision",
    "reason_code",
    "severity",
    "created_at",
    "client_id",
    "account_id",
    "amount",
    "currency",
    "destination_type",
    "destination_id",
    "requested_speed",
    "channel",
    "snapshot_account_status",
    "snapshot_kyc_status",
    "snapshot_aml_risk_tier",
    "snapshot_available_cash",
    "snapshot_settled_cash",
    "snapshot_unsettled_cash",
    "available_cash_after_request",
    "settled_cash_after_request",
    "dest_is_whitelisted",
    "dest_days_since_change",
    "dest_changed_recently_flag",
    "urgent_risk_flag",
    "duplicate_candidate_flag",
    "duplicate_pair_request_id",
    "mins_from_prev",
    "mins_to_next",
    "triggered_rules",
]

DECISION_ORDER = {"REJECT": 0, "HOLD": 1, "APPROVE": 2}


def normalize_types(base: pd.DataFrame) -> pd.DataFrame:
    base = base.copy()
    for col in DATETIME_COLS:
        if col in base.columns:
            base[col] = pd.to_datetime(base[col], errors="coerce", utc=True)
    for col in BOOL_COLS:
        # Text flags ("True"/"False") arrive as object (pandas 2) or str (pandas 3).
        if col in base.columns and not pd.api.types.is_bool_dtype(base[col]):
            base[col] = base[col].astype(str).str.strip().str.lower().map({"true": True, "false": False})
    for col in NUMERIC_COLS:
        if col in base.columns:
            base[col] = pd.to_numeric(base[col], errors="coerce")
    return base


def _norm(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.lower()


def _flag(s: pd.Series) -> pd.Series:
    return s.astype("boolean").fillna(False).astype(bool)


def compute_rule_flags(base: pd.DataFrame, buffer_usd: float) -> pd.DataFrame:
    """Return one boolean column per reason code."""
    return pd.DataFrame(
        {
            "KYC_NOT_VERIFIED": _norm(base["snapshot_kyc_status"]) != "verified",
            "ACCOUNT_NOT_ACTIVE": _norm(base["snapshot_account_status"]) != "active",
            "UNWHITELISTED_HIGH_AML": (_norm(base["snapshot_aml_risk_tier"]) == "high")
            & ~_flag(base["dest_is_whitelisted"]),
            "INVALID_AMOUNT": base["amount"].isna() | (base["amount"] <= 0),
            "DUPLICATE_REQUEST": _flag(base["duplicate_candidate_flag"]),
            # NaN < buffer is False: a missing balance does not trigger the rule,
            # same as in the original notebook.
            "INSUFFICIENT_SETTLED_AFTER_BUFFER": base["settled_cash_after_request"] < buffer_usd,
            "INSUFFICIENT_AVAILABLE_AFTER_BUFFER": base["available_cash_after_request"] < buffer_usd,
            "DEST_CHANGED_RECENTLY": _flag(base["dest_changed_recently_flag"]),
            "URGENT_RISK_TIER": _flag(base["urgent_risk_flag"]),
        },
        index=base.index,
    )


def decide(triggered: list, severity: Dict[str, int]) -> dict:
    """Pick the decision for one request given the reason codes it triggered."""
    if not triggered:
        return {"decision": "APPROVE", "reason_code": pd.NA, "severity": pd.NA, "triggered_rules": pd.NA}

    top_reason = max(triggered, key=lambda code: severity[code])
    if top_reason in REJECT_REASON_CODES:
        decision = "REJECT"
    elif top_reason in HOLD_REASON_CODES:
        decision = "HOLD"
    else:
        raise ValueError(f"reason_code no clasificado: {top_reason}")

    return {
        "decision": decision,
        "reason_code": top_reason,
        "severity": severity[top_reason],
        "triggered_rules": " | ".join(triggered),
    }


def run_engine(base: pd.DataFrame, rules: Dict[str, float], severity: Dict[str, int]) -> Dict[str, pd.DataFrame]:
    base = normalize_types(base)
    flags = compute_rule_flags(base, float(rules["BUFFER_USD"]))

    # Rules are listed in glossary order so triggered_rules is deterministic.
    ordered_codes = list(severity.keys())
    decisions = pd.DataFrame(
        [decide([code for code in ordered_codes if row[code]], severity) for _, row in flags.iterrows()],
        index=base.index,
    )
    decisions["severity"] = pd.to_numeric(decisions["severity"])

    final = pd.concat([base, decisions], axis=1)[OUTPUT_COLS].copy()
    final["decision_order"] = final["decision"].map(DECISION_ORDER)
    final = (
        final.sort_values(
            ["decision_order", "severity", "created_at", "request_id"],
            ascending=[True, False, True, True],
        )
        .drop(columns="decision_order")
        .reset_index(drop=True)
    )

    review_queue = (
        final.loc[final["decision"] == "HOLD"]
        .sort_values(["severity", "created_at", "request_id"], ascending=[False, True, True])
        .reset_index(drop=True)
    )

    rule_hits = (
        pd.DataFrame(
            [
                {"reason_code": code, "severity": severity[code], "hit_count": int(flags[code].sum())}
                for code in ordered_codes
            ]
        )
        .sort_values(["severity", "reason_code"], ascending=[False, True])
        .reset_index(drop=True)
    )

    decision_counts = final["decision"].value_counts().rename_axis("decision").reset_index(name="request_count")

    return {
        "final_decisions": final,
        "review_queue": review_queue,
        "rule_hits": rule_hits,
        "decision_counts": decision_counts,
    }


def load_inputs(input_dir: Path = EJ3_DIR):
    base = pd.read_csv(input_dir / "ejercicio_3_requests_enriched_base.csv")
    rules_df = pd.read_csv(input_dir / "ejercicio_3_rules_config.csv")
    glossary_df = pd.read_csv(input_dir / "ejercicio_3_reason_glossary.csv")
    rules = dict(zip(rules_df["rule_name"], rules_df["value"], strict=True))
    severity = {code: int(sev) for code, sev in zip(glossary_df["reason_code"], glossary_df["severity"], strict=True)}
    return base, rules, severity


def main(argv: Optional[list] = None) -> None:
    parser = argparse.ArgumentParser(description="Withdrawal decision engine (Ejercicio 3)")
    parser.add_argument("--input-dir", type=Path, default=EJ3_DIR)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    results = run_engine(*load_inputs(args.input_dir))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, df in results.items():
        df.to_csv(args.output_dir / f"ejercicio_3_{name}.csv", index=False)

    print(results["decision_counts"].to_string(index=False))
    print(f"\nResultados guardados en: {args.output_dir}")


if __name__ == "__main__":
    main()
