"""
CONIGLI E LEPRE: UNA SIMULAZIONE "PREDA-PREDATORE"
====================================================

L'IDEA (spiegata semplice):
In questa finestra ci sono due tipi di personaggi che si muovono a caso:

    - i CONIGLI (pallini blu)  -> le "prede"
    - le volpi   (pallini rossi) -> i "predatori"

Nota simpatica: nella realtà le volpi non mangiano i conigli! Qui le
usiamo solo come "personaggio B" della nostra storia, un po' come in
una favola. Quello che conta è la REGOLA che li fa interagire:

    - se due CONIGLI si incontrano, possono fare un cucciolo
      (i conigli aumentano);
    - se una LEPRE incontra un CONIGLIO, puo' mangiarlo
      (i conigli diminuiscono, ma la lepre si sfama);
    - se una lepre ha appena mangiato, puo' fare un cucciolo di lepre
      (le volpi aumentano);
    - ogni tanto una lepre muore di fame (le volpi diminuiscono).

Non abbiamo scritto nessuna formula! Eppure, guardando il grafico in
basso, vedrete che i conigli e le volpi crescono e calano a ondate,
uno di seguito all'altro: tanti conigli -> le volpi trovano cibo e
aumentano -> troppe volpi mangiano troppi conigli -> i conigli calano
-> le volpi restano senza cibo e calano -> pochi predatori -> i conigli
possono aumentare di nuovo -> e così via.

Questo comportamento "a onde" è esattamente quello che succede nel
modello matematico di Lotka-Volterra, che nel prossimo file
scriveremo usando le vere equazioni:

    dR/dt = a*R - b*R*F        (R = conigli, F = volpi)
    dF/dt = c*R*F - d*F

I quattro cursori a destra (a, b, c, d) sono proprio i quattro
parametri di quelle equazioni:

    a -> quanto facilmente i conigli si riproducono
    b -> quanto sono efficaci le volpi a cacciare
    c -> quanto le volpi si riproducono quando mangiano
    d -> quanto velocemente le volpi muoiono di fame

Provate a spostare i cursori e osservate come cambia il ritmo delle
"onde" nel grafico!

COMANDI:
    SPAZIO -> metti in pausa / riprendi
    R      -> ricomincia da capo
    ESC    -> esci dal programma

NOTA TECNICA per l'insegnante/lo studente più curioso:
questo file richiede la libreria "pygame". Nel nostro ambiente va
eseguito con Python 3.12, ad esempio:

    py -3.12 step2\\01_lotka_volterra.py

(pygame non ha ancora un pacchetto pronto per le versioni più nuove
di Python, come la 3.14).
"""

import math
import random
from collections import deque

import pygame

# ---------------------------------------------------------------
# 1) FINESTRA, COLORI E LAYOUT
# ---------------------------------------------------------------
LARGHEZZA_FINESTRA = 1000
ALTEZZA_FINESTRA = 650

# Dividiamo la finestra in tre zone:
#   - AREA_SIMULAZIONE: dove si muovono conigli e volpi (in alto a sinistra)
#   - AREA_GRAFICO:     l'andamento delle popolazioni nel tempo (in basso)
#   - AREA_PANNELLO:    i cursori dei 4 parametri (a destra)
AREA_SIMULAZIONE = pygame.Rect(0, 0, 750, 450)
AREA_GRAFICO = pygame.Rect(0, 450, 750, 200)
AREA_PANNELLO = pygame.Rect(750, 0, 250, ALTEZZA_FINESTRA)

BIANCO = (255, 255, 255)
NERO = (20, 20, 20)
GRIGIO_CHIARO = (235, 235, 230)
GRIGIO_SCURO = (150, 150, 150)
BLU_CONIGLIO = (50, 110, 210)
ROSSO_LEPRE = (210, 60, 60)
VERDE_PANNELLO = (245, 245, 250)

# ---------------------------------------------------------------
# 2) PARAMETRI INIZIALI DEL MODELLO E DELLA SIMULAZIONE
# ---------------------------------------------------------------
N_CONIGLI_INIZIALE = 60
N_volpi_INIZIALE = 10

CONIGLI_MASSIMI = 300   # limite per non rallentare troppo il programma
volpi_MASSIME = 200

CONIGLI_MINIMI = 2      # non facciamo mai estinguere del tutto le popolazioni
volpi_MINIME = 2

RAGGIO_INCONTRO = 20    # distanza (in pixel) entro cui due personaggi "si incontrano"

VELOCITA_CONIGLIO = 1.6
VELOCITA_LEPRE = 1.9


# ---------------------------------------------------------------
# 3) I DUE PERSONAGGI: CONIGLIO E LEPRE
# ---------------------------------------------------------------
class Coniglio:
    RAGGIO_DISEGNO = 5
    VELOCITA = VELOCITA_CONIGLIO
    COLORE = BLU_CONIGLIO

    def __init__(self, x, y):
        self.x = x
        self.y = y
        angolo = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angolo) * self.VELOCITA
        self.vy = math.sin(angolo) * self.VELOCITA

    def muovi(self):
        # Ogni tanto cambiamo un po' la direzione, come se il
        # personaggio "decidesse" spontaneamente di girare.
        if random.random() < 0.04:
            self.vx += random.uniform(-0.4, 0.4)
            self.vy += random.uniform(-0.4, 0.4)
            lunghezza = math.hypot(self.vx, self.vy)
            if lunghezza > 0:
                self.vx = self.vx / lunghezza * self.VELOCITA
                self.vy = self.vy / lunghezza * self.VELOCITA

        self.x += self.vx
        self.y += self.vy

        # Rimbalziamo sui bordi dell'area di simulazione.
        if self.x < AREA_SIMULAZIONE.left + self.RAGGIO_DISEGNO:
            self.x = AREA_SIMULAZIONE.left + self.RAGGIO_DISEGNO
            self.vx = abs(self.vx)
        elif self.x > AREA_SIMULAZIONE.right - self.RAGGIO_DISEGNO:
            self.x = AREA_SIMULAZIONE.right - self.RAGGIO_DISEGNO
            self.vx = -abs(self.vx)

        if self.y < AREA_SIMULAZIONE.top + self.RAGGIO_DISEGNO:
            self.y = AREA_SIMULAZIONE.top + self.RAGGIO_DISEGNO
            self.vy = abs(self.vy)
        elif self.y > AREA_SIMULAZIONE.bottom - self.RAGGIO_DISEGNO:
            self.y = AREA_SIMULAZIONE.bottom - self.RAGGIO_DISEGNO
            self.vy = -abs(self.vy)

    def disegna(self, schermo):
        pygame.draw.circle(schermo, self.COLORE, (int(self.x), int(self.y)), self.RAGGIO_DISEGNO)


class Lepre(Coniglio):
    # La lepre si muove esattamente come il coniglio: riusiamo lo
    # stesso comportamento e cambiamo solo aspetto e velocità.
    RAGGIO_DISEGNO = 7
    VELOCITA = VELOCITA_LEPRE
    COLORE = ROSSO_LEPRE


def distanza(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


# ---------------------------------------------------------------
# 4) UN CURSORE (SLIDER) PER CAMBIARE UN PARAMETRO CON IL MOUSE
# ---------------------------------------------------------------
class Slider:
    def __init__(self, x, y, larghezza, valore_min, valore_max, valore_iniziale, etichetta):
        self.barra = pygame.Rect(x, y, larghezza, 6)
        self.valore_min = valore_min
        self.valore_max = valore_max
        self.valore = valore_iniziale
        self.etichetta = etichetta
        self.sto_trascinando = False

    def _x_manopola(self):
        frazione = (self.valore - self.valore_min) / (self.valore_max - self.valore_min)
        return self.barra.x + frazione * self.barra.width

    def gestisci_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mx, my = evento.pos
            if (mx - self._x_manopola()) ** 2 + (my - self.barra.centery) ** 2 <= 13 ** 2:
                self.sto_trascinando = True
        elif evento.type == pygame.MOUSEBUTTONUP:
            self.sto_trascinando = False
        elif evento.type == pygame.MOUSEMOTION and self.sto_trascinando:
            frazione = (evento.pos[0] - self.barra.x) / self.barra.width
            frazione = max(0.0, min(1.0, frazione))
            self.valore = self.valore_min + frazione * (self.valore_max - self.valore_min)

    def disegna(self, schermo, font):
        testo = font.render(f"{self.etichetta} = {self.valore:.3f}", True, NERO)
        schermo.blit(testo, (self.barra.x, self.barra.y - 22))
        pygame.draw.rect(schermo, GRIGIO_SCURO, self.barra, border_radius=3)
        x_manopola = int(self._x_manopola())
        pygame.draw.circle(schermo, NERO, (x_manopola, self.barra.centery), 9)
        pygame.draw.circle(schermo, BIANCO, (x_manopola, self.barra.centery), 6)


# ---------------------------------------------------------------
# 5) LA "REGOLA" CHE FA EVOLVERE IL SISTEMA DI UN FOTOGRAMMA
# ---------------------------------------------------------------
def aggiorna_simulazione(conigli, volpi, a, b, c, d):
    for coniglio in conigli:
        coniglio.muovi()
    for lepre in volpi:
        lepre.muovi()

    # --- le volpi muoiono di fame con probabilità d (mai sotto il minimo) ---
    sopravvissute = [lepre for lepre in volpi if random.random() >= d]
    if len(sopravvissute) < volpi_MINIME and len(volpi) >= volpi_MINIME:
        morte = [lepre for lepre in volpi if lepre not in sopravvissute]
        sopravvissute.extend(morte[:volpi_MINIME - len(sopravvissute)])
    volpi[:] = sopravvissute

    # --- una lepre che incontra un coniglio puo' mangiarlo (prob. b) ---
    # se ha appena mangiato, puo' anche riprodursi (prob. c)
    conigli_mangiati = set()
    nuove_volpi = []
    for lepre in volpi:
        for indice, coniglio in enumerate(conigli):
            if indice in conigli_mangiati:
                continue
            if distanza(lepre, coniglio) < RAGGIO_INCONTRO:
                if random.random() < b:
                    conigli_mangiati.add(indice)
                    if random.random() < c:
                        nuove_volpi.append(Lepre(lepre.x, lepre.y))
                break  # una lepre mangia al massimo un coniglio per fotogramma

    if conigli_mangiati:
        # non facciamo scendere i conigli sotto il minimo
        massimo_da_mangiare = max(0, len(conigli) - CONIGLI_MINIMI)
        if len(conigli_mangiati) > massimo_da_mangiare:
            conigli_mangiati = set(list(conigli_mangiati)[:massimo_da_mangiare])
        conigli[:] = [c_ for i, c_ in enumerate(conigli) if i not in conigli_mangiati]

    # --- due conigli che si incontrano possono fare un cucciolo (prob. a) ---
    nuovi_conigli = []
    gia_accoppiati = set()
    numero_conigli = len(conigli)
    for i in range(numero_conigli):
        if i in gia_accoppiati:
            continue
        for j in range(i + 1, numero_conigli):
            if j in gia_accoppiati:
                continue
            if distanza(conigli[i], conigli[j]) < RAGGIO_INCONTRO:
                if random.random() < a:
                    nuovi_conigli.append(Coniglio(
                        (conigli[i].x + conigli[j].x) / 2,
                        (conigli[i].y + conigli[j].y) / 2,
                    ))
                    gia_accoppiati.add(i)
                    gia_accoppiati.add(j)
                break

    # aggiungiamo i nuovi nati, rispettando i limiti massimi
    if len(conigli) + len(nuovi_conigli) <= CONIGLI_MASSIMI:
        conigli.extend(nuovi_conigli)
    if len(volpi) + len(nuove_volpi) <= volpi_MASSIME:
        volpi.extend(nuove_volpi)


# ---------------------------------------------------------------
# 6) DISEGNO DEL GRAFICO "POPOLAZIONE NEL TEMPO"
# ---------------------------------------------------------------
def disegna_grafico(schermo, storia_conigli, storia_volpi, font):
    pygame.draw.rect(schermo, BIANCO, AREA_GRAFICO)
    pygame.draw.rect(schermo, GRIGIO_SCURO, AREA_GRAFICO, 2)

    titolo = font.render("Numero di conigli (blu) e volpi (rosso) nel tempo", True, NERO)
    schermo.blit(titolo, (AREA_GRAFICO.x + 10, AREA_GRAFICO.y + 6))

    area = pygame.Rect(AREA_GRAFICO.x + 10, AREA_GRAFICO.y + 30,
                        AREA_GRAFICO.width - 20, AREA_GRAFICO.height - 65)
    pygame.draw.rect(schermo, GRIGIO_CHIARO, area)

    massimo = max(list(storia_conigli) + list(storia_volpi) + [10])  # evita di dividere per zero

    def disegna_linea(storia, colore):
        if len(storia) < 2:
            return
        punti = []
        n = len(storia)
        for i, valore in enumerate(storia):
            x = area.x + i / (n - 1) * area.width
            y = area.bottom - (valore / massimo) * area.height
            punti.append((x, y))
        pygame.draw.lines(schermo, colore, False, punti, 2)

    disegna_linea(storia_conigli, BLU_CONIGLIO)
    disegna_linea(storia_volpi, ROSSO_LEPRE)

    etichetta_x = font.render("Tempo →", True, NERO)
    schermo.blit(etichetta_x, (area.right - etichetta_x.get_width(), area.bottom + 8))

    etichetta_y = font.render("Popolazione", True, NERO)
    etichetta_y = pygame.transform.rotate(etichetta_y, 90)
    schermo.blit(etichetta_y, (AREA_GRAFICO.x + 8, area.y))

    n_conigli = storia_conigli[-1] if storia_conigli else 0
    n_volpi = storia_volpi[-1] if storia_volpi else 0
    testo_valori = font.render(f"Conigli: {n_conigli}       volpi: {n_volpi}", True, NERO)
    schermo.blit(testo_valori, (AREA_GRAFICO.x + 10, AREA_GRAFICO.bottom - 25))


# ---------------------------------------------------------------
# 7) PROGRAMMA PRINCIPALE
# ---------------------------------------------------------------
def crea_popolazione_iniziale():
    conigli = [
        Coniglio(random.uniform(AREA_SIMULAZIONE.left + 20, AREA_SIMULAZIONE.right - 20),
                  random.uniform(AREA_SIMULAZIONE.top + 20, AREA_SIMULAZIONE.bottom - 20))
        for _ in range(N_CONIGLI_INIZIALE)
    ]
    volpi = [
        Lepre(random.uniform(AREA_SIMULAZIONE.left + 20, AREA_SIMULAZIONE.right - 20),
               random.uniform(AREA_SIMULAZIONE.top + 20, AREA_SIMULAZIONE.bottom - 20))
        for _ in range(N_volpi_INIZIALE)
    ]
    return conigli, volpi


def main():
    pygame.init()
    schermo = pygame.display.set_mode((LARGHEZZA_FINESTRA, ALTEZZA_FINESTRA))
    pygame.display.set_caption("Conigli e volpi - un modello preda-predatore")
    orologio = pygame.time.Clock()

    font = pygame.font.SysFont(None, 20)
    font_titolo = pygame.font.SysFont(None, 24, bold=True)

    # I quattro parametri del modello di Lotka-Volterra, come cursori
    x_pannello = AREA_PANNELLO.x + 20
    larghezza_slider = AREA_PANNELLO.width - 40
    slider_a = Slider(x_pannello, 100, larghezza_slider, 0.0, 0.10, 0.03, "a (crescita conigli)")
    slider_b = Slider(x_pannello, 190, larghezza_slider, 0.0, 1.00, 0.21, "b (predazione)")
    slider_c = Slider(x_pannello, 280, larghezza_slider, 0.0, 1.00, 0.27, "c (crescita volpi)")
    slider_d = Slider(x_pannello, 370, larghezza_slider, 0.0, 0.02, 0.009, "d (mortalità volpi)")
    sliders = [slider_a, slider_b, slider_c, slider_d]

    conigli, volpi = crea_popolazione_iniziale()
    storia_conigli = deque(maxlen=400)
    storia_volpi = deque(maxlen=400)
    contatore_fotogrammi = 0
    in_pausa = False

    in_esecuzione = True
    while in_esecuzione:
        orologio.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                in_esecuzione = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    in_esecuzione = False
                elif evento.key == pygame.K_SPACE:
                    in_pausa = not in_pausa
                elif evento.key == pygame.K_r:
                    conigli, volpi = crea_popolazione_iniziale()
                    storia_conigli.clear()
                    storia_volpi.clear()
                    contatore_fotogrammi = 0
                    in_pausa = False
            for slider in sliders:
                slider.gestisci_evento(evento)

        if not in_pausa:
            aggiorna_simulazione(conigli, volpi, slider_a.valore, slider_b.valore,
                                 slider_c.valore, slider_d.valore)
            contatore_fotogrammi += 1
            if contatore_fotogrammi % 3 == 0:  # campioniamo la storia ogni 3 fotogrammi
                storia_conigli.append(len(conigli))
                storia_volpi.append(len(volpi))

        # --- disegno di tutta la finestra ---
        schermo.fill(GRIGIO_CHIARO)

        pygame.draw.rect(schermo, BIANCO, AREA_SIMULAZIONE)
        for coniglio in conigli:
            coniglio.disegna(schermo)
        for lepre in volpi:
            lepre.disegna(schermo)
        pygame.draw.rect(schermo, GRIGIO_SCURO, AREA_SIMULAZIONE, 2)

        if in_pausa:
            testo_pausa = font_titolo.render("IN PAUSA (premi SPAZIO per riprendere)", True, NERO)
            schermo.blit(testo_pausa, (AREA_SIMULAZIONE.x + 15, AREA_SIMULAZIONE.y + 10))

        disegna_grafico(schermo, storia_conigli, storia_volpi, font)

        pygame.draw.rect(schermo, VERDE_PANNELLO, AREA_PANNELLO)
        pygame.draw.line(schermo, GRIGIO_SCURO, (AREA_PANNELLO.x, 0),
                          (AREA_PANNELLO.x, ALTEZZA_FINESTRA), 2)
        titolo_pannello = font_titolo.render("Parametri del modello", True, NERO)
        schermo.blit(titolo_pannello, (x_pannello, 55))
        for slider in sliders:
            slider.disegna(schermo, font)

        comandi = [
            "SPAZIO = pausa/riprendi",
            "R = ricomincia",
            "ESC = esci",
        ]
        for i, riga in enumerate(comandi):
            testo = font.render(riga, True, NERO)
            schermo.blit(testo, (x_pannello, 470 + i * 22))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
