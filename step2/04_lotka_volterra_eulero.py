"""
CONIGLI E LEPRE: LE EQUAZIONI DI LOTKA-VOLTERRA (VERSIONE MATPLOTLIB)
=======================================================================

Questa e' la stessa simulazione di 02_lotka_volterra.py (la finestra
pygame), ma disegnata con Matplotlib, la libreria che usiamo fin
dall'inizio del laboratorio per i grafici.

Le equazioni sono sempre le stesse:

    dR/dt = a*R - b*R*F        (R = conigli, F = volpi)
    dF/dt = c*R*F - d*F

A sinistra in alto c'e' lo SPAZIO DELLE FASI (volpi rispetto a
conigli): il punto viola disegna un "anello", perche' le due
popolazioni continuano a ciclare fra gli stessi valori. Il cerchietto
nero e' il punto di equilibrio (dove conigli e volpi smetterebbero di
cambiare). In basso c'e' l'andamento nel tempo delle due popolazioni.
A destra ci sono 4 cursori per cambiare i parametri a, b, c, d anche
mentre l'animazione e' in corso, piu' due pulsanti per mettere in
pausa e per ricominciare.

NOTA TECNICA: usa la libreria "matplotlib" (già presente nel nostro
ambiente virtuale). Si esegue come un normale script Python, senza
bisogno di pygame:

    .\\.venv\\Scripts\\python.exe step2\\02_lotka_volterra_matplotlib.py
"""

from collections import deque

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider

# ---------------------------------------------------------------
# 1) PARAMETRI INIZIALI DEL MODELLO
# ---------------------------------------------------------------
R0_INIZIALE = 10.0   # conigli all'inizio
F0_INIZIALE = 12.0    # volpi all'inizio

POPOLAZIONE_MINIMA = 0.1  # evita numeri negativi o nulli per errori di calcolo

DT_SOTTOPASSO = 0.03              # durata di un piccolissimo passo di tempo
SOTTOPASSI_PER_FOTOGRAMMA = 5     # quanti passi calcoliamo ad ogni fotogramma
LUNGHEZZA_STORIA = 2000           # quanti punti "ricordiamo" per disegnare le curve


# ---------------------------------------------------------------
# 2) LE EQUAZIONI DEL MODELLO (identiche alla versione pygame)
# ---------------------------------------------------------------
def derivate(R, F, a, b, c, d):
    """Di quanto cambiano conigli e volpi in questo istante."""
    dR = a * R * (1-R/100)- b * R * F
    dF = c * R * F - d * F
    return dR, dF


def passo_rk4(R, F, a, b, c, d, dt):
    # "Runge-Kutta 4": guardiamo la direzione del cambiamento in 4
    # punti vicini e le combiniamo, per fare un passo molto piu'
    # preciso di un semplice "R = R + dR*dt".
    k1R, k1F = derivate(R, F, a, b, c, d)
    k2R, k2F = derivate(R + dt / 2 * k1R, F + dt / 2 * k1F, a, b, c, d)
    k3R, k3F = derivate(R + dt / 2 * k2R, F + dt / 2 * k2F, a, b, c, d)
    k4R, k4F = derivate(R + dt * k3R, F + dt * k3F, a, b, c, d)

    R_nuovo = R + dt / 6 * (k1R + 2 * k2R + 2 * k3R + k4R)
    F_nuovo = F + dt / 6 * (k1F + 2 * k2F + 2 * k3F + k4F)

    # derivata "semplice" 
    # dR_dt, dF_dt = derivate(R, F, a, b, c, d)
    # R_nuovo = R + dt * dR_dt
    # F_nuovo = F + dt * dF_dt


    return max(R_nuovo, POPOLAZIONE_MINIMA), max(F_nuovo, POPOLAZIONE_MINIMA)


# ---------------------------------------------------------------
# 3) STATO DELLA SIMULAZIONE E "STORIA" DA DISEGNARE
# ---------------------------------------------------------------
stato = {"R": R0_INIZIALE, "F": F0_INIZIALE, "in_pausa": False}
storia_R = deque([R0_INIZIALE], maxlen=LUNGHEZZA_STORIA)
storia_F = deque([F0_INIZIALE], maxlen=LUNGHEZZA_STORIA)
storia_tempo = deque([0.0], maxlen=LUNGHEZZA_STORIA)


def ricomincia(evento=None):
    stato["R"] = R0_INIZIALE
    stato["F"] = F0_INIZIALE
    stato["in_pausa"] = False
    pulsante_pausa.label.set_text("Pausa")
    storia_R.clear()
    storia_F.clear()
    storia_tempo.clear()
    storia_R.append(R0_INIZIALE)
    storia_F.append(F0_INIZIALE)
    storia_tempo.append(0.0)


def metti_in_pausa(evento=None):
    stato["in_pausa"] = not stato["in_pausa"]
    pulsante_pausa.label.set_text("Riprendi" if stato["in_pausa"] else "Pausa")


# ---------------------------------------------------------------
# 4) FINESTRA: 2 grafici a sinistra, cursori e pulsanti a destra
# ---------------------------------------------------------------
figura = plt.figure(figsize=(11, 6.5))
figura.suptitle("Conigli e volpi - le equazioni di Lotka-Volterra", fontsize=13)

assi_fase = figura.add_axes((0.08, 0.40, 0.55, 0.50))
assi_tempo = figura.add_axes((0.08, 0.08, 0.55, 0.24))

assi_fase.set_title("Spazio delle fasi: volpi (F) rispetto a conigli (R)")
assi_fase.set_xlabel("Conigli (R)")
assi_fase.set_ylabel("volpi (F)")

assi_tempo.set_title("Conigli (blu) e volpi (rosso) nel tempo")
assi_tempo.set_xlabel("Tempo")
assi_tempo.set_ylabel("Popolazione")

linea_traiettoria, = assi_fase.plot([], [], color="purple", linewidth=1.5)
punto_attuale, = assi_fase.plot([], [], marker="o", color="purple", markersize=8)
punto_equilibrio, = assi_fase.plot([], [], marker="o", color="black",
                                    markersize=9, markerfacecolor="none")

linea_conigli, = assi_tempo.plot([], [], color="tab:blue", label="Conigli")
linea_volpi, = assi_tempo.plot([], [], color="tab:red", label="volpi")
assi_tempo.legend(loc="upper right")

# --- cursori dei 4 parametri, sulla destra della finestra ---
cursore_a = Slider(figura.add_axes((0.74, 0.80, 0.20, 0.03)), "a", 0.0, 2.0, valinit=1.0)
cursore_b = Slider(figura.add_axes((0.74, 0.68, 0.20, 0.03)), "b", 0.0, 0.3, valinit=0.10)
cursore_c = Slider(figura.add_axes((0.74, 0.56, 0.20, 0.03)), "c", 0.0, 0.3, valinit=0.10)
cursore_d = Slider(figura.add_axes((0.74, 0.44, 0.20, 0.03)), "d", 0.0, 2.0, valinit=1.0)

# --- pulsanti pausa/ricomincia ---
pulsante_pausa = Button(figura.add_axes((0.74, 0.30, 0.09, 0.05)), "Pausa")
pulsante_reset = Button(figura.add_axes((0.85, 0.30, 0.09, 0.05)), "Ricomincia")
pulsante_pausa.on_clicked(metti_in_pausa)
pulsante_reset.on_clicked(ricomincia)


# ---------------------------------------------------------------
# 5) FUNZIONE CHIAMATA AD OGNI FOTOGRAMMA DELL'ANIMAZIONE
# ---------------------------------------------------------------
def aggiorna(fotogramma):
    a, b, c, d = cursore_a.val, cursore_b.val, cursore_c.val, cursore_d.val

    if not stato["in_pausa"]:
        R, F = stato["R"], stato["F"]
        for _ in range(SOTTOPASSI_PER_FOTOGRAMMA):
            R, F = passo_rk4(R, F, a, b, c, d, DT_SOTTOPASSO)
        stato["R"], stato["F"] = R, F

        storia_tempo.append(storia_tempo[-1] + DT_SOTTOPASSO * SOTTOPASSI_PER_FOTOGRAMMA)
        storia_R.append(R)
        storia_F.append(F)

    # --- spazio delle fasi ---
    linea_traiettoria.set_data(list(storia_R), list(storia_F))
    punto_attuale.set_data([storia_R[-1]], [storia_F[-1]])
    punto_equilibrio.set_data([d / c] if c > 0 else [], [a / b] if b > 0 else [])
    assi_fase.relim()
    assi_fase.autoscale_view()

    # --- andamento nel tempo ---
    linea_conigli.set_data(list(storia_tempo), list(storia_R))
    linea_volpi.set_data(list(storia_tempo), list(storia_F))
    assi_tempo.relim()
    assi_tempo.autoscale_view()

    return linea_traiettoria, punto_attuale, punto_equilibrio, linea_conigli, linea_volpi


animazione = FuncAnimation(figura, aggiorna, interval=30, blit=False, cache_frame_data=False)

plt.show()
