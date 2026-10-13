"""
CONIGLI E LEPRE: LE EQUAZIONI DI LOTKA-VOLTERRA (VERSIONE STATICA)
=====================================================================

Questa e' la versione piu' semplice possibile della simulazione: niente
animazione, niente cursori. Calcoliamo prima TUTTA la storia delle due
popolazioni (X e Y) dall'inizio alla fine, e solo alla fine disegniamo
i due grafici con Matplotlib.

Le equazioni sono sempre le stesse (qui chiamiamo le due popolazioni
X prede e Y predatori):

    dX/dt = a*X - b*X*Y
    dY/dt = c*X*Y - d*Y

"""

import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# 1) PARAMETRI DEL MODELLO E DELLA SIMULAZIONE
# ---------------------------------------------------------------
a, b, c, d = 1.0, 0.10, 0.10, 1.0

X0_INIZIALE = 10.0   # conigli all'inizio
Y0_INIZIALE = 12.0   # volpi all'inizio

POPOLAZIONE_MINIMA = 0.1   # evita numeri negativi o nulli per errori di calcolo

DT_SOTTOPASSO = 0.001   # durata di un piccolissimo passo di tempo
NUMERO_PASSI = 20000   # quanti passi calcoliamo in totale (= tempo finale / DT_SOTTOPASSO)


# ---------------------------------------------------------------
# 2) LE EQUAZIONI DEL MODELLO
# ---------------------------------------------------------------
def passo(X, Y, a, b, c, d, dt):
    dX = a * X - b * X * Y
    dY = c * X * Y - d * Y

    X_nuovo = X + dt * dX
    Y_nuovo = Y + dt * dY

    return max(X_nuovo, POPOLAZIONE_MINIMA), max(Y_nuovo, POPOLAZIONE_MINIMA)


# ---------------------------------------------------------------
# 3) CALCOLIAMO TUTTA LA STORIA, PRIMA DI DISEGNARE
# ---------------------------------------------------------------
storia_X = [X0_INIZIALE]
storia_Y = [Y0_INIZIALE]
storia_tempo = [0.0]

X, Y, tempo = X0_INIZIALE, Y0_INIZIALE, 0.0
for _ in range(NUMERO_PASSI):
    X, Y = passo(X, Y, a, b, c, d, DT_SOTTOPASSO)
    tempo += DT_SOTTOPASSO
    storia_X.append(X)
    storia_Y.append(Y)
    storia_tempo.append(tempo)


# ---------------------------------------------------------------
# 4) DISEGNIAMO I DUE GRAFICI CON MATPLOTLIB
# ---------------------------------------------------------------
figura, (assi_fase, assi_tempo) = plt.subplots(1, 2, figsize=(12, 5.5))
figura.suptitle("Conigli e volpi - le equazioni di Lotka-Volterra (versione statica)", fontsize=13)

# --- spazio delle fasi: Y rispetto a X ---
assi_fase.plot(storia_X, storia_Y, color="purple", linewidth=1)
assi_fase.plot(d / c, a / b, marker="o", color="black", markersize=9, markerfacecolor="none")
assi_fase.set_title("Spazio delle fasi: Predatori rispetto a Prede")
assi_fase.set_xlabel("prede")
assi_fase.set_ylabel("predatori")

# --- andamento nel tempo ---
assi_tempo.plot(storia_tempo, storia_X, color="tab:blue", label="prede")
assi_tempo.plot(storia_tempo, storia_Y, color="tab:red", label="predatori")
assi_tempo.set_title("Prede e predatori nel tempo")
assi_tempo.set_xlabel("Tempo")
assi_tempo.set_ylabel("Popolazione")
assi_tempo.legend(loc="upper right")

plt.tight_layout()
plt.show()
