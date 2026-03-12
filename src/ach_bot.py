import argparse

from ach_state import BotState, SessionState
from ach_services import (
    clean_account_number,
    explain_ach,
    load_routing_lookup,
    lookup_routing,
    save_session_artifacts,
    simulate_submission,
    validate_account_type,
    validate_amount,
)


def bot_say(session: SessionState, message: str) -> None:
    print(f"\nBot: {message}")
    session.add_turn("bot", message)


def user_reply(session: SessionState, prompt: str = "> ") -> str:
    response = input(prompt).strip()
    session.add_turn("user", response)
    return response


def run_bot(scenario: str) -> None:
    routing_df = load_routing_lookup()
    session = SessionState(scenario=scenario)

    bot_say(
        session,
        "Hola. Soy el prototipo ACH Funding Bot de Insights. "
        "Te voy a ayudar a preparar un fondeo ACH de forma simple y paso a paso."
    )

    while session.current_state != BotState.END:
        if session.current_state == BotState.ASK_BANK:
            bot_say(session, "Primero, ¿cuál es tu banco?")
            bank = user_reply(session)
            if not bank:
                bot_say(session, "Necesito el nombre del banco para continuar.")
                continue
            session.bank = bank
            session.current_state = BotState.ASK_STATE

        elif session.current_state == BotState.ASK_STATE:
            bot_say(session, "¿En qué estado abriste esa cuenta bancaria?")
            state_name = user_reply(session)
            if not state_name:
                bot_say(session, "Necesito el estado para buscar el routing number.")
                continue
            session.state_name = state_name
            session.current_state = BotState.LOOKUP_ROUTING

        elif session.current_state == BotState.LOOKUP_ROUTING:
            result = lookup_routing(session.bank, session.state_name, routing_df)
            if not result["found"]:
                bot_say(
                    session,
                    "No encontré una coincidencia en el lookup seed. "
                    "Para el demo, intenta con un banco/estado soportado, por ejemplo: "
                    "Bank of America + Texas, Chase + Texas o Wells Fargo + California."
                )
                session.current_state = BotState.ASK_BANK
                continue

            session.routing_number = result["routing_number"]
            session.routing_match_note = result["match_note"]
            bot_say(
                session,
                f"Encontré un routing sugerido: {session.routing_number}. "
                f"{session.routing_match_note}"
            )
            session.current_state = BotState.EXPLAIN_ACH

        elif session.current_state == BotState.EXPLAIN_ACH:
            bot_say(session, explain_ach(session.bank, session.state_name, session.routing_number))
            session.current_state = BotState.ASK_ACCOUNT_TYPE

        elif session.current_state == BotState.ASK_ACCOUNT_TYPE:
            bot_say(session, "¿Tu cuenta es checking o savings?")
            account_type_raw = user_reply(session)
            account_type = validate_account_type(account_type_raw)
            if not account_type:
                bot_say(session, "Respuesta no válida. Escribe checking o savings.")
                continue
            session.account_type = account_type
            session.current_state = BotState.ASK_ACCOUNT_HOLDER

        elif session.current_state == BotState.ASK_ACCOUNT_HOLDER:
            bot_say(session, "¿Cuál es el nombre legal del titular de la cuenta bancaria?")
            holder = user_reply(session)
            if not holder:
                bot_say(session, "Necesito el nombre del titular para continuar.")
                continue
            session.account_holder_name = holder
            session.current_state = BotState.ASK_ACCOUNT_NUMBER

        elif session.current_state == BotState.ASK_ACCOUNT_NUMBER:
            bot_say(session, "Ingresa el account number de la cuenta bancaria.")
            account_number_raw = user_reply(session)
            account_number = clean_account_number(account_number_raw)
            if not account_number:
                bot_say(session, "El account number debe tener al menos 4 dígitos.")
                continue
            session.account_number = account_number
            session.current_state = BotState.ASK_AMOUNT

        elif session.current_state == BotState.ASK_AMOUNT:
            bot_say(session, "¿Qué monto quieres fondear por ACH en USD?")
            amount_raw = user_reply(session)
            amount = validate_amount(amount_raw)
            if amount is None:
                bot_say(session, "El monto debe ser un número positivo.")
                continue
            session.amount = amount
            session.current_state = BotState.CONFIRM

        elif session.current_state == BotState.CONFIRM:
            summary = (
                "Voy a confirmar los datos antes de enviar:\n"
                f"- Banco: {session.bank}\n"
                f"- Estado: {session.state_name}\n"
                f"- Routing sugerido: {session.routing_number}\n"
                f"- Tipo de cuenta: {session.account_type}\n"
                f"- Titular: {session.account_holder_name}\n"
                f"- Account number: {session.masked_account_number}\n"
                f"- Monto: USD {session.amount:.2f}\n"
                "¿Confirmas el envío? (si/no)"
            )
            bot_say(session, summary)
            answer = user_reply(session).lower().strip()

            if answer in {"si", "sí", "s", "yes", "y"}:
                session.current_state = BotState.SUBMIT
            else:
                bot_say(session, "Entendido. No enviaré la solicitud. Puedes reiniciar el bot si deseas corregir los datos.")
                session.current_state = BotState.END

        elif session.current_state == BotState.SUBMIT:
            outcome = simulate_submission(session.scenario, session)
            session.outcome_code = outcome["code"]
            session.outcome_message = outcome["message"]
            bot_say(session, outcome["message"])
            session.current_state = BotState.END

    paths = save_session_artifacts(session)
    print("\nArchivos de transcript generados:")
    print(f"- {paths['json']}")
    print(f"- {paths['txt']}")


def main():
    parser = argparse.ArgumentParser(description="ACH Funding Bot CLI")
    parser.add_argument(
        "--scenario",
        default="success",
        choices=["success", "r01", "r03"],
        help="Escenario de simulación del resultado final.",
    )
    args = parser.parse_args()
    run_bot(args.scenario)


if __name__ == "__main__":
    main()
