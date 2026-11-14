"""
LA MAPPA LOGISTICA: LA POPOLAZIONE NEL TEMPO
=======================================================================

formula, che prende la popolazione di quest'anno e calcola quella
dell'anno dopo:

    x(nuovo) = r * x * (1 - x)

    x -> la popolazione, misurata da 0 (nessun coniglio) a 1 (il prato
         e' pieno, il massimo possibile)
    r -> il tasso di crescita: quanto in fretta i conigli si riproducono

Il pezzo "r * x" fa crescere la popolazione (piu' conigli = piu' cuccioli).
Il pezzo "(1 - x)" la frena (piu' il prato e' pieno, meno cibo c'e').

"""

import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# 1) PARAMETRI INIZIALI
# ---------------------------------------------------------------
R = 5     # tasso di crescita
X0_INIZIALE = 0.04    # popolazione iniziale (0 = vuoto, 1 = prato pieno)
N_PASSI = 40          # quanti anni simuliamo


# ---------------------------------------------------------------
# 2) CALCOLO DEI VALORI NEL TEMPO
# ---------------------------------------------------------------
valori = [X0_INIZIALE]
X = X0_INIZIALE
for i in range(N_PASSI):
       
        valori.append(X)

# ---------------------------------------------------------------
# 3) FINESTRA: il grafico
# ---------------------------------------------------------------
figura = plt.figure(figsize=(11, 6.5))
figura.suptitle("La mappa logistica: x(nuovo) = r * x * (1 - x) con R = " + str(R) + " e x0 = " + str(X0_INIZIALE), fontsize=13)

assi = figura.add_axes((0.08, 0.32, 0.88, 0.58)) # posizione e dimensione dell'area del grafico
assi.set_title("Popolazione nel tempo")
assi.set_xlabel("Tempo (anni)")
assi.set_ylabel("Popolazione")
assi.set_xlim(-0.5, N_PASSI + 0.5)
assi.set_ylim(0, 1)
assi.grid(True, alpha=0.3)
assi.plot(range(N_PASSI + 1), valori, marker="o")
plt.show()