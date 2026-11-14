
"""
CONIGLI E PRATO: UNA POPOLAZIONE CHE FA I CONTI CON L'AMBIENTE
================================================================

L'IDEA (spiegata semplice):
Nello step 2 avevamo due popolazioni (conigli e volpi) che si
influenzavano a vicenda. Qui togliamo le volpi: restano solo i
CONIGLI (pallini blu) e un PRATO (tutto verde) che e' la loro risorsa.

Il prato e' diviso in tante "caselle". In ogni casella puo' stare
al massimo UN coniglio. A ogni "tic" del tempo TUTTI i conigli, nello
stesso momento:

    1) guardano le 8 caselle attorno a loro e contano quante sono LIBERE
       (cioe' erba senza altri conigli sopra);
    2) se ne hanno abbastanza libere (almeno "V_MIN") trovano da mangiare
       e recuperano energia; se invece sono troppo affollati restano
       a digiuno e perdono energia (basta un tic storto per essere in
       crisi, due per morire);
    3) chi e' in forze puo' fare un cucciolo (con probabilita' "r"),
       se trova una casella libera accanto;
    4) infine tutti fanno un passetto a caso in una casella libera.

Non abbiamo scritto nessuna formula! Eppure, guardando il grafico in
basso, vedrete una curva a "S":

    - all'inizio i conigli sono pochi, hanno tanto spazio e crescono
      in fretta (sempre piu' conigli -> sempre piu' cuccioli);
    - poi il prato si riempie, il cibo/spazio scarseggia e la crescita
      rallenta;
    - alla fine la popolazione si stabilizza attorno a un valore
      massimo che l'ambiente riesce a sostenere: la CAPACITA' DELL'AMBIENTE
      (si indica con K, la linea tratteggiata).

E se r e' alto? Succede una cosa interessante: i conigli si riproducono
tutti insieme, il prato si riempie "oltre K", poi in tanti restano a
digiuno e muoiono tutti insieme... e la popolazione OSCILLA attorno a K.
Con r vicino a 1 puo' addirittura alternare un anno "tanti" e un anno "pochi".

Questo e' esattamente il comportamento descritto dalla MAPPA LOGISTICA,
che nel prossimo file scriveremo con la vera formula:

    x(n+1) = r * x(n) * (1 - x(n) / K)

    r -> quanto in fretta i conigli si riproducono quando sono pochi
    K -> quanti conigli riesce a sostenere il prato

I due cursori a destra:

    r     -> probabilita' di fare un cucciolo: con r basso la popolazione
             sale piano e si stabilizza; con r alto sale in fretta, sfora
             K e comincia a oscillare
    V_MIN -> quante caselle libere servono per mangiare: piu' e' alto,
             piu' il prato "si stufa" in fretta e K diventa piccolo

COMANDI:
    SPAZIO -> metti in pausa / riprendi
    R      -> ricomincia da capo
    S      -> salva la serie "tempo, numero_conigli" in un file CSV
    ESC    -> esci dal programma

NOTA TECNICA per l'insegnante/lo studente piu' curioso:
questo file richiede la libreria "pygame". Nel nostro ambiente va
eseguito con Python 3.12, ad esempio:

    py -3.12 step3\\01_conigli_e_prato.py
"""

import csv
import os
import random

import pygame

# ---------------------------------------------------------------
# 1) FINESTRA, COLORI E LAYOUT (come nello step 2)
# ---------------------------------------------------------------
LARGHEZZA_FINESTRA = 1000
ALTEZZA_FINESTRA = 850

AREA_SIMULAZIONE = pygame.Rect(0, 0, 750, 450)
AREA_GRAFICO = pygame.Rect(0, 450, 750, 400)
AREA_PANNELLO = pygame.Rect(750, 0, 250, ALTEZZA_FINESTRA)

BIANCO = (255, 255, 255)
NERO = (20, 20, 20)
GRIGIO_CHIARO = (235, 235, 230)
GRIGIO_SCURO = (150, 150, 150)
BLU_CONIGLIO = (50, 110, 210)
VERDE_ERBA = (130, 195, 95)
VERDE_ERBA_SCURO = (118, 184, 85)
VERDE_PANNELLO = (245, 245, 250)
ARANCIO_K = (230, 120, 20)

# ---------------------------------------------------------------
# 2) IL PRATO E I PARAMETRI DELLA SIMULAZIONE
# ---------------------------------------------------------------
LATO_CASELLA = 15
COLONNE = AREA_SIMULAZIONE.width // LATO_CASELLA   # 50
RIGHE = AREA_SIMULAZIONE.height // LATO_CASELLA    # 30

N_CONIGLI_INIZIALE = 20
CONIGLI_MINIMI = 2           # non lasciamo estinguere del tutto la popolazione

# Energia "corta": un coniglio ha una sola scorta di riserva, quindi
# basta un tic di affollamento per metterlo in crisi e due per farlo
# morire. Nascite e morti sono rapide e questo permette le oscillazioni.
ENERGIA_INIZIALE = 2         # energia di un coniglio appena nato
ENERGIA_MASSIMA = 2
COSTO_CUCCIOLO = 1           # energia che il genitore perde facendo un cucciolo
SOGLIA_RIPRODUZIONE = 2      # energia minima per poter fare un cucciolo

R_INIZIALE = 0.20
R_MINIMO = 0.05
R_MASSIMO = 1.00
V_MIN_INIZIALE = 3           # caselle libere (su 8) necessarie per mangiare

FOTOGRAMMI_PER_TIC = 3       # velocita' della simulazione
CAMPIONI_GRAFICO = 120       # quanti punti mostrare nel grafico (pochi = oscillazioni piu' leggibili)
CAMPIONI_PER_K = 100         # ultimi punti usati per stimare K


# ---------------------------------------------------------------
# 3) IL CONIGLIO E IL PRATO
# ---------------------------------------------------------------
class Coniglio:
    def __init__(self, colonna, riga, energia=ENERGIA_INIZIALE):
        self.colonna = colonna
        self.riga = riga
        self.energia = energia
        self.vivo = True


class Prato:
    def __init__(self, n_conigli=N_CONIGLI_INIZIALE):
        self.celle = [[None] * COLONNE for _ in range(RIGHE)]
        self.conigli = []
        for _ in range(n_conigli):
            self._aggiungi_in_casella_libera()

    def _aggiungi(self, colonna, riga, energia=ENERGIA_INIZIALE):
        coniglio = Coniglio(colonna, riga, energia)
        self.celle[riga][colonna] = coniglio
        self.conigli.append(coniglio)
        return coniglio

    def _aggiungi_in_casella_libera(self):
        while True:
            colonna = random.randrange(COLONNE)
            riga = random.randrange(RIGHE)
            if self.celle[riga][colonna] is None:
                self._aggiungi(colonna, riga)
                return

    def caselle_libere_vicine(self, colonna, riga):
        # Il prato "si chiude su se stesso" (come in Pac-Man): uscendo
        # da un lato si rientra dall'altro, cosi' nessun coniglio e'
        # svantaggiato perche' sta vicino al bordo.
        libere = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                c = (colonna + dc) % COLONNE
                r = (riga + dr) % RIGHE
                if self.celle[r][c] is None:
                    libere.append((c, r))
        return libere

    def percentuale_occupata(self):
        return 100 * len(self.conigli) / (COLONNE * RIGHE)

    def passo(self, r, v_min):
        """Fa avanzare il prato di un "tic" di tempo."""
        # Tutti i conigli "guardano" il prato nello stesso istante, prima
        # che nascano i cuccioli: e' come se la popolazione si muovesse a
        # "generazioni". Il ritardo fra "c'e' posto" e "ora e' pieno" e'
        # cio' che puo' far sforare K e poi crollare, cioe' oscillare.
        spazio = {c: len(self.caselle_libere_vicine(c.colonna, c.riga))
                  for c in self.conigli}

        # 1) mangia (se c'e' abbastanza spazio) oppure digiuna
        # 2) chi ha l'energia a zero muore, tutti insieme
        genitori = []
        for coniglio in self.conigli:
            if spazio[coniglio] >= v_min:
                coniglio.energia = min(coniglio.energia + 1, ENERGIA_MASSIMA)
                if coniglio.energia >= SOGLIA_RIPRODUZIONE and random.random() < r:
                    genitori.append(coniglio)
            else:
                coniglio.energia -= 1
            if coniglio.energia <= 0:
                coniglio.vivo = False
                self.celle[coniglio.riga][coniglio.colonna] = None

        # 3) i sopravvissuti che volevano un cucciolo lo fanno, se trovano posto
        random.shuffle(genitori)  # nessun genitore ha la precedenza
        for coniglio in genitori:
            if not coniglio.vivo:
                continue
            libere = self.caselle_libere_vicine(coniglio.colonna, coniglio.riga)
            if libere:
                c, rg = random.choice(libere)
                coniglio.energia -= COSTO_CUCCIOLO
                self._aggiungi(c, rg)

        # 4) tutti fanno un passetto in una casella libera
        for coniglio in self.conigli:
            if not coniglio.vivo:
                continue
            libere = self.caselle_libere_vicine(coniglio.colonna, coniglio.riga)
            if libere:
                c, rg = random.choice(libere)
                self.celle[coniglio.riga][coniglio.colonna] = None
                coniglio.colonna, coniglio.riga = c, rg
                self.celle[rg][c] = coniglio

        self.conigli = [c for c in self.conigli if c.vivo]
        while len(self.conigli) < CONIGLI_MINIMI:
            self._aggiungi_in_casella_libera()


# ---------------------------------------------------------------
# 4) UN CURSORE (SLIDER) PER CAMBIARE UN PARAMETRO CON IL MOUSE
# ---------------------------------------------------------------
class Slider:
    def __init__(self, x, y, larghezza, valore_min, valore_max, valore_iniziale,
                 etichetta, intero=False):
        self.barra = pygame.Rect(x, y, larghezza, 6)
        self.valore_min = valore_min
        self.valore_max = valore_max
        self.valore = valore_iniziale
        self.etichetta = etichetta
        self.intero = intero
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
            valore = self.valore_min + frazione * (self.valore_max - self.valore_min)
            self.valore = round(valore) if self.intero else valore

    def disegna(self, schermo, font):
        valore_testo = f"{self.valore}" if self.intero else f"{self.valore:.2f}"
        testo = font.render(f"{self.etichetta} = {valore_testo}", True, NERO)
        schermo.blit(testo, (self.barra.x, self.barra.y - 22))
        pygame.draw.rect(schermo, GRIGIO_SCURO, self.barra, border_radius=3)
        x_manopola = int(self._x_manopola())
        pygame.draw.circle(schermo, NERO, (x_manopola, self.barra.centery), 9)
        pygame.draw.circle(schermo, BIANCO, (x_manopola, self.barra.centery), 6)


# ---------------------------------------------------------------
# 5) DISEGNO DEL PRATO E DEL GRAFICO
# ---------------------------------------------------------------
def crea_sfondo_prato():
    # Disegniamo il prato una volta sola: caselle verdi di due toni alternati.
    sfondo = pygame.Surface(AREA_SIMULAZIONE.size)
    for riga in range(RIGHE):
        for colonna in range(COLONNE):
            colore = VERDE_ERBA if (riga + colonna) % 2 == 0 else VERDE_ERBA_SCURO
            pygame.draw.rect(sfondo, colore,
                             (colonna * LATO_CASELLA, riga * LATO_CASELLA,
                              LATO_CASELLA, LATO_CASELLA))
    return sfondo


def disegna_prato(schermo, sfondo, prato):
    schermo.blit(sfondo, AREA_SIMULAZIONE.topleft)
    raggio = LATO_CASELLA // 2 - 2
    for coniglio in prato.conigli:
        centro = (AREA_SIMULAZIONE.x + coniglio.colonna * LATO_CASELLA + LATO_CASELLA // 2,
                  AREA_SIMULAZIONE.y + coniglio.riga * LATO_CASELLA + LATO_CASELLA // 2)
        pygame.draw.circle(schermo, BLU_CONIGLIO, centro, raggio)
    pygame.draw.rect(schermo, GRIGIO_SCURO, AREA_SIMULAZIONE, 2)


def stima_k(serie):
    """K stimato = media degli ultimi punti, ma solo quando la serie e' abbastanza lunga."""
    if len(serie) < 2 * CAMPIONI_PER_K:
        return None
    ultimi = serie[-CAMPIONI_PER_K:]
    return sum(ultimi) / len(ultimi)


def disegna_grafico(schermo, storia, k_stimato, font):
    pygame.draw.rect(schermo, BIANCO, AREA_GRAFICO)
    pygame.draw.rect(schermo, GRIGIO_SCURO, AREA_GRAFICO, 2)

    titolo = font.render("Numero di conigli nel tempo (tratteggio arancio = K stimato)",
                         True, NERO)
    schermo.blit(titolo, (AREA_GRAFICO.x + 10, AREA_GRAFICO.y + 6))

    area = pygame.Rect(AREA_GRAFICO.x + 30, AREA_GRAFICO.y + 30,
                       AREA_GRAFICO.width - 40, AREA_GRAFICO.height - 65)
    pygame.draw.rect(schermo, GRIGIO_CHIARO, area)

    massimo = max(list(storia) + [100]) * 1.1

    def y_di(valore):
        return area.bottom - (valore / massimo) * area.height

    if len(storia) >= 2:
        passo_x = area.width / (CAMPIONI_GRAFICO - 1)
        punti = [(area.x + i * passo_x, y_di(v)) for i, v in enumerate(storia)]
        pygame.draw.lines(schermo, BLU_CONIGLIO, False, punti, 2)

    if k_stimato is not None:
        y = y_di(k_stimato)
        for x in range(area.x, area.right, 12):
            pygame.draw.line(schermo, ARANCIO_K, (x, y), (min(x + 6, area.right), y), 2)

    schermo.blit(font.render(f"max {massimo:.0f}", True, NERO), (area.x + 4, area.y + 2))
    schermo.blit(font.render("0", True, NERO), (area.x + 4, area.bottom - 16))

    etichetta_x = font.render("Tempo ->", True, NERO)
    schermo.blit(etichetta_x, (area.right - etichetta_x.get_width(), area.bottom + 8))
    etichetta_y = pygame.transform.rotate(font.render("Conigli", True, NERO), 90)
    schermo.blit(etichetta_y, (AREA_GRAFICO.x + 8, area.y))


# ---------------------------------------------------------------
# 6) SALVATAGGIO DELLA SERIE (per il file sulla mappa logistica)
# ---------------------------------------------------------------
def salva_csv(serie):
    percorso = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serie_conigli.csv")
    with open(percorso, "w", newline="", encoding="utf-8") as f:
        scrittore = csv.writer(f)
        scrittore.writerow(["tempo", "numero_conigli"])
        for tempo, numero in enumerate(serie):
            scrittore.writerow([tempo, numero])
    return percorso


# ---------------------------------------------------------------
# 7) PROGRAMMA PRINCIPALE
# ---------------------------------------------------------------
def main():
    pygame.init()
    schermo = pygame.display.set_mode((LARGHEZZA_FINESTRA, ALTEZZA_FINESTRA))
    pygame.display.set_caption("Conigli e prato - verso la mappa logistica")
    orologio = pygame.time.Clock()

    font = pygame.font.SysFont(None, 20)
    font_titolo = pygame.font.SysFont(None, 24, bold=True)

    x_pannello = AREA_PANNELLO.x + 20
    larghezza_slider = AREA_PANNELLO.width - 40
    slider_r = Slider(x_pannello, 100, larghezza_slider, R_MINIMO, R_MASSIMO, R_INIZIALE,
                      "r (voglia di riprodursi)")
    slider_vmin = Slider(x_pannello, 190, larghezza_slider, 1, 6, V_MIN_INIZIALE,
                         "V_MIN (spazio per mangiare)", intero=True)
    sliders = [slider_r, slider_vmin]

    sfondo = crea_sfondo_prato()
    prato = Prato()
    serie = [len(prato.conigli)]
    contatore_fotogrammi = 0
    in_pausa = False
    messaggio = ""
    fotogrammi_messaggio = 0

    in_esecuzione = True
    while in_esecuzione:
        orologio.tick(30)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                in_esecuzione = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    in_esecuzione = False
                elif evento.key == pygame.K_SPACE:
                    in_pausa = not in_pausa
                elif evento.key == pygame.K_r:
                    prato = Prato()
                    serie = [len(prato.conigli)]
                    contatore_fotogrammi = 0
                    in_pausa = False
                elif evento.key == pygame.K_s:
                    messaggio = "Salvato: " + os.path.basename(salva_csv(serie))
                    fotogrammi_messaggio = 90
            for slider in sliders:
                slider.gestisci_evento(evento)

        if not in_pausa:
            contatore_fotogrammi += 1
            if contatore_fotogrammi % FOTOGRAMMI_PER_TIC == 0:
                prato.passo(slider_r.valore, slider_vmin.valore)
                serie.append(len(prato.conigli))

        k_stimato = stima_k(serie)

        schermo.fill(GRIGIO_CHIARO)
        disegna_prato(schermo, sfondo, prato)
        if in_pausa:
            testo_pausa = font_titolo.render("IN PAUSA (premi SPAZIO per riprendere)",
                                             True, NERO)
            schermo.blit(testo_pausa, (AREA_SIMULAZIONE.x + 15, AREA_SIMULAZIONE.y + 10))

        disegna_grafico(schermo, serie[-CAMPIONI_GRAFICO:], k_stimato, font)

        pygame.draw.rect(schermo, VERDE_PANNELLO, AREA_PANNELLO)
        pygame.draw.line(schermo, GRIGIO_SCURO, (AREA_PANNELLO.x, 0),
                         (AREA_PANNELLO.x, ALTEZZA_FINESTRA), 2)
        schermo.blit(font_titolo.render("Parametri del modello", True, NERO), (x_pannello, 55))
        for slider in sliders:
            slider.disegna(schermo, font)

        contatori = [
            f"Tempo: {len(serie) - 1}",
            f"Conigli: {len(prato.conigli)}",
            f"Prato occupato: {prato.percentuale_occupata():.0f}%",
            "K stimato: " + (f"{k_stimato:.0f}" if k_stimato is not None else "..."),
        ]
        for i, riga in enumerate(contatori):
            schermo.blit(font.render(riga, True, NERO), (x_pannello, 270 + i * 24))

        comandi = ["SPAZIO = pausa/riprendi", "R = ricomincia", "S = salva CSV", "ESC = esci"]
        for i, riga in enumerate(comandi):
            schermo.blit(font.render(riga, True, NERO), (x_pannello, 420 + i * 22))

        if fotogrammi_messaggio > 0:
            fotogrammi_messaggio -= 1
            schermo.blit(font.render(messaggio, True, NERO), (x_pannello, 520))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
