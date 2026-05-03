"""
Ez a fájl a benchmark portfólióból kiinduló aktívan kezelt portfóliók
szimulálásához szükséges paramétereket és segédfüggvényeket tartalmazza.
A modul szektor- és opciónkénti aktív súlyeltéréseket generál, majd ezekből
több portfóliómenedzseri portfóliót állít elő.

aktivan_kezelt_portfoliok:
    A benchmark portfólió alapján megadott számú aktívan kezelt portfóliót
    generál. Az eredmény portfóliómenedzserenként egy-egy DataFrame, amely
    a szektor- és opciónkénti aktív súlyokat tartalmazza.

"""

import numpy as np
import pandas as pd

# generált aktív portfóliók száma
pm_db = 100

# Dirichlet koncentrációs paraméter a szektorsúlyokhoz
lambda_ertek = 100.0

# aktív döntések intenzitása szektoron belül
szigma_aktiv = 0.08


def szektor_azonosito_nevbol(nev: str) -> int:
    if nev.startswith("Szektor"):
        return int(nev.replace("Szektor ", ""))
    if nev.startswith("Opció"):
        return int(nev.replace("Opció ", "").split(",")[0])
    raise ValueError(f"Ismeretlen névformátum: {nev}")


def benchmark_szektorsulyak(df: pd.DataFrame) -> pd.DataFrame:
    szektor = df["nev"].str.startswith("Szektor")
    df_szektor = df.loc[szektor, ["nev", "suly"]].copy()
    df_szektor["szektor_id"] = df_szektor["nev"].apply(szektor_azonosito_nevbol)
    return df_szektor


def benchmark_szektoron_beluli_sulyak(df: pd.DataFrame) -> pd.DataFrame:
    opcio = df["nev"].str.startswith("Opció")
    df_opcio = df.loc[opcio, ["nev", "suly"]].copy()
    df_opcio["szektor_id"] = df_opcio["nev"].apply(szektor_azonosito_nevbol)
    return df_opcio


def aktiv_szektorsulyak_dirichlet(w_bench: np.ndarray, lambda_ertek: float) -> np.ndarray:
    alpha = lambda_ertek * w_bench
    return np.random.dirichlet(alpha)


def aktiv_szektoron_beluli_sulyak(w_bench: np.ndarray, szigma_aktiv: float) -> np.ndarray:
    x = np.random.normal(0, szigma_aktiv, size=len(w_bench))
    epsilon = x - np.mean(x)
    w_port = w_bench + epsilon
    return w_port


def aktivan_kezelt_portfoliok(
    df_benchmark: pd.DataFrame,
    pm_db: int,
) -> list[pd.DataFrame]:

    df_benchmark = df_benchmark.copy()

    df_szektor = benchmark_szektorsulyak(df_benchmark)
    df_opcio = benchmark_szektoron_beluli_sulyak(df_benchmark)

    szektor_idk = df_szektor["szektor_id"].tolist()
    w_szektor_bench = df_szektor["suly"].to_numpy()

    eredmeny = []

    for pm in range(1, pm_db + 1):

        w_szektor_port = aktiv_szektorsulyak_dirichlet(
            w_bench=w_szektor_bench,
            lambda_ertek=lambda_ertek
        )

        sorok = []
        pm_teljes_suly = 0.0

        for i, szektor_id in enumerate(szektor_idk):

            sorok.append({
                "nev": f"Szektor {szektor_id}",
                "suly": w_szektor_port[i]
            })

            aktualis_opciok = df_opcio[df_opcio["szektor_id"] == szektor_id].copy()
            w_opcio_bench = aktualis_opciok["suly"].to_numpy()

            w_opcio_port = aktiv_szektoron_beluli_sulyak(
                w_bench=w_opcio_bench,
                szigma_aktiv=szigma_aktiv
            )

            pm_teljes_suly += w_szektor_port[i] * np.sum(w_opcio_port)

            for j, suly in enumerate(w_opcio_port, start=1):
                sorok.append({
                    "nev": f"Opció {szektor_id},{j}",
                    "suly": suly
                })

        sorok.insert(0, {
            "nev": f"PM {pm}",
            "suly": pm_teljes_suly
        })

        df_pm = pd.DataFrame(sorok)
        eredmeny.append(df_pm)

    return eredmeny