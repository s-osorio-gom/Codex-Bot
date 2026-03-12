{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Prueba t\'e9cnica Insights\
**Santiago Osorio G\'f3mez**  \
**C\'e9dula:** 1000.099.104\
\
## Resumen\
Esta carpeta contiene la soluci\'f3n desarrollada para la prueba t\'e9cnica de Analista Jr de Inversiones de Insights.\
\
La entrega est\'e1 organizada por ejercicios:\
\
- `notebooks/` contiene los notebooks principales por ejercicio\
- `src/` contiene el c\'f3digo fuente del prototipo ACH del ejercicio 4\
- `outputs/` contiene los resultados generados\
- `docs/` contiene documentaci\'f3n y res\'famenes finales\
- `data/` contiene los insumos originales utilizados\
\
## Estructura del proyecto\
- `notebooks/Ejercicio1.ipynb`\
- `notebooks/Ejercicio2.ipynb`\
- `notebooks/Ejercicio3.ipynb`\
- `notebooks/Ejercicio4.ipynb`\
\
## Ejercicio 1\
Resoluci\'f3n en Python de la l\'f3gica de joins, filtros y drops solicitada en el enunciado, incluyendo validaci\'f3n metodol\'f3gica del ejemplo del PDF.\
\
## Ejercicio 2\
C\'e1lculo del retorno esperado y volatilidad de los portafolios P1 y P2, comparaci\'f3n entre modelos de IA y an\'e1lisis financiero correspondiente.\
\
## Ejercicio 3\
Construcci\'f3n de un motor de decisi\'f3n para solicitudes de retiro con clasificaci\'f3n `APPROVE`, `HOLD` y `REJECT`, incluyendo archivo de review y outputs generados.\
\
## Ejercicio 4\
Implementaci\'f3n de un prototipo funcional de chatbot ACH en Python CLI, con:\
- lookup de routing number,\
- flujo conversacional determin\'edstico,\
- simulaci\'f3n de escenarios `success`, `R01` y `R03`,\
- y transcripts generados como evidencia.\
\
## C\'f3mo correr el bot del ejercicio 4\
Desde la ra\'edz del proyecto:\
\
```bash\
source .venv/bin/activate\
python src/ach_bot.py --scenario success\
python src/ach_bot.py --scenario r01\
python src/ach_bot.py --scenario r03}