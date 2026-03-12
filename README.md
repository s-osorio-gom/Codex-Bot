# Prueba técnica Insights
**Santiago Osorio Gómez**  
**Cédula:** 1000.099.104

## Resumen
Este repositorio contiene la solución desarrollada para la prueba técnica de **Analista Jr de Inversiones** de Insights.

La entrega está organizada por ejercicios e incluye:

- notebooks con el desarrollo completo;
- código fuente en Python;
- documentación de apoyo;
- y outputs generados durante la ejecución.

## Estructura del proyecto
- `notebooks/` → notebooks principales por ejercicio
- `src/` → código fuente del bot ACH del ejercicio 4
- `docs/` → documentación y resúmenes finales
- `outputs/` → resultados generados por los ejercicios

## Notebooks principales
- `notebooks/Ejercicio1.ipynb`
- `notebooks/Ejercicio2.ipynb`
- `notebooks/Ejercicio3.ipynb`
- `notebooks/Ejercicio4.ipynb`

## Ejercicio 1
Resolución en Python de la lógica de joins, filtros y drops solicitada en el enunciado, incluyendo validación metodológica del ejemplo presentado en el PDF.

## Ejercicio 2
Cálculo del retorno esperado y volatilidad de los portafolios P1 y P2, junto con el análisis financiero correspondiente y la comparación metodológica entre modelos de IA.

## Ejercicio 3
Construcción de un motor de decisión para solicitudes de retiro con clasificación `APPROVE`, `HOLD` y `REJECT`, incluyendo archivo de review y outputs generados.

## Ejercicio 4
Implementación de un prototipo funcional de chatbot ACH en Python CLI, con:

- lookup de routing number;
- flujo conversacional determinístico;
- simulación de escenarios `success`, `R01` y `R03`;
- y transcripts generados como evidencia.

## Cómo correr el bot del ejercicio 4
Desde la raíz del proyecto:

```bash
source .venv/bin/activate
python src/ach_bot.py --scenario success
python src/ach_bot.py --scenario r01
python src/ach_bot.py --scenario r03
