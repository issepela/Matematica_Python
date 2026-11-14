"""
LA MAPPA LOGISTICA: IL DIAGRAMMA DI BIFORCAZIONE
=======================================================================

L'IDEA (spiegata semplice):
Nei file precedenti abbiamo visto che, per ogni tasso di crescita r,
la popolazione dopo tanti anni:

    - si stabilizza su UN valore,
    - oppure oscilla fra 2, 4, 8... valori,
    - oppure non si ripete mai (caos).

Adesso mettiamo TUTTE le risposte in un unico disegno:

    orizzontale -> il tasso di crescita r
    verticale   -> i valori che la popolazione tocca "alla fine"

Per ogni r il programma:

    1) parte da una popolazione qualsiasi;
    2) applica la formula 1000 volte, senza disegnare niente (aspetta che
       la popolazione si assesti, il "transitorio");
    3) applica la formula ancora 100 volte e disegna un puntino ogni volta.

Per farlo per 1500 valori di r in un attimo usiamo NumPy, che calcola
tutti gli r insieme come se fossero una lista unica.

Il disegno ottenuto si chiama DIAGRAMMA DI BIFORCAZIONE:

    r < 1        -> la popolazione si estingue
    1 < r < 3    -> un solo valore, che cresce con r
    r = 3        -> PRIMA BIFORCAZIONE: la linea si spezza in due
    r = 3.449... -> ogni ramo si spezza ancora: 4 valori
    ...          -> raddoppi sempre piu' ravvicinati (8, 16, 32...)
    r = 3.57...  -> comincia il CAOS
    r = 3.83...  -> nel mezzo del caos, una "finestra" con un ciclo di 3 valori!

COSA PROVARE
    1) Guarda il diagramma intero e trova le biforcazioni.
    2) ingrandisci una zona: la forma
       si RIPETE a scale sempre piu' piccole (e' un frattale).
    3) Ingrandisci la finestra del ciclo di 3 valori (r fra 3.82 e 3.86).

    .\\.venv\\Scripts\\python.exe step3_preview\\05_diagramma_biforcazione.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

# ---------------------------------------------------------------
# 1) PARAMETRI
# ---------------------------------------------------------------
N_VALORI_R = 1500             # quanti valori di r proviamo
ANNI_DI_ASSESTAMENTO = 1000   # anni "buttati via" (il transitorio)
PUNTI_PER_R = 100             # anni che disegniamo per ogni r
X_INIZIALE = 0.3              # la popolazione iniziale (non conta!)

R_MIN = 3.82                  # valore minimo di r
R_MAX = 3.86                  # valore massimo di r
    
if R_MIN >= R_MAX:
    raise ValueError("R_MIN deve essere minore di R_MAX")

# ---------------------------------------------------------------
# 2) IL CALCOLO: tutti gli r insieme grazie a NumPy
# ---------------------------------------------------------------

r = np.linspace(R_MIN, R_MAX, N_VALORI_R)
x = np.full(N_VALORI_R, X_INIZIALE)

for _ in range(ANNI_DI_ASSESTAMENTO):
    x = r * x * (1 - x)           # la solita formula, per tutti gli r insieme

punti_r = []
punti_x = []
for _ in range(PUNTI_PER_R):
    x = r * x * (1 - x)
    punti_r.append(r)
    punti_x.append(x)

punti_r = np.concatenate(punti_r)  # trasformiamo la lista di array in un unico array
punti_x = np.concatenate(punti_x)   


# ---------------------------------------------------------------
# 4) DISEGNA IL DIAGRAMMA PER L'INTERVALLO SCELTO
# ---------------------------------------------------------------
figura = plt.figure(figsize=(11, 7))
figura.suptitle("Diagramma di biforcazione della mappa logistica", fontsize=13)

assi = figura.add_axes((0.08, 0.28, 0.88, 0.62))
assi.set_xlabel("Tasso di crescita r")
assi.set_ylabel("Popolazione finale")
assi.grid(True, alpha=0.3)

assi.plot(punti_r, punti_x, linestyle="", marker=".", markersize=1, color="black", alpha=0.4)   
plt.show()
