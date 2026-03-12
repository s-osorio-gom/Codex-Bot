from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List


class BotState(str, Enum):
    ASK_BANK = "ask_bank"
    ASK_STATE = "ask_state"
    LOOKUP_ROUTING = "lookup_routing"
    EXPLAIN_ACH = "explain_ach"
    ASK_ACCOUNT_TYPE = "ask_account_type"
    ASK_ACCOUNT_HOLDER = "ask_account_holder"
    ASK_ACCOUNT_NUMBER = "ask_account_number"
    ASK_AMOUNT = "ask_amount"
    CONFIRM = "confirm"
    SUBMIT = "submit"
    END = "end"


@dataclass
class Turn:
    speaker: str
    message: str
    timestamp_utc: str
    state: str


@dataclass
class SessionState:
    scenario: str = "success"
    current_state: BotState = BotState.ASK_BANK
    bank: Optional[str] = None
    state_name: Optional[str] = None
    routing_number: Optional[str] = None
    routing_match_note: Optional[str] = None
    account_type: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    amount: Optional[float] = None
    outcome_code: Optional[str] = None
    outcome_message: Optional[str] = None
    history: List[Turn] = field(default_factory=list)

    def add_turn(self, speaker: str, message: str) -> None:
        self.history.append(
            Turn(
                speaker=speaker,
                message=message,
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
                state=self.current_state.value,
            )
        )

    @property
    def masked_account_number(self) -> Optional[str]:
        if not self.account_number:
            return None
        return f"****{self.account_number[-4:]}"

    def to_dict(self):
        data = asdict(self)
        data["current_state"] = self.current_state.value
        return data
