import math

import numpy as np
import matplotlib.pyplot as plt

NUMERO_MASSIMO = 1000 

def e_multiplo_di_7(n):
    """Vero se n è un multiplo di 7 (7, 14, 21, ...)."""
    return n % 11 == 0

numeri =range(1, NUMERO_MASSIMO + 1)
numeri_np = np.array(numeri)

x = numeri_np * np.cos(numeri_np)
y = numeri_np * np.sin(numeri_np)
maschera_multipli_di_7 = np.array([e_multiplo_di_7(n) for n in numeri])
print(numeri_np)
print(maschera_multipli_di_7)
x_multipli_di_7 = x[maschera_multipli_di_7]
y_multipli_di_7 = y[maschera_multipli_di_7]



figura, assi = plt.subplots(figsize=(8, 8))
assi.scatter(x, y, color="yellow", s=6, label="tutti gli interi")
assi.scatter(x_multipli_di_7, y_multipli_di_7, color="red", s=14, label="multipli di 7")
assi.set_title(f"Tutti i numeri (multipli di 11 in rosso)")
assi.set_aspect("equal")
assi.set_xticks([])
assi.set_yticks([])
plt.show()  