# Ejercicio 4 - Arquitectura mínima recomendada del agente ACH

## Objetivo
Construir un prototipo funcional, rápido y defendible dentro de una ventana corta de implementación.

## Decisión técnica
Se utiliza una arquitectura simple con cuatro capas:

1. Estado conversacional
   - Archivo: src/ach_state.py
   - Responsabilidad: guardar estado actual, datos recolectados e historial.

2. Servicios
   - Archivo: src/ach_services.py
   - Responsabilidad:
     - cargar routing lookup;
     - inferir routing number;
     - validar entradas;
     - simular outcomes;
     - guardar transcripts.

3. Orquestación
   - Archivo: src/ach_bot.py
   - Responsabilidad:
     - conducir el flujo;
     - pedir datos;
     - confirmar;
     - ejecutar la simulación final.

4. Datos seed
   - Archivo reutilizado:
     - outputs/ejercicio_4/ejercicio_4_1_routing_lookup_seed.csv
   - Responsabilidad:
     - permitir un lookup rápido y local sin depender de APIs externas.

## Estados del bot
- ask_bank
- ask_state
- lookup_routing
- explain_ach
- ask_account_type
- ask_account_holder
- ask_account_number
- ask_amount
- confirm
- submit
- end

## Casos soportados
- success
- R01
- R03

## Criterio de diseño
La lógica crítica permanece en Python y no depende de un LLM.
Esto hace el prototipo más fácil de probar, depurar y defender.
