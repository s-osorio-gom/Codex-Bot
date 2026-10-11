import json
import re
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from ach_state import SessionState

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ROUTING_SEED_PATH = PROJECT_ROOT / "outputs" / "ejercicio_4" / "ejercicio_4_1_routing_lookup_seed.csv"
TRANSCRIPTS_DIR = PROJECT_ROOT / "outputs" / "ejercicio_4" / "transcripts"


def normalize_text(text: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in str(text))
    return " ".join(cleaned.split())


def load_routing_lookup(path: Optional[Path] = None) -> pd.DataFrame:
    path = Path(path) if path is not None else ROUTING_SEED_PATH
    if not path.exists():
        raise FileNotFoundError(f"No encontré el archivo de routing lookup: {path}")

    # IMPORTANTE:
    # routing_number debe leerse como texto para no perder ceros a la izquierda
    routing_df = pd.read_csv(path, dtype={"routing_number": "string"})
    routing_df["routing_number"] = (
        routing_df["routing_number"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .str.zfill(9)
    )
    routing_df["bank_norm"] = routing_df["bank"].map(normalize_text)
    routing_df["region_norm"] = routing_df["state_or_region"].map(normalize_text)
    return routing_df


def _state_matches(user_state: str, row_region: str) -> bool:
    # Comparación por palabras completas: "California" coincide con
    # "California - North", pero "ca" ya no coincide con cualquier región
    # que contenga esas letras.
    user_tokens = set(normalize_text(user_state).split())
    region_tokens = set(normalize_text(row_region).split())

    if not user_tokens:
        return False

    if user_tokens <= region_tokens:
        return True

    return bool(region_tokens & {"nationwide", "general", "online"})


def lookup_routing(bank: str, state_name: str, routing_df: pd.DataFrame) -> Dict[str, Optional[str]]:
    bank_norm = normalize_text(bank)
    state_norm = normalize_text(state_name)

    exact_matches = routing_df[
        (routing_df["bank_norm"] == bank_norm)
        & (routing_df["region_norm"].map(lambda x: _state_matches(state_norm, x)))
    ].copy()

    if not exact_matches.empty:
        row = exact_matches.iloc[0]
        return {
            "found": True,
            "bank": str(row["bank"]),
            "state_or_region": str(row["state_or_region"]),
            "routing_number": str(row["routing_number"]),
            "match_note": "Coincidencia encontrada en seed lookup por banco y estado/región.",
        }

    if len(bank_norm) < 3:
        # Evita que entradas como "a" coincidan parcialmente con cualquier banco.
        return _not_found()

    partial_matches = routing_df[
        (routing_df["bank_norm"].str.contains(bank_norm, regex=False))
        & (routing_df["region_norm"].map(lambda x: _state_matches(state_norm, x)))
    ].copy()

    if not partial_matches.empty:
        row = partial_matches.iloc[0]
        return {
            "found": True,
            "bank": str(row["bank"]),
            "state_or_region": str(row["state_or_region"]),
            "routing_number": str(row["routing_number"]),
            "match_note": (
                "Coincidencia parcial encontrada en seed lookup; conviene confirmación visual en app o cheque."
            ),
        }

    return _not_found()


def _not_found() -> Dict[str, Optional[str]]:
    return {
        "found": False,
        "bank": None,
        "state_or_region": None,
        "routing_number": None,
        "match_note": "No se encontró una coincidencia en el lookup seed.",
    }


def explain_ach(bank: str, state_name: str, routing_number: str) -> str:
    return (
        f"Perfecto. Para {bank} en {state_name}, el routing sugerido en el lookup seed es {routing_number}.\n"
        "El proceso ACH funciona así: recopilamos tus datos bancarios, confirmamos la información, "
        "originamos la instrucción y el banco receptor puede aceptar o retornar la operación. "
        "En general, el fondeo ACH no es instantáneo y puede reflejarse en un rango de 1 a 5 días hábiles."
    )


def validate_account_type(value: str) -> Optional[str]:
    value_norm = normalize_text(value)
    if value_norm in {"checking", "corriente"}:
        return "checking"
    if value_norm in {"savings", "ahorros"}:
        return "savings"
    return None


def clean_account_number(value: str) -> Optional[str]:
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if len(digits) < 4:
        return None
    return digits


THOUSANDS_RE = re.compile(r"^\d{1,3}(,\d{3})+(\.\d+)?$")


def validate_amount(value: str) -> Optional[float]:
    text = str(value).strip()
    if "," in text:
        # Solo se aceptan comas como separador de miles ("2,500.00"). "2,5" es
        # ambiguo (en español significa 2.5) y se rechaza en lugar de leerlo como 25.
        if not THOUSANDS_RE.match(text):
            return None
        text = text.replace(",", "")
    try:
        # Decimal evita errores de redondeo binario (round(2500.555, 2) == 2500.55).
        # quantize lanza InvalidOperation con montos absurdos (p. ej. 1e400).
        amount = Decimal(text).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        return None
    if not amount.is_finite() or amount <= 0:
        return None
    return float(amount)


def simulate_submission(scenario: str, session: SessionState) -> Dict[str, Optional[str]]:
    scenario = scenario.lower().strip()

    if scenario == "success":
        return {
            "status": "success",
            "code": None,
            "message": (
                f"Tu solicitud ACH fue creada correctamente por USD {session.amount:.2f}. "
                "La referencia quedó en estado submitted y el fondeo puede reflejarse en 1 a 5 días hábiles."
            ),
        }

    if scenario == "r01":
        return {
            "status": "returned",
            "code": "R01",
            "message": (
                "La operación fue retornada con código R01 (insufficient funds). "
                "La cuenta existe, pero no tenía fondos suficientes para completar el débito."
            ),
        }

    if scenario == "r03":
        return {
            "status": "returned",
            "code": "R03",
            "message": (
                "La operación fue retornada con código R03 (no account / unable to locate account). "
                "No fue posible localizar la cuenta con los datos proporcionados."
            ),
        }

    raise ValueError("Escenario no soportado. Usa: success, r01 o r03.")


def build_transcript_text(session: SessionState) -> str:
    lines = []
    lines.append("ACH BOT TRANSCRIPT")
    lines.append(f"Scenario: {session.scenario}")
    lines.append(f"Bank: {session.bank}")
    lines.append(f"State: {session.state_name}")
    lines.append(f"Routing: {session.routing_number}")
    lines.append(f"Account type: {session.account_type}")
    lines.append(f"Account holder: {session.account_holder_name}")
    lines.append(f"Account number: {session.masked_account_number}")
    lines.append(f"Amount: {session.amount}")
    lines.append(f"Outcome code: {session.outcome_code}")
    lines.append("")
    lines.append("Conversation history:")
    for turn in session.history:
        lines.append(f"[{turn.timestamp_utc}] {turn.speaker.upper()} ({turn.state}): {turn.message}")
    return "\n".join(lines)


def _to_json_safe(obj: Any):
    if isinstance(obj, dict):
        return {str(k): _to_json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_to_json_safe(v) for v in obj]

    if isinstance(obj, tuple):
        return [_to_json_safe(v) for v in obj]

    # Tipos de pandas / numpy
    if hasattr(obj, "item") and callable(obj.item):
        try:
            return obj.item()
        except Exception:
            pass

    # Datetimes y otros objetos
    if isinstance(obj, Path):
        return str(obj)

    return obj


def save_session_artifacts(session: SessionState, out_dir: Optional[Path] = None) -> Dict[str, Path]:
    out_dir = Path(out_dir) if out_dir is not None else TRANSCRIPTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base_name = f"ach_bot_{session.scenario}_{timestamp}"

    json_path = out_dir / f"{base_name}.json"
    txt_path = out_dir / f"{base_name}.txt"

    session_dict = _to_json_safe(session.to_dict())

    json_path.write_text(
        json.dumps(session_dict, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    txt_path.write_text(build_transcript_text(session), encoding="utf-8")

    return {"json": json_path, "txt": txt_path}
