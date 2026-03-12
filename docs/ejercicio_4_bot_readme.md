# ACH Funding Bot - Quick Start

## Qué hace
Bot CLI para simular el fondeo de una cuenta de inversión vía ACH.

## Qué pregunta
- banco
- estado
- tipo de cuenta
- nombre del titular
- account number
- monto
- confirmación final

## Qué hace después
- infiere un routing number usando un lookup seed
- explica el proceso ACH
- simula outcome final:
  - success
  - R01
  - R03
- guarda transcript en:
  - outputs/ejercicio_4/transcripts/

## Cómo correrlo
Desde la raíz del proyecto:

source .venv/bin/activate
python src/ach_bot.py --scenario success
python src/ach_bot.py --scenario r01
python src/ach_bot.py --scenario r03

## Inputs sugeridos para el demo
- Banco: Bank of America
- Estado: Texas
- Tipo de cuenta: checking
- Titular: Santiago Osorio Gomez
- Account number: 123456789
- Monto: 2500
- Confirmación: si

## Alcance
Este prototipo prioriza claridad, velocidad de implementación y testabilidad.
No usa web app, LLM, RAG ni integraciones externas en tiempo real.
