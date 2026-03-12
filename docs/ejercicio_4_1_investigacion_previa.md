# Ejercicio 4.1 - Investigación previa
**Prueba técnica Insights**  
**Santiago Osorio Gómez**

## 4.1.1 ¿Cómo funciona ACH en EE.UU.?
El flujo ACH se entiende como una cadena de cinco actores: **Originator -> ODFI -> ACH Network / Operator -> RDFI -> Receiver**.  
El Originator inicia la instrucción; el ODFI la valida y la origina; el operador ACH la compensa y enruta; el RDFI la recibe, la postea o la retorna; y el Receiver recibe el abono o sufre el débito.

ACH no es un riel en tiempo real: funciona por archivos y ventanas de procesamiento.  
Como criterio práctico para el agente, la opción base debe ser **ACH estándar**, mientras que **Same-Day ACH** solo debería recomendarse cuando el cliente necesita fondeo urgente el mismo día hábil, el monto es elegible y la institución participante soporta ese flujo.

## 4.1.2 Requisitos para fondear una cuenta de inversión vía ACH
Para configurar un **ACH pull**, el usuario necesita como mínimo:
- nombre del banco;
- estado donde abrió la cuenta;
- ABA routing number;
- account number;
- tipo de cuenta (checking o savings);
- nombre legal del titular;
- autorización expresa del débito ACH.

Adicionalmente, el proceso suele requerir **verificación de titularidad** por instant verification o micro-deposits, y en algunos casos verificación de balances.

Los códigos de retorno más relevantes para el prototipo son:
- **R01**: fondos insuficientes;
- **R02**: cuenta cerrada;
- **R03**: cuenta inexistente o no localizable.

## 4.1.3 Routing numbers (ABA): lógica y lookup por banco y estado
Un **ABA routing number** es un identificador de 9 dígitos para pagos en EE.UU.  
No es suficiente con preguntar el banco: los bancos grandes pueden tener múltiples routing numbers por estado, región o legado operativo. Por eso, el agente debe cumplir esta regla:

1. preguntar banco;
2. preguntar estado;
3. hacer lookup;
4. mostrar el routing sugerido;
5. pedir confirmación si hay ambigüedad.

Para este prototipo se construye una tabla curada de 10 bancos frecuentes, suficiente como **seed lookup** y no como directorio nacional exhaustivo.

## 4.1.4 Comparativa: ACH vs Wire vs Debit Card
La conclusión operativa es:

- **ACH** debe ser el método preferido para Insights por su bajo costo, buena experiencia y adecuación al fondeo recurrente.
- **Wire** debe recomendarse cuando el cliente prioriza urgencia o monto alto y acepta mayor costo.
- **Debit Card** sirve mejor como opción complementaria para conveniencia e importes pequeños, no como riel principal del bot.

## Conclusión de 4.1
La investigación sugiere que el agente de Insights debe ser:
- **compliance-minded**;
- explícito sobre tiempos de disponibilidad;
- estricto con la recolección de banco + estado antes de cualquier instrucción;
- y prudente al comunicar routing numbers, tratándolos como inferencia asistida con confirmación cuando sea necesario.

Esta síntesis deja lista la base conceptual para diseñar en 4.2 un bot CLI simple, determinístico y modular.
