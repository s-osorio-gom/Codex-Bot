# Ejercicio 1 - Manejo de Datos
**Prueba tecnica Insights**  
**Santiago Osorio Gomez**

## Objetivo
Construir una secuencia de funciones `join`, `filter` y `drop` que permita consultar el valor de los balances para un rango de fechas y segun tipo de portafolio, de los portafolios pertenecientes a usuarios cuyo asesor sea `person1@example.com`.

## Secuencia propuesta
1. `join(Portafolios, Usuarios, id_usuario, Usuarios_portafolios)`
2. `drop(Usuarios_portafolios, email & perfil_riesgo)`
3. `join(Usuarios_portafolios, Asesores, id_asesor, Usuarios_portafolios_asesores)`
4. `filter(Usuarios_portafolios_asesores, email, "person1@example.com")`
5. `drop(Usuarios_portafolios_asesores, num_clientes)`
6. `join(Usuarios_portafolios_asesores, Balances, id_portafolio, Tabla_final)`
7. `filter(Tabla_final, tipo_portafolio, <tipo_portafolio>)`
8. `filter(Tabla_final, fecha, [<fecha_inicio>, <fecha_fin>])`

## Justificacion
La logica de la solucion consiste en:
- relacionar primero los portafolios con sus usuarios mediante `id_usuario`;
- eliminar campos que no son necesarios para la consulta final;
- incorporar la informacion de asesores mediante `id_asesor`;
- filtrar unicamente los registros asociados al asesor `person1@example.com`;
- unir esa tabla resultante con los balances mediante `id_portafolio`;
- y finalmente aplicar los filtros de tipo de portafolio y rango de fechas para obtener la consulta requerida.

## Validacion en Python
Para verificar la logica, implemente una version reproducible en Python y ejecute una prueba con un caso demo consistente.

Caso de validacion usado:
- `tipo_portafolio = "bonos"`
- `fecha_inicio = "2022-10-01"`
- `fecha_fin = "2022-10-31"`

Resultado del caso demo:
- se identifico el portafolio `45789`;
- asociado al usuario `123456`;
- con asesor `person1@example.com`;
- y se obtuvieron los balances del rango consultado para las fechas `2022-10-12` y `2022-10-18`.

## Nota metodologica
Los registros visibles en el enunciado cumplen una funcion ilustrativa de la estructura de las tablas y de sus relaciones.
Para validar la secuencia completa en Python, construi una version demo consistente, manteniendo la misma logica relacional entre `Usuarios`, `Portafolios`, `Asesores` y `Balances`.
