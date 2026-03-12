# Ejercicio 4 - Resultados finales del prototipo ACH Funding Bot
**Prueba técnica Insights**  
**Santiago Osorio Gómez**

## Resultado general
Se ejecutaron satisfactoriamente los tres escenarios mínimos requeridos:

- `success`
- `R01`
- `R03`

## Resumen de pruebas
| scenario | outcome_label | bank | state_name | routing_number | account_type | masked_account_number | amount | outcome_code | total_turns | bot_turns | user_turns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r01 | R01 - Insufficient Funds | Bank of America | Texas | 111000025 | checking | ****6789 | 2500.0 | R01 | 18 | 11 | 7 |
| r03 | R03 - No Account / Unable to Locate Account | Bank of America | Texas | 111000025 | checking | ****6789 | 2500.0 | R03 | 18 | 11 | 7 |
| success | Success | Bank of America | Texas | 111000025 | checking | ****6789 | 2500.0 |  | 18 | 11 | 7 |

## Mensajes finales por escenario
| scenario | outcome_code | outcome_message | file_name |
| --- | --- | --- | --- |
| r01 | R01 | La operación fue retornada con código R01 (insufficient funds). La cuenta existe, pero no tenía fondos suficientes para completar el débito. | ach_bot_r01_20260312_222818.json |
| r03 | R03 | La operación fue retornada con código R03 (no account / unable to locate account). No fue posible localizar la cuenta con los datos proporcionados. | ach_bot_r03_20260312_222903.json |
| success |  | Tu solicitud ACH fue creada correctamente por USD 2500.00. La referencia quedó en estado submitted y el fondeo puede reflejarse en 1 a 5 días hábiles. | ach_bot_success_20260312_222724.json |

## Lectura de resultados
El prototipo mostró un comportamiento consistente en los tres escenarios evaluados.

- En **success**, el bot completó el flujo y devolvió una confirmación de solicitud ACH creada.
- En **R01**, el bot simuló correctamente un retorno por fondos insuficientes.
- En **R03**, el bot simuló correctamente un retorno por imposibilidad de localizar la cuenta.

## Conclusión
El agente CLI implementado cumple con el alcance esperado del ejercicio:
- recolecta datos bancarios básicos;
- realiza lookup de routing number;
- explica el proceso ACH;
- confirma la información antes de enviar;
- simula outcomes relevantes;
- y conserva evidencia del flujo conversacional mediante transcripts.
