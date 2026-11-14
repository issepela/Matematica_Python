"""
LA MAPPA LOGISTICA: DALLA POPOLAZIONE NEL TEMPO ALLA POPOLAZIONE FINALE
=======================================================================

L'IDEA (spiegata semplice):
Riprendiamo il file precedente (02) e aggiungiamo un secondo grafico.

    x(nuovo) = r * x * (1 - x)

A SINISTRA c'e' la solita popolazione nel tempo, per un certo r e una
certa popolazione iniziale x0.

A DESTRA, per ogni r che proviamo, segniamo con dei puntini verdi dove
va a finire la popolazione dopo tanti anni (la popolazione FINALE):

    - se la popolazione si stabilizza, c'e' UN solo puntino;
    - se alterna "tanti" e "pochi", ci sono DUE puntini;
    - se alterna fra 4 valori, ci sono QUATTRO puntini; e cosi' via.

Man mano che muovi r, a destra si disegna una curva. Fino a r = 3 e' una
linea sola, poi... si SPEZZA in due: e' la prima "biforcazione".

COSA PROVARE
    1) Trascina il cursore r lentamente da 0 a 4 e guarda il grafico
       di destra che si riempie.
    2) Oppure premi "Scansiona r": il programma fa tutto da solo.
    3) Cambia x0: il grafico di destra cambia? (Spoiler: no! La
       popolazione finale dipende da r, non da x0.)
    4) Trova a occhio il valore di r in cui la linea si spezza in due.

COMANDI
    cursore r   -> tasso di crescita (da 0 a 4)
    cursore x0  -> popolazione iniziale (da 0.01 a 0.99)
    Pausa       -> ferma / fa ripartire l'animazione
    Ricomincia  -> rifa' partire la linea di sinistra da x0
    Cancella    -> toglie le linee vecchie e i puntini di destra
    Scansiona r -> fa scorrere r da 0 a 4 riempiendo il grafico di destra

    .\\.venv\\Scripts\\python.exe step3_preview\\03_mappa_logistica_tempo_e_finale.py
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider

# ---------------------------------------------------------------
# 1) PARAMETRI INIZIALI
# ---------------------------------------------------------------
R_INIZIALE = 2.6
X0_INIZIALE = 0.04
N_PASSI = 40                 # quanti anni mostriamo a sinistra
MILLISECONDI_PER_ANNO = 150

ANNI_DI_ASSESTAMENTO = 1000  # anni "buttati via" prima di guardare la popolazione finale
PUNTI_PER_R = 20             # quanti anni finali segniamo a destra per ogni r

PASSO_SCANSIONE = 0.005      # di quanto aumenta r a ogni "timbro" durante la scansione
TIMBRI_PER_FOTOGRAMMA = 10


# ---------------------------------------------------------------
# 2) LA FORMULA
# ---------------------------------------------------------------
def logistica(x, r):
    """La popolazione dell'anno dopo, data quella di quest'anno."""
    return r * x * (1 - x)


def calcola_traiettoria(x0, r, n_passi):
    valori = [x0]
    for _ in range(n_passi):
        valori.append(logistica(valori[-1], r))
    return valori


def popolazione_finale(x0, r):
    """Lascia passare tanti anni e restituisce i valori in cui la popolazione si e' assestata."""
    x = x0
    for _ in range(ANNI_DI_ASSESTAMENTO):
        x = logistica(x, r)
    finali = []
    for _ in range(PUNTI_PER_R):
        x = logistica(x, r)
        finali.append(x)
    return finali


# ---------------------------------------------------------------
# 3) STATO DELLA SIMULAZIONE
# ---------------------------------------------------------------
stato = {
    "valori": [X0_INIZIALE],
    "linea": None,
    "vecchie": [],
    "in_pausa": False,
    "scansione": False,
}
punti_r = []   # i "puntini" di destra: ascissa (r)...
punti_x = []   # ...e ordinata (popolazione finale)

COLORI = plt.get_cmap("tab10").colors

# ---------------------------------------------------------------
# 4) FINESTRA: a sinistra il tempo, a destra la popolazione finale
# ---------------------------------------------------------------
figura = plt.figure(figsize=(12, 6.5))
figura.suptitle("La mappa logistica: x(nuovo) = r * x * (1 - x)", fontsize=13)

assi_tempo = figura.add_axes((0.06, 0.32, 0.43, 0.58))
assi_tempo.set_title("Popolazione nel tempo")
assi_tempo.set_xlabel("Tempo (anni)")
assi_tempo.set_ylabel("Popolazione")
assi_tempo.set_xlim(-0.5, N_PASSI + 0.5)
assi_tempo.set_ylim(0, 1)
assi_tempo.grid(True, alpha=0.3)

assi_finale = figura.add_axes((0.56, 0.32, 0.40, 0.58))
assi_finale.set_title("Popolazione finale per ogni r")
assi_finale.set_xlabel("Tasso di crescita r")
assi_finale.set_ylabel("Popolazione finale")
assi_finale.set_xlim(0, 4)
assi_finale.set_ylim(0, 1)
assi_finale.grid(True, alpha=0.3)

puntini, = assi_finale.plot([], [], linestyle="", marker=".", markersize=2, color="seagreen")
riga_r_attuale = assi_finale.axvline(R_INIZIALE, color="tab:red", linewidth=1)

cursore_r = Slider(figura.add_axes((0.10, 0.19, 0.42, 0.03)), "r", 0.0, 4.0,
                   valinit=R_INIZIALE, valstep=0.01)
cursore_x0 = Slider(figura.add_axes((0.10, 0.12, 0.42, 0.03)), "x0", 0.01, 0.99,
                    valinit=X0_INIZIALE, valstep=0.01)

pulsante_pausa = Button(figura.add_axes((0.60, 0.17, 0.08, 0.06)), "Pausa")
pulsante_reset = Button(figura.add_axes((0.70, 0.17, 0.08, 0.06)), "Ricomincia")
pulsante_cancella = Button(figura.add_axes((0.80, 0.17, 0.08, 0.06)), "Cancella")
pulsante_scansione = Button(figura.add_axes((0.60, 0.08, 0.28, 0.06)), "Scansiona r da 0 a 4")


# ---------------------------------------------------------------
# 5) I PUNTINI DI DESTRA
# ---------------------------------------------------------------
def timbra(r):
    """Segna a destra dove va a finire la popolazione per questo r."""
    for x in popolazione_finale(cursore_x0.val, r):
        punti_r.append(r)
        punti_x.append(x)
    puntini.set_data(punti_r, punti_x)


# ---------------------------------------------------------------
# 6) COSA SUCCEDE QUANDO TOCCHI UN COMANDO
# ---------------------------------------------------------------
def nuova_linea():
    x0, r = cursore_x0.val, cursore_r.val
    colore = COLORI[len(stato["vecchie"]) % len(COLORI)]
    # Durante la scansione r cambia di continuo: mostriamo subito tutti gli anni.
    valori = calcola_traiettoria(x0, r, N_PASSI) if stato["scansione"] else [x0]
    stato["valori"] = valori
    stato["linea"], = assi_tempo.plot(range(len(valori)), valori, marker="o",
                                      color=colore, label=f"x0 = {x0:.2f}")
    assi_tempo.legend(loc="upper right")


def metti_da_parte_la_linea():
    stato["linea"].set_alpha(0.35)
    stato["vecchie"].append(stato["linea"])


def cancella_le_vecchie(evento=None):
    for linea in stato["vecchie"]:
        linea.remove()
    stato["vecchie"].clear()


def cancella_tutto(evento=None):
    cancella_le_vecchie()
    punti_r.clear()
    punti_x.clear()
    puntini.set_data([], [])


def cambia_x0(valore):
    metti_da_parte_la_linea()
    nuova_linea()


def cambia_r(valore):
    stato["linea"].remove()
    cancella_le_vecchie()
    nuova_linea()
    riga_r_attuale.set_xdata([valore, valore])
    timbra(valore)


def ricomincia(evento=None):
    stato["linea"].remove()
    nuova_linea()


def metti_in_pausa(evento=None):
    stato["in_pausa"] = not stato["in_pausa"]
    pulsante_pausa.label.set_text("Riprendi" if stato["in_pausa"] else "Pausa")


def avvia_scansione(evento=None):
    stato["scansione"] = True
    cursore_r.set_val(0.0)


cursore_r.on_changed(cambia_r)
cursore_x0.on_changed(cambia_x0)
pulsante_pausa.on_clicked(metti_in_pausa)
pulsante_reset.on_clicked(ricomincia)
pulsante_cancella.on_clicked(cancella_tutto)
pulsante_scansione.on_clicked(avvia_scansione)


# ---------------------------------------------------------------
# 7) FUNZIONE CHIAMATA AD OGNI FOTOGRAMMA
# ---------------------------------------------------------------
def aggiorna(fotogramma):
    if stato["scansione"]:
        r = cursore_r.val
        # i primi timbri li facciamo "di nascosto", l'ultimo lo fa il cursore
        for _ in range(TIMBRI_PER_FOTOGRAMMA - 1):
            r += PASSO_SCANSIONE
            timbra(r)
        r += PASSO_SCANSIONE
        if r >= 4.0:
            stato["scansione"] = False
            r = 4.0
        cursore_r.set_val(r)
        return (stato["linea"], puntini)

    valori = stato["valori"]
    if not stato["in_pausa"] and len(valori) <= N_PASSI:
        valori.append(logistica(valori[-1], cursore_r.val))

    stato["linea"].set_data(range(len(valori)), valori)
    return (stato["linea"], puntini)


nuova_linea()
timbra(R_INIZIALE)
animazione = FuncAnimation(figura, aggiorna, interval=MILLISECONDI_PER_ANNO,
                           blit=False, cache_frame_data=False)

plt.show()
