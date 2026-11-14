"""
LA MAPPA LOGISTICA: LA POPOLAZIONE NEL TEMPO
=======================================================================


COSA PROVARE
    1) Lascia r = 2.6 e cambia x0 con il cursore. Ogni volta parte una
       nuova linea colorata, e le vecchie restano un po' sbiadite.
       Parti da pochi conigli o da tantissimi: la popolazione FINALE e'
       sempre la stessa!
    2) Ora muovi r (le linee vecchie vengono cancellate, perche' con un
       r diverso non si possono piu' confrontare):
         - r sotto 1  -> i conigli si estinguono
         - r fra 1 e 3 -> la popolazione si stabilizza su un valore
         - r poco sopra 3 -> la popolazione NON si stabilizza piu':
                             alterna un anno "tanti" e un anno "pochi"
         - r sempre piu' grande -> alterna fra 4 valori, poi 8, ...
                                   e poi sembra casuale (caos!)
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider

# ---------------------------------------------------------------
# 1) PARAMETRI INIZIALI
# ---------------------------------------------------------------
R_INIZIALE = 2.6      # tasso di crescita
X0_INIZIALE = 0.04    # popolazione iniziale (0 = vuoto, 1 = prato pieno)
N_PASSI = 40          # quanti anni simuliamo
MILLISECONDI_PER_ANNO = 150


# ---------------------------------------------------------------
# 2) LA FORMULA: tutta la matematica sta in queste due righe
# ---------------------------------------------------------------
def logistica(x, r):
    """La popolazione dell'anno dopo, data quella di quest'anno."""
    return r * x * (1 - x)


def calcola_traiettoria(x0, r, n_passi):
    """Applica la formula n_passi volte e ricorda tutti i valori."""
    valori = [x0]
    for _ in range(n_passi):
        valori.append(logistica(valori[-1], r))
    return valori


# ---------------------------------------------------------------
# 3) CHE COMPORTAMENTO HA? (serve solo per scrivere il messaggio)
# ---------------------------------------------------------------
def descrivi_comportamento(x0, r):
    # Prima lasciamo passare tanti anni, finche' la popolazione si e' assestata...
    x = x0
    for _ in range(20000):
        x = logistica(x, r)
    # ...poi guardiamo i 64 anni successivi.
    ultimi = [x]
    for _ in range(63):
        ultimi.append(logistica(ultimi[-1], r))

    # Se dopo "p" anni la popolazione e' tornata uguale, il ciclo dura p anni.
    for p in range(1, 33):
        if all(abs(ultimi[i + p] - ultimi[i]) < 1e-4 for i in range(32)):
            if p == 1 and ultimi[-1] < 0.001:
                return "I conigli si estinguono: la popolazione finale e' 0"
            # Per r = 3 esatto i due valori sono quasi uguali: la popolazione si sta ancora assestando.
            if p == 1 or max(ultimi) - min(ultimi) < 0.01:
                return f"La popolazione si stabilizza su {ultimi[-1]:.3f}"
            valori = sorted(set(round(v, 3) for v in ultimi[:p]))
            elenco = ", ".join(f"{v:.3f}" for v in valori)
            return f"La popolazione oscilla fra {p} valori: {elenco}"
    return "La popolazione non si ripete mai: comportamento caotico"


# ---------------------------------------------------------------
# 4) STATO DELLA SIMULAZIONE
# ---------------------------------------------------------------
stato = {
    "valori": [X0_INIZIALE],   # la linea che si sta disegnando adesso
    "linea": None,             # il suo "disegno" in Matplotlib
    "vecchie": [],             # le linee dei tentativi precedenti
    "in_pausa": False,
}

COLORI = plt.get_cmap("tab10").colors

# ---------------------------------------------------------------
# 5) FINESTRA: il grafico sopra, cursori e pulsanti sotto
# ---------------------------------------------------------------
figura = plt.figure(figsize=(11, 6.5))
figura.suptitle("La mappa logistica: x(nuovo) = r * x * (1 - x)", fontsize=13)

assi = figura.add_axes((0.08, 0.32, 0.88, 0.58))
assi.set_title("Popolazione nel tempo")
assi.set_xlabel("Tempo (anni)")
assi.set_ylabel("Popolazione")
assi.set_xlim(-0.5, N_PASSI + 0.5)
assi.set_ylim(0, 1)
assi.grid(True, alpha=0.3)

cursore_r = Slider(figura.add_axes((0.12, 0.19, 0.50, 0.03)), "r", 0.0, 4.0,
                   valinit=R_INIZIALE, valstep=0.01)
cursore_x0 = Slider(figura.add_axes((0.12, 0.12, 0.50, 0.03)), "x0", 0.01, 0.99,
                    valinit=X0_INIZIALE, valstep=0.01)

pulsante_pausa = Button(figura.add_axes((0.70, 0.17, 0.08, 0.06)), "Pausa")
pulsante_reset = Button(figura.add_axes((0.80, 0.17, 0.08, 0.06)), "Ricomincia")
pulsante_cancella = Button(figura.add_axes((0.90, 0.17, 0.08, 0.06)), "Cancella")

messaggio = figura.text(0.08, 0.04, "", fontsize=12, color="darkgreen")


# ---------------------------------------------------------------
# 6) COSA SUCCEDE QUANDO TOCCHI UN COMANDO
# ---------------------------------------------------------------
def nuova_linea():
    """Fa partire una nuova linea da x0, con un nuovo colore."""
    x0, r = cursore_x0.val, cursore_r.val
    colore = COLORI[len(stato["vecchie"]) % len(COLORI)]
    stato["valori"] = [x0]
    stato["linea"], = assi.plot([], [], marker="o", color=colore,
                                label=f"x0 = {x0:.2f}")
    assi.legend(loc="upper right")

    messaggio.set_text(descrivi_comportamento(x0, r))


def metti_da_parte_la_linea():
    """La linea attuale diventa una "vecchia" linea sbiadita."""
    stato["linea"].set_alpha(0.35)
    stato["vecchie"].append(stato["linea"])


def cancella_le_vecchie(evento=None):
    for linea in stato["vecchie"]:
        linea.remove()
    stato["vecchie"].clear()


def cambia_x0(valore):
    # Stesso r, popolazione iniziale diversa: teniamo la vecchia linea per confrontarla.
    metti_da_parte_la_linea()
    nuova_linea()


def cambia_r(valore):
    # Con un r diverso le vecchie linee non servono piu'.
    stato["linea"].remove()
    cancella_le_vecchie()
    nuova_linea()


def ricomincia(evento=None):
    stato["linea"].remove()
    nuova_linea()


def metti_in_pausa(evento=None):
    stato["in_pausa"] = not stato["in_pausa"]
    pulsante_pausa.label.set_text("Riprendi" if stato["in_pausa"] else "Pausa")


cursore_r.on_changed(cambia_r)
cursore_x0.on_changed(cambia_x0)
pulsante_pausa.on_clicked(metti_in_pausa)
pulsante_reset.on_clicked(ricomincia)
pulsante_cancella.on_clicked(cancella_le_vecchie)


# ---------------------------------------------------------------
# 7) FUNZIONE CHIAMATA AD OGNI FOTOGRAMMA: un anno che passa
# ---------------------------------------------------------------
def aggiorna(fotogramma):
    valori = stato["valori"]
    if not stato["in_pausa"] and len(valori) <= N_PASSI:
        valori.append(logistica(valori[-1], cursore_r.val))

    stato["linea"].set_data(range(len(valori)), valori)
    return (stato["linea"],)


nuova_linea()
animazione = FuncAnimation(figura, aggiorna, interval=MILLISECONDI_PER_ANNO,
                           blit=False, cache_frame_data=False)

plt.show()
