"""
MODELLO PREDA-PREDATORE (LOTKA-VOLTERRA)
========================================
Librerie usate: Matplotlib e NumPy
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# ===============================================================
# 1. PARAMETRI DEL MODELLO (Fissati nel programma)
# ===============================================================
# I quattro valori chiave del modello Lotka-Volterra:
a = 0.5   # Fertilità conigli: quanti nuovi conigli nascono
b = 0.02  # Predazione: quanto sono brave le lepri a cacciare
c = 0.01  # Crescita lepri: quante nuove lepri nascono quando mangiano
d = 0.3   # Mortalità lepri: quante lepri muoiono di fame

# Popolazioni iniziali:
conigli = 40.0   # Numero iniziale di conigli (Prede)
lepri = 10.0     # Numero iniziale di lepri (Predatori)

# Passo temporale per il calcolo (piccolo intervallo di tempo "dt"):
dt = 0.05 


# ===============================================================
# 2. STRUTTURE PER SALVARE LA STORIA DEI DATI
# ===============================================================
# Usiamo delle liste per memorizzare l'andamento nel tempo:
tempo_storia = [0]
conigli_storia = [conigli]
lepri_storia = [lepri]


# ===============================================================
# 3. PREPARAZIONE DEL GRAFICO (Matplotlib)
# ===============================================================
fig, ax = plt.subplots(figsize=(10, 5))

# Creiamo le due linee del grafico (inizialmente vuote):
linea_conigli, = ax.plot([], [], label="Conigli (Prede)", color="blue", lw=2)
linea_lepri, = ax.plot([], [], label="Lepri (Predatori)", color="red", lw=2)

# Configurazione delle etichette e della griglia del grafico:
ax.set_title("Simulazione Modello Preda-Predatore (Lotka-Volterra)", fontsize=14)
ax.set_xlabel("Tempo", fontsize=12)
ax.set_ylabel("Popolazione", fontsize=12)
ax.set_ylim(0, 100)  # Limite verticale per la popolazione
ax.grid(True, linestyle="--", alpha=0.6)
ax.legend(loc="upper right")

# Testo per mostrare i valori numerici in tempo reale sul grafico:
testo_stato = ax.text(0.02, 0.90, "", transform=ax.transAxes, fontsize=11,
                      bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))


# ===============================================================
# 4. FUNZIONE DI AGGIORNAMENTO (Calcolo ad ogni fotogramma)
# ===============================================================
def aggiorna(frame):
    global conigli, lepri
    
    # -----------------------------------------------------------
    # LE EQUAZIONI MATEMATICHE (Metodo di Eulero)
    # -----------------------------------------------------------
    # dR/dt = a*R - b*R*F  --> Variazione dei conigli
    # dF/dt = c*R*F - d*F  --> Variazione delle lepri
    
    # 1. Calcoliamo di quanto cambiano le popolazioni in questo piccolo istante (dt)
    variazione_conigli = (a * conigli - b * conigli * lepri) * dt
    variazione_lepri = (c * conigli * lepri - d * lepri) * dt
    
    # 2. Aggiorniamo le popolazioni attuali
    conigli += variazione_conigli
    lepri += variazione_lepri
    
    # Impediamo che le popolazioni diventino negative
    conigli = max(0, conigli)
    lepri = max(0, lepri)
    
    # 3. Salviamo il nuovo punto nella storia
    tempo_corrente = tempo_storia[-1] + dt
    tempo_storia.append(tempo_corrente)
    conigli_storia.append(conigli)
    lepri_storia.append(lepri)
    
    # -----------------------------------------------------------
    # AGGIORNAMENTO DELLA GRAFICA
    # -----------------------------------------------------------
    # Aggiorniamo i dati delle linee:
    linea_conigli.set_data(tempo_storia, conigli_storia)
    linea_lepri.set_data(tempo_storia, lepri_storia)
    
    # Facciamo scorrere la vista sull'asse X per seguire il tempo che avanza
    if tempo_corrente > 20:
        ax.set_xlim(tempo_corrente - 20, tempo_corrente)
    else:
        ax.set_xlim(0, 20)
        
    # Adattiamo l'asse Y se la popolazione supera i limiti iniziali
    max_pop = max(max(conigli_storia), max(lepri_storia), 10)
    ax.set_ylim(0, max_pop * 1.2)
    
    # Aggiorniamo il riquadro con i dati in tempo reale
    testo_stato.set_text(f"Tempo: {tempo_corrente:.1f}\nConigli: {int(conigli)}\nLepri: {int(lepri)}")
    
    return linea_conigli, linea_lepri, testo_stato


# ===============================================================
# 5. AVVIO DELL'ANIMAZIONE
# ===============================================================
# FuncAnimation chiama la funzione 'aggiorna' ogni 30 millisecondi (interval=30)
animazione = FuncAnimation(fig, aggiorna, interval=30, cache_frame_data=False)

plt.tight_layout()
plt.show()