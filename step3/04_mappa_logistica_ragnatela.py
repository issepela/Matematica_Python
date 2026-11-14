"""
LA MAPPA LOGISTICA: LA RAGNATELA FRA PARABOLA E BISETTRICE
=======================================================================

L'IDEA (spiegata semplice):
La formula della mappa logistica

    x(nuovo) = r * x * (1 - x)

si puo' DISEGNARE. Mettiamo la popolazione di quest'anno sull'asse
orizzontale (x) e quella dell'anno dopo sull'asse verticale (y):

    - la PARABOLA blu e' la formula: y = r * x * (1 - x).
      Dato x, ti dice quanto vale x l'anno dopo;
    - la RETTA tratteggiata (la "bisettrice") e' y = x. Serve a
      "riportare" il risultato sull'asse orizzontale, per ripetere
      la formula l'anno dopo.

Il pallino rosso fa questo gioco, a ripetizione:

    1) parte da x sulla bisettrice;
    2) si muove IN VERTICALE fino alla parabola: ha calcolato il valore
       dell'anno dopo;
    3) si muove IN ORIZZONTALE fino alla bisettrice: il risultato diventa
       il nuovo x;
    4) ricomincia dal punto 2.

Il disegno che resta sullo schermo sembra una RAGNATELA. A destra vedi
la stessa storia come popolazione nel tempo (come nel file 02).

COSA PROVARE
    1) Con r = 2.6 la ragnatela si avvolge a spirale verso il punto in cui
       la parabola incontra la bisettrice (cerchietto nero): e' il PUNTO
       FISSO, cioe' la popolazione in cui, una volta arrivati, si resta.
    2) Con r = 3.3 il pallino non si ferma piu': gira su un rettangolo.
       Sono i due valori fra cui la popolazione oscilla.
    3) Con r = 3.9 la ragnatela diventa un groviglio: caos.
    4) Guarda cosa cambia passando da r = 2.9 a r = 3.1: il cerchietto
       nero e' sempre li', ma la ragnatela smette di avvicinarsi e
       comincia ad allontanarsi. Sopra r = 3 la parabola, nel punto
       fisso, e' troppo "ripida" e il punto fisso non regge piu'.

COMANDI
    cursore r   -> tasso di crescita (da 0 a 4)
    cursore x0  -> popolazione iniziale (da 0.01 a 0.99)
    Pausa       -> ferma / fa ripartire l'animazione
    Ricomincia  -> ridisegna la ragnatela da capo

NOTA TECNICA: usa solo "matplotlib". Si esegue come un normale script:

    .\\.venv\\Scripts\\python.exe step3_preview\\04_mappa_logistica_ragnatela.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider

# ---------------------------------------------------------------
# 1) PARAMETRI INIZIALI
# ---------------------------------------------------------------
R_INIZIALE = 2.6
X0_INIZIALE = 0.2
N_PASSI = 60                # quanti anni disegniamo
MILLISECONDI_PER_MOSSA = 120


def logistica(x, r):
    """La popolazione dell'anno dopo, data quella di quest'anno."""
    return r * x * (1 - x)


# ---------------------------------------------------------------
# 2) STATO DELLA SIMULAZIONE
# ---------------------------------------------------------------
stato = {
    "x": X0_INIZIALE,           # popolazione attuale
    "in_verticale": True,       # il prossimo movimento e' verso la parabola?
    "ragnatela_x": [X0_INIZIALE],
    "ragnatela_y": [X0_INIZIALE],
    "anni": [0],
    "popolazioni": [X0_INIZIALE],
    "in_pausa": False,
}

# ---------------------------------------------------------------
# 3) FINESTRA: a sinistra la ragnatela, a destra il tempo
# ---------------------------------------------------------------
figura = plt.figure(figsize=(12, 6.5))
figura.suptitle("La mappa logistica: la ragnatela", fontsize=13)

assi_mappa = figura.add_axes((0.06, 0.30, 0.38, 0.60))
assi_mappa.set_title("Parabola, bisettrice e pallino")
assi_mappa.set_xlabel("Popolazione quest'anno (x)")
assi_mappa.set_ylabel("Popolazione l'anno dopo")
assi_mappa.set_xlim(-3, 3)
assi_mappa.set_ylim(-3, 3)
assi_mappa.set_aspect("equal")
assi_mappa.grid(True, alpha=0.3)

assi_tempo = figura.add_axes((0.56, 0.30, 0.40, 0.60))
assi_tempo.set_title("La stessa storia nel tempo")
assi_tempo.set_xlabel("Tempo (anni)")
assi_tempo.set_ylabel("Popolazione")
assi_tempo.set_xlim(-0.5, N_PASSI + 0.5)
assi_tempo.set_ylim(0, 1)
assi_tempo.grid(True, alpha=0.3)

x_curva = np.linspace(-3, 3, 300)
linea_parabola, = assi_mappa.plot(x_curva, logistica(x_curva, R_INIZIALE),
                                  color="tab:blue", linewidth=2, label="parabola: r*x*(1-x)")
assi_mappa.plot([-3, 3], [-3, 3], color="black", linestyle="--", label="bisettrice: y = x")
linea_ragnatela, = assi_mappa.plot([], [], color="gray", linewidth=0.8)
punto_fisso, = assi_mappa.plot([], [], marker="o", color="black", markersize=10,
                               markerfacecolor="none", linestyle="", label="punto fisso")
pallino, = assi_mappa.plot([], [], marker="o", color="tab:red", markersize=9, linestyle="")
assi_mappa.legend(loc="upper left", fontsize=8)

linea_tempo, = assi_tempo.plot([], [], marker="o", color="tab:green")

cursore_r = Slider(figura.add_axes((0.10, 0.17, 0.38, 0.03)), "r", 0.0, 5.0,
                   valinit=R_INIZIALE, valstep=0.01)
cursore_x0 = Slider(figura.add_axes((0.10, 0.10, 0.38, 0.03)), "x0", 0.01, 0.99,
                    valinit=X0_INIZIALE, valstep=0.01)

pulsante_pausa = Button(figura.add_axes((0.58, 0.12, 0.10, 0.06)), "Pausa")
pulsante_reset = Button(figura.add_axes((0.70, 0.12, 0.12, 0.06)), "Ricomincia")


# ---------------------------------------------------------------
# 4) COSA SUCCEDE QUANDO TOCCHI UN COMANDO
# ---------------------------------------------------------------
def ricomincia(valore=None):
    r, x0 = cursore_r.val, cursore_x0.val
    stato["x"] = x0
    stato["in_verticale"] = True
    stato["ragnatela_x"] = [x0]
    stato["ragnatela_y"] = [x0]
    stato["anni"] = [0]
    stato["popolazioni"] = [x0]

    linea_parabola.set_ydata(logistica(x_curva, r))
    if r > 1:
        x_fisso = 1 - 1 / r      # qui r*x*(1-x) = x
        punto_fisso.set_data([x_fisso], [x_fisso])
    else:
        punto_fisso.set_data([], [])


def metti_in_pausa(evento=None):
    stato["in_pausa"] = not stato["in_pausa"]
    pulsante_pausa.label.set_text("Riprendi" if stato["in_pausa"] else "Pausa")


cursore_r.on_changed(ricomincia)
cursore_x0.on_changed(ricomincia)
pulsante_pausa.on_clicked(metti_in_pausa)
pulsante_reset.on_clicked(ricomincia)


# ---------------------------------------------------------------
# 5) FUNZIONE CHIAMATA AD OGNI FOTOGRAMMA: una mossa del pallino
# ---------------------------------------------------------------
def aggiorna(fotogramma):
    r = cursore_r.val
    x = stato["x"]

    if not stato["in_pausa"] and stato["anni"][-1] < N_PASSI:
        if stato["in_verticale"]:
            # dalla bisettrice su (o giu') fino alla parabola
            stato["ragnatela_x"].append(x)
            stato["ragnatela_y"].append(logistica(x, r))
        else:
            # dalla parabola, di lato, fino alla bisettrice: e' passato un anno
            x = logistica(x, r)
            stato["x"] = x
            stato["ragnatela_x"].append(x)
            stato["ragnatela_y"].append(x)
            stato["anni"].append(stato["anni"][-1] + 1)
            stato["popolazioni"].append(x)
        stato["in_verticale"] = not stato["in_verticale"]

    linea_ragnatela.set_data(stato["ragnatela_x"], stato["ragnatela_y"])
    pallino.set_data([stato["ragnatela_x"][-1]], [stato["ragnatela_y"][-1]])
    linea_tempo.set_data(stato["anni"], stato["popolazioni"])
    return linea_ragnatela, pallino, linea_tempo


ricomincia()
animazione = FuncAnimation(figura, aggiorna, interval=MILLISECONDI_PER_MOSSA,
                           blit=False, cache_frame_data=False)

plt.show()
