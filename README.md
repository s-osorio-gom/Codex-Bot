# Junior Investment Analyst — Technical Assessment

[![CI](https://github.com/s-osorio-gom/prueba-analista-jr-insights-santiago-osorio/actions/workflows/ci.yml/badge.svg)](https://github.com/s-osorio-gom/prueba-analista-jr-insights-santiago-osorio/actions/workflows/ci.yml)

**Author:** Santiago Osorio Gómez · [github.com/s-osorio-gom](https://github.com/s-osorio-gom)

My solution to a four-part take-home assessment for a Junior Investment Analyst role at Insights. It covers relational data logic, portfolio risk/return, a rule-based withdrawal decision engine and a conversational ACH-funding prototype.

> *Solución a la prueba técnica de Analista Jr de Inversiones de Insights. Los notebooks y documentos originales están en español; esta portada está en inglés para una audiencia internacional.*

## Highlights

| Exercise | What it shows | Status in this repo |
|---|---|---|
| **3 · Withdrawal decision engine** | Rule-based `APPROVE` / `HOLD` / `REJECT` classifier with severity ranking and a manual-review queue | ✅ Runnable module + tests (`src/withdrawal_engine.py`) |
| **4 · ACH funding chatbot** | Deterministic state-machine CLI bot: routing-number lookup, input validation, simulated `R01`/`R03` returns, masked transcripts | ✅ Runnable CLI + tests (`src/ach_bot.py`) |
| **2 · Portfolio risk/return** | Expected return and volatility for two portfolios from a 30,000-scenario × 55-asset simulation, plus a comparison of two LLM answers | 📓 Notebook (input data not included) |
| **1 · Data handling** | `join` / `filter` / `drop` sequence to query balances, validated in pandas | 📓 Notebook |

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/s-osorio-gom/prueba-analista-jr-insights-santiago-osorio.git
cd prueba-analista-jr-insights-santiago-osorio
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the withdrawal decision engine (Exercise 3)

```bash
python src/withdrawal_engine.py --output-dir out/ejercicio_3
```

```
decision  request_count
 APPROVE             51
    HOLD             49
  REJECT             28
```

It reads the prepared inputs in `outputs/ejercicio_3/` and writes five CSVs: `final_decisions`, `review_queue`, `rule_hits`, `decision_summary` and `decision_counts`. A regression test checks that they are identical to the results published with the original submission.

**How decisions are made.** Each request is checked against nine rules. Each rule has a reason code and a severity:

| Severity | Reason code | Outcome |
|---:|---|---|
| 100 | `KYC_NOT_VERIFIED` | REJECT |
| 95 | `ACCOUNT_NOT_ACTIVE` | REJECT |
| 90 | `UNWHITELISTED_HIGH_AML` | REJECT |
| 85 | `INVALID_AMOUNT` | REJECT |
| 70 | `DUPLICATE_REQUEST` | HOLD |
| 65 | `INSUFFICIENT_SETTLED_AFTER_BUFFER` | HOLD |
| 55 | `INSUFFICIENT_AVAILABLE_AFTER_BUFFER` | HOLD |
| 45 | `DEST_CHANGED_RECENTLY` | HOLD |
| 35 | `URGENT_RISK_TIER` | HOLD |

When several rules fire, the most severe one decides. The output keeps every rule that fired in `triggered_rules`, for auditability. Only `HOLD` cases go to the review queue, sorted by severity. The cash buffer (USD 50) is read at run time from `outputs/ejercicio_3/ejercicio_3_rules_config.csv`. The time-window flags (recent destination change, duplicate window) were precomputed by the notebook into `ejercicio_3_requests_enriched_base.csv`. Changing those two values in the config file therefore has no effect on the module.

### Run the ACH funding bot (Exercise 4)

```bash
python src/ach_bot.py --scenario r01   # or: success, r03
```

Suggested demo answers (all fictitious): `Bank of America` → `Texas` → `checking` → `Jane Doe` → `123456789` → `2500` → `si`.

Real output of the command above, lightly abridged (user answers shown after `>`):

```
Bot: Primero, ¿cuál es tu banco?
> Bank of America
Bot: ¿En qué estado abriste esa cuenta bancaria?
> Texas
Bot: Encontré un routing sugerido: 111000025. Coincidencia encontrada en seed lookup por banco y estado/región.
...
Bot: Voy a confirmar los datos antes de enviar:
- Banco: Bank of America
- Estado: Texas
- Routing sugerido: 111000025
- Tipo de cuenta: checking
- Titular: Jane Doe
- Account number: ****6789
- Monto: USD 2500.00
¿Confirmas el envío? (si/no)
> si
Bot: La operación fue retornada con código R01 (insufficient funds). La cuenta existe, pero no tenía fondos suficientes para completar el débito.
```

Transcripts are saved as JSON and TXT to `outputs/ejercicio_4/transcripts/`, or to `--output-dir`. The account number is masked (`****6789`) in both the saved fields and the conversation history. Invalid answers are asked again. Ctrl-D or Ctrl-C ends the session without submitting, and the transcript is still saved.

> The three transcripts committed with the original submission predate this masking: they contain the fictitious demo number `123456789` in full. They are kept unchanged as part of the original deliverable.

**Design choice:** the conversation is a plain finite-state machine (`src/ach_state.py`), not an LLM. Every branch is deterministic, so it is easy to test, debug and audit. That matters in a payments flow. An LLM could later be added for free-text understanding without moving the validation logic out of Python.

**Limits:** this is a prototype. The routing lookup is a 10-row seed table built from public bank pages (`outputs/ejercicio_4/ejercicio_4_1_routing_lookup_seed.csv`). Bank submission and the ACH outcomes are simulated. Nothing connects to a bank or payment API.

### Run the tests

```bash
pip install -r requirements-dev.txt
pytest
ruff check src tests
```

The suite covers:

- **Rule engine:** each rule on synthetic requests, and a regression check against the published results.
- **Bot:** the full conversation for every scenario, re-prompting after invalid answers, Ctrl-D handling, and transcript masking.
- **Validators:** amount and account-number edge cases (`0.001`, `2,5`, `1e400`, `nan`).
- **Randomised stress tests:** 20,000 perturbed requests checked against decision invariants, and 500 fuzzed bot conversations with hostile input.

A `Makefile` wraps the common commands: `make setup`, `make check`, `make engine`, `make bot SCENARIO=r03`.

GitHub Actions runs the same checks, plus a CLI smoke test, on Python 3.10 and 3.12 for every push.

## Repository layout

```
src/
  withdrawal_engine.py   Exercise 3 rule engine (CLI + importable functions)
  ach_bot.py             Exercise 4 conversation loop / CLI
  ach_services.py        Routing lookup, validation, simulated outcomes, transcripts
  ach_state.py           Conversation states and session data
tests/                   pytest suite
notebooks/               Original exercise notebooks (Spanish)
docs/                    Original written answers and summaries (Spanish)
outputs/                 Results produced by the notebooks; also the inputs for src/
requirements*.txt        Runtime / dev / notebook dependencies
Makefile                 Shortcuts: setup, check, engine, bot
```

## Provenance: original submission vs. later improvements

- **Original submission** (12 March 2026): everything up to commit [`c5963d6`](https://github.com/s-osorio-gom/prueba-analista-jr-insights-santiago-osorio/tree/c5963d6). This is the notebooks, `docs/`, `outputs/` and the first version of the ACH bot. I have left the notebooks, docs and outputs unchanged so the evaluated work stays as submitted, with one exception: on 11 October 2026 the whole history was cleaned of personal data. An ID number, e-mail addresses and a local user path were replaced with placeholders in every commit. Messages, authors and dates were kept.
- **Later improvements** (after the assessment, not part of what was evaluated):
  - Extracted the Exercise 3 engine from the notebook into `src/withdrawal_engine.py`, with a regression test that it reproduces the submitted results exactly.
  - Fixed the ACH bot so it runs from a fresh clone. It previously looked for a local `data/` folder that was never committed.
  - The ACH bot no longer saves the full account number in transcripts.
  - Matched states by whole words. Before, a one-letter input could match any bank or state.
  - Rounded money amounts with `Decimal`.
  - Made flag parsing compatible with pandas 3.
  - Ctrl-D and Ctrl-C end the bot cleanly. Amounts that round to zero, and ambiguous decimal commas such as `2,5`, are rejected. Flag parsing accepts `1/0` and `yes/no` and raises on unknown values instead of silently treating them as False.
  - Added tests (including randomised stress tests), CI, declared dependencies, a Makefile and this README. An independent review of the changes was run and its findings addressed.

## Known limitations

- **The notebooks do not run from a fresh clone.** They expect the original assessment files in a local `data/` folder: a withdrawals Excel workbook and the return-simulation matrix. Those files belonged to the assessment and are not redistributed here. Their saved outputs are kept in the notebooks and in `outputs/`.
- Exercises 1 and 2 are presented as analysis (notebooks + `docs/`) and have no standalone module.
- `outputs/ejercicio_3/` holds the cleaned tables prepared from the assessment data. They use opaque IDs (`C001`, `A0001`, …) and serve as the engine's input.

## License

- **Code** (`src/`, `tests/`, the code cells in `notebooks/`, `Makefile`, CI configuration): [MIT](LICENSE), © 2026 s-osorio-gom.
- **Written material and results** (`docs/`, `outputs/`, notebook text): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You may reuse them with attribution.
- **Data:** the client, adviser, account, e-mail and transaction records in this repository are simulated and do not describe real people; e-mail addresses use reserved example domains. The original assessment input files (`data/`) are not included and are not covered by these licenses.
