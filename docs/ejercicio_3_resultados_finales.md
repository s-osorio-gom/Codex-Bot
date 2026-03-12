# Ejercicio 3 - Caso de automatización
**Prueba técnica Insights**  
**Santiago Osorio Gómez**

## Resultado agregado
- **APPROVE:** 51
- **HOLD:** 49
- **REJECT:** 28

## Criterio aplicado
- `REJECT` domina sobre `HOLD`
- `HOLD` domina sobre `APPROVE`
- si una solicitud activa múltiples reglas, se asigna el `reason_code` de mayor severidad

## Lectura de resultados
Los rechazos estuvieron explicados principalmente por cuentas no activas y por KYC no verificado.

Los casos de revisión manual se concentraron principalmente en:
- solicitudes potencialmente duplicadas,
- cambios recientes de destino,
- y solicitudes que comprometían el efectivo liquidado después del buffer operativo.

El archivo de review se generó únicamente con solicitudes `HOLD`, ordenadas de mayor a menor severidad.
