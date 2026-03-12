# Ejercicio 2.1 - Retorno esperado y volatilidad esperada
**Prueba tecnica Insights**  
**Santiago Osorio Gomez**

## Metodologia
Se utilizo la matriz de simulacion de retornos anuales de 30,000 escenarios para 55 activos, junto con los vectores de pesos de los portafolios P1 y P2.

La formulacion utilizada fue:
- retorno por escenario: `r_p = R @ P`
- retorno esperado: `E[r_p] = mu @ P`
- volatilidad esperada: `sigma_p = sqrt(P' @ Sigma @ P)`

Dado que la matriz contiene retornos anuales simulados, no se aplico anualizacion adicional.

## Resultados
- **P1:** retorno esperado = **9.1191%** | volatilidad esperada = **20.6253%**
- **P2:** retorno esperado = **5.8419%** | volatilidad esperada = **10.1071%**

## Interpretacion
P1 presenta el mayor retorno esperado, pero tambien una volatilidad sustancialmente mayor.  
P2 ofrece un retorno esperado menor, pero con un nivel de riesgo claramente mas contenido.

En consecuencia, para un perfil de riesgo moderado, **P2** parece la alternativa mas eficiente en terminos de retorno por unidad de riesgo.  
Si el mandato de inversion fuera agresivo y priorizara retorno esperado sobre estabilidad, **P1** seria la alternativa razonable.
