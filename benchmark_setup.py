"""
Ez a fájl a benchmark portfólió kezdeti szerkezetének szimulálásához
szükséges paramétereket és segédfüggvényeket tartalmazza.
A modul véletlenszerű szektor- és opciónkénti súlyokat, opciótípusokat,
irányokat, részvényárakat, kötési árfolyamokat, volatilitásokat és
futamidőket generál.

benchmark_kezdeti:
    Létrehozza a szimuláció kiinduló benchmark portfólióját tartalmazó
    DataFrame-et. A táblázat szektor- és opciósorokat is tartalmaz a
    későbbi árazási és attribúciós lépésekhez.
"""

import numpy as np
import pandas as pd

# ============================================================
# paraméterek
# ============================================================
veletlen_mag = 80

# portfólió szerkezet
szektorok_szama = 11
opciok_szama_szektoronkent = 10

# dirichlet paraméterek
alpha_szektorok = [1.0] * szektorok_szama

# szektoron belüli súlyok szórása
szoras_suly = 0.35

# call valószínűség
call_valoszinuseg = 0.5

# részvényár intervallum
s_min = 80
s_max = 120

# moneyness intervallum
m_min = 0.9
m_max = 1.1

# futamidő (nap)
tau_min_nap = 30
tau_max_nap = 365

# volatilitás intervallum
sigma_min = 0.15
sigma_max = 0.30

# kockázatmentes kamat
rf_0 = 0.03


def gen_veletlen_mag(mag: int) -> None:
    np.random.seed(mag)

def benchmark_szektorsuly(n_szektor: int, alpha: list[float]) -> np.ndarray:
    return np.random.dirichlet(alpha)

def benchmark_szektoron_beluli_suly(m: int, szoras: float) -> np.ndarray:
    x = np.random.normal(0, szoras, size=m)

    korrekcio = (1 - np.sum(x)) / m
    w = x + korrekcio

    return w

def irany(sulyok: np.ndarray) -> np.ndarray:
    return np.where(sulyok > 0, "long", "short")

def tipus(n: int, call_valoszinuseg: float) -> np.ndarray:
    u = np.random.uniform(0, 1, size=n)
    return np.where(u < call_valoszinuseg, "call", "put")

def tipus_es_irany(irany: np.ndarray, call_put: np.ndarray) -> np.ndarray:
    return np.array([f"{i}_{cp}" for i, cp in zip(irany, call_put)])

def reszvenyarak(n: int, s_min: int, s_max: int) -> np.ndarray:
    return np.random.randint(s_min, s_max + 1, size=n)

def kotesi_arfolyam(s0: np.ndarray, m_min: float, m_max: float) -> np.ndarray:
    
    n = len(s0)
    moneyness = np.random.uniform(m_min, m_max, size=n)
    k = np.round(s0 * moneyness).astype(int)
    
    return k

def volatilitas(n: int, sigma_min: float, sigma_max: float) -> np.ndarray:
    return np.random.uniform(sigma_min, sigma_max, size=n)

def hatralevo_ido(n: int, tau_min_nap: int, tau_max_nap: int) -> np.ndarray:
    
    tau_nap = np.random.randint(tau_min_nap, tau_max_nap + 1, size=n)
    tau_ev = tau_nap / 365
    
    return tau_ev

def benchmark_kezdeti() -> pd.DataFrame:

    gen_veletlen_mag(veletlen_mag)

    sorok = []

    szektor_sulyok = benchmark_szektorsuly(szektorok_szama, alpha_szektorok)

    for i in range(szektorok_szama):

        aktualis_szektor = i + 1
        aktualis_szektor_suly = szektor_sulyok[i]

        sorok.append({
            "nev": f"Szektor {aktualis_szektor}",
            "suly": aktualis_szektor_suly,
            "abszolut_suly": None,
            "tipus_es_irany": None,
            "irany": None,
            "tipus": None,
            "reszvenyarfolyam": None,
            "volatilitas": None,
            "hatralevo_ido": None,
            "kotesi_arfolyam": None,
            "kockazatmentes_kamat": None
        })

        szektoron_beluli_sulyok = benchmark_szektoron_beluli_suly(
            opciok_szama_szektoronkent,
            szoras_suly
        )

        opcio_irany = irany(szektoron_beluli_sulyok)
        opcio_tipus = tipus(opciok_szama_szektoronkent, call_valoszinuseg)
        opcio_tipus_es_irany = tipus_es_irany(opcio_irany, opcio_tipus)

        opcio_reszvenyarak = reszvenyarak(
            opciok_szama_szektoronkent,
            s_min,
            s_max
        )

        opcio_kotesi_arfolyamok = kotesi_arfolyam(
            opcio_reszvenyarak,
            m_min,
            m_max
        )

        opcio_volatilitasok = volatilitas(
            opciok_szama_szektoronkent,
            sigma_min,
            sigma_max
        )

        opcio_hatralevo_ido = hatralevo_ido(
            opciok_szama_szektoronkent,
            tau_min_nap,
            tau_max_nap
        )

        for j in range(opciok_szama_szektoronkent):

            aktualis_opcio = j + 1

            sorok.append({
                "nev": f"Opció {aktualis_szektor},{aktualis_opcio}",
                "suly": szektoron_beluli_sulyok[j],
                "abszolut_suly": aktualis_szektor_suly * szektoron_beluli_sulyok[j],
                "tipus_es_irany": opcio_tipus_es_irany[j],
                "irany": opcio_irany[j],
                "tipus": opcio_tipus[j],
                "reszvenyarfolyam": opcio_reszvenyarak[j],
                "volatilitas": opcio_volatilitasok[j],
                "hatralevo_ido": opcio_hatralevo_ido[j],
                "kotesi_arfolyam": opcio_kotesi_arfolyamok[j],
                "kockazatmentes_kamat": rf_0
            })

    df = pd.DataFrame(sorok)

    return df
