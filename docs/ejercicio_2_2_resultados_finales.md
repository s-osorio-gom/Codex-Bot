# Ejercicio 2.2 - Cálculo numérico del retorno esperado y la volatilidad esperada
**Prueba técnica Insights**  
**Santiago Osorio Gómez**

## Metodología
Con base en la formulación del punto 2.1, se calcularon los valores numéricos del retorno esperado y la volatilidad esperada de los portafolios P1 y P2 utilizando:

- retorno esperado: `E[r_p] = mu @ P`
- volatilidad esperada: `sigma_p = sqrt(P' @ Sigma @ P)`

donde `mu` es el vector de retornos esperados de los activos y `Sigma` es la matriz de covarianzas de la matriz de simulación.

Dado que la información de entrada corresponde a retornos anuales simulados, no se aplicó anualización adicional.

## Resultados
- **P1:** retorno esperado = **9.1191%** | volatilidad esperada = **20.6253%**
- **P2:** retorno esperado = **5.8419%** | volatilidad esperada = **10.1071%**

## Interpretación
P1 exhibe una combinación de mayor retorno esperado y mayor riesgo, por lo que se asocia a un perfil de inversión más agresivo.  
P2 presenta un retorno esperado menor, pero con una volatilidad notablemente más baja, lo que lo hace más consistente con un perfil moderado o conservador.

En consecuencia, la elección entre ambos portafolios depende del nivel de tolerancia al riesgo del inversionista.
