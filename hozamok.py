"""
Ez a fájl az opciós portfólió teljesítményének és hozamának görög
betűk szerinti felbontásához szükséges segédfüggvényeket tartalmazza.
A modul opció-, szektor- és benchmarkszinten számít hozamokat,
hozzájárulásokat, valamint delta-, gamma-, theta-, vega-, rho- és
reziduális komponenseket.

teljesitmeny_es_hozam_felbontas:
    Végrehajtja a teljes hozam- és teljesítményfelbontási folyamatot a
    bemeneti portfólió DataFrame-en. Az eredmény egy rendezett táblázat,
    amely opció-, szektor- és benchmarkszinten tartalmazza a hozamokat,
    görög betűs komponenseket és hozzájárulásokat.
"""

import numpy as np
import pandas as pd


def szektor_azonosito(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    opcio = df["nev"].str.startswith("Opció")
    szektor = df["nev"].str.startswith("Szektor")

    df["szektor_id"] = np.nan
    df.loc[opcio, "szektor_id"] = (
        df.loc[opcio, "nev"].str.extract(r"Opció (\d+),")[0].astype(float)
    )
    df.loc[szektor, "szektor_id"] = (
        df.loc[szektor, "nev"].str.extract(r"Szektor (\d+)")[0].astype(float)
    )

    return df


def differenciak(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["dS"] = np.nan
    df["dSigma"] = np.nan
    df["dR"] = np.nan

    opcio = df["nev"].str.startswith("Opció")

    df.loc[opcio, "dS"] = (
        df.loc[opcio, "reszvenyarfolyam_t1"]
        - df.loc[opcio, "reszvenyarfolyam"]
    )

    df.loc[opcio, "dSigma"] = (
        df.loc[opcio, "volatilitas_t1"]
        - df.loc[opcio, "volatilitas"]
    )

    df.loc[opcio, "dR"] = (
        df.loc[opcio, "kockazatmentes_kamat_t1"]
        - df.loc[opcio, "kockazatmentes_kamat"]
    )

    return df


def opciohozamok(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["hozam"] = np.nan

    opcio = df["nev"].str.startswith("Opció")

    df.loc[opcio, "hozam"] = (
        df.loc[opcio, "ar_t1"] / df.loc[opcio, "ar_t0"] - 1
    )

    return df


def gorog_felbontas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    opcio = df["nev"].str.startswith("Opció")

    dt = (
        df.loc[opcio, "hatralevo_ido"].iloc[0]
        - df.loc[opcio, "hatralevo_ido_t1"].iloc[0]
    )

    df["r_delta"] = np.nan
    df["r_gamma"] = np.nan
    df["r_theta"] = np.nan
    df["r_vega"] = np.nan
    df["r_rho"] = np.nan
    df["r_epsilon"] = np.nan

    df.loc[opcio, "r_delta"] = (
        df.loc[opcio, "delta_t0"] * df.loc[opcio, "dS"] / df.loc[opcio, "ar_t0"]
    )

    df.loc[opcio, "r_gamma"] = (
        0.5
        * df.loc[opcio, "gamma_t0"]
        * df.loc[opcio, "dS"] ** 2
        / df.loc[opcio, "ar_t0"]
    )

    df.loc[opcio, "r_theta"] = (
        df.loc[opcio, "theta_t0"] * dt / df.loc[opcio, "ar_t0"]
    )

    df.loc[opcio, "r_vega"] = (
        df.loc[opcio, "vega_t0"] * df.loc[opcio, "dSigma"] / df.loc[opcio, "ar_t0"]
    )

    df.loc[opcio, "r_rho"] = (
        df.loc[opcio, "rho_t0"] * df.loc[opcio, "dR"] / df.loc[opcio, "ar_t0"]
    )

    df.loc[opcio, "r_epsilon"] = (
        df.loc[opcio, "hozam"]
        - df.loc[opcio, "r_delta"]
        - df.loc[opcio, "r_gamma"]
        - df.loc[opcio, "r_theta"]
        - df.loc[opcio, "r_vega"]
        - df.loc[opcio, "r_rho"]
    )

    return df


def szektorhozamok(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    opcio = df["nev"].str.startswith("Opció")
    szektor = df["nev"].str.startswith("Szektor")

    szektor_hozamok = (
        df.loc[opcio]
        .groupby("szektor_id")
        .apply(lambda x: np.sum(x["suly"] * x["hozam"]))
    )

    for idx in df.index[szektor]:
        aktualis_szektor = df.loc[idx, "szektor_id"]
        df.loc[idx, "hozam"] = szektor_hozamok.loc[aktualis_szektor]

    return df


def szektor_gorog_hozamok(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    opcio = df["nev"].str.startswith("Opció")
    szektor = df["nev"].str.startswith("Szektor")

    gorog_oszlopok = [
        "r_delta",
        "r_gamma",
        "r_theta",
        "r_vega",
        "r_rho",
        "r_epsilon",
    ]

    for oszlop in gorog_oszlopok:
        szektor_ertekek = (
            df.loc[opcio]
            .groupby("szektor_id")
            .apply(lambda x: np.sum(x["suly"] * x[oszlop]))
        )

        for idx in df.index[szektor]:
            aktualis_szektor = df.loc[idx, "szektor_id"]
            df.loc[idx, oszlop] = szektor_ertekek.loc[aktualis_szektor]

    return df


def benchmark_sor(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    opcio = df["nev"].str.startswith("Opció")
    szektor = df["nev"].str.startswith("Szektor")

    uj_sor = {}

    for oszlop in df.columns:
        uj_sor[oszlop] = np.nan

    uj_sor["nev"] = "Benchmark"
    uj_sor["suly"] = df.loc[szektor, "suly"].sum()
    uj_sor["abszolut_suly"] = df.loc[opcio, "abszolut_suly"].sum()

    uj_sor["hozam"] = np.sum(
        df.loc[szektor, "suly"] * df.loc[szektor, "hozam"]
    )

    gorog_oszlopok = [
        "r_delta",
        "r_gamma",
        "r_theta",
        "r_vega",
        "r_rho",
        "r_epsilon",
    ]

    for oszlop in gorog_oszlopok:
        uj_sor[oszlop] = np.sum(
            df.loc[szektor, "suly"] * df.loc[szektor, oszlop]
        )

    uj_sor["kockazatmentes_kamat"] = df.loc[opcio, "kockazatmentes_kamat"].iloc[0]
    uj_sor["kockazatmentes_kamat_t1"] = df.loc[opcio, "kockazatmentes_kamat_t1"].iloc[0]
    uj_sor["dR"] = uj_sor["kockazatmentes_kamat_t1"] - uj_sor["kockazatmentes_kamat"]

    df = pd.concat([df, pd.DataFrame([uj_sor])], ignore_index=True)

    return df


def pozicio_alapu_ertekek(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    opcio = df["nev"].str.startswith("Opció")

    df["pozicio_hozam"] = np.nan
    df["pozicio_r_delta"] = np.nan
    df["pozicio_r_gamma"] = np.nan
    df["pozicio_r_theta"] = np.nan
    df["pozicio_r_vega"] = np.nan
    df["pozicio_r_rho"] = np.nan
    df["pozicio_r_epsilon"] = np.nan

    elojelek = np.where(df.loc[opcio, "irany"] == "long", 1.0, -1.0)

    df.loc[opcio, "pozicio_hozam"] = elojelek * df.loc[opcio, "hozam"]
    df.loc[opcio, "pozicio_r_delta"] = elojelek * df.loc[opcio, "r_delta"]
    df.loc[opcio, "pozicio_r_gamma"] = elojelek * df.loc[opcio, "r_gamma"]
    df.loc[opcio, "pozicio_r_theta"] = elojelek * df.loc[opcio, "r_theta"]
    df.loc[opcio, "pozicio_r_vega"] = elojelek * df.loc[opcio, "r_vega"]
    df.loc[opcio, "pozicio_r_rho"] = elojelek * df.loc[opcio, "r_rho"]
    df.loc[opcio, "pozicio_r_epsilon"] = elojelek * df.loc[opcio, "r_epsilon"]

    return df


def hozzajarulasok(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    opcio = df["nev"].str.startswith("Opció")

    df["hozzajarulas"] = np.nan
    df["hozzajarulas_delta"] = np.nan
    df["hozzajarulas_gamma"] = np.nan
    df["hozzajarulas_theta"] = np.nan
    df["hozzajarulas_vega"] = np.nan
    df["hozzajarulas_rho"] = np.nan
    df["hozzajarulas_epsilon"] = np.nan

    df.loc[opcio, "hozzajarulas"] = (
        df.loc[opcio, "abszolut_suly"] * df.loc[opcio, "hozam"]
    )

    df.loc[opcio, "hozzajarulas_delta"] = (
        df.loc[opcio, "abszolut_suly"] * df.loc[opcio, "r_delta"]
    )

    df.loc[opcio, "hozzajarulas_gamma"] = (
        df.loc[opcio, "abszolut_suly"] * df.loc[opcio, "r_gamma"]
    )

    df.loc[opcio, "hozzajarulas_theta"] = (
        df.loc[opcio, "abszolut_suly"] * df.loc[opcio, "r_theta"]
    )

    df.loc[opcio, "hozzajarulas_vega"] = (
        df.loc[opcio, "abszolut_suly"] * df.loc[opcio, "r_vega"]
    )

    df.loc[opcio, "hozzajarulas_rho"] = (
        df.loc[opcio, "abszolut_suly"] * df.loc[opcio, "r_rho"]
    )

    df.loc[opcio, "hozzajarulas_epsilon"] = (
        df.loc[opcio, "abszolut_suly"] * df.loc[opcio, "r_epsilon"]
    )

    return df


def szektor_hozzajarulasok(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    opcio = df["nev"].str.startswith("Opció")
    szektor = df["nev"].str.startswith("Szektor")

    hozzajarulas_oszlopok = [
        "hozzajarulas",
        "hozzajarulas_delta",
        "hozzajarulas_gamma",
        "hozzajarulas_theta",
        "hozzajarulas_vega",
        "hozzajarulas_rho",
        "hozzajarulas_epsilon",
    ]

    for oszlop in hozzajarulas_oszlopok:
        szektor_ertekek = (
            df.loc[opcio]
            .groupby("szektor_id")[oszlop]
            .sum()
        )

        for idx in df.index[szektor]:
            aktualis_szektor = df.loc[idx, "szektor_id"]
            df.loc[idx, oszlop] = szektor_ertekek.loc[aktualis_szektor]

    return df


def oszlopok_rendezese(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    sorrend = [
        "nev",
        "szektor_id",
        "suly",
        "abszolut_suly",
        "tipus_es_irany",
        "irany",
        "tipus",
        "",

        "reszvenyarfolyam",
        "volatilitas",
        "hatralevo_ido",
        "kotesi_arfolyam",
        "kockazatmentes_kamat",
        "",

        "ar_t0",
        "delta_t0",
        "gamma_t0",
        "vega_t0",
        "theta_t0",
        "rho_t0",
        "",

        "mu_szektor",
        "mu",
        "z_reszvenyar_szektor",
        "z_reszvenyar",
        "z_vol_szektor",
        "u_vol",
        "korrelalt_z_vol",
        "",

        "reszvenyarfolyam_t1",
        "volatilitas_t1",
        "hatralevo_ido_t1",
        "kockazatmentes_kamat_t1",
        "",

        "ar_t1",
        "delta_t1",
        "gamma_t1",
        "vega_t1",
        "theta_t1",
        "rho_t1",
        "",

        "dS",
        "dSigma",
        "dR",
        "",

        "hozam",
        "r_delta",
        "r_gamma",
        "r_theta",
        "r_vega",
        "r_rho",
        "r_epsilon",
        "",

        "pozicio_hozam",
        "pozicio_r_delta",
        "pozicio_r_gamma",
        "pozicio_r_theta",
        "pozicio_r_vega",
        "pozicio_r_rho",
        "pozicio_r_epsilon",
        "",

        "hozzajarulas",
        "hozzajarulas_delta",
        "hozzajarulas_gamma",
        "hozzajarulas_theta",
        "hozzajarulas_vega",
        "hozzajarulas_rho",
        "hozzajarulas_epsilon",
    ]

    uj_df = pd.DataFrame(index=df.index)
    ures_db = 0

    for oszlop in sorrend:
        if oszlop == "":
            ures_db += 1
            uj_df[f"ures_{ures_db}"] = np.nan
        elif oszlop in df.columns:
            uj_df[oszlop] = df[oszlop]

    return uj_df

def teljesitmeny_es_hozam_felbontas(df: pd.DataFrame) -> pd.DataFrame:
    df = szektor_azonosito(df)
    df = differenciak(df)
    df = opciohozamok(df)
    df = gorog_felbontas(df)

    df = pozicio_alapu_ertekek(df)
    df = hozzajarulasok(df)

    df = szektorhozamok(df)
    df = szektor_gorog_hozamok(df)
    df = szektor_hozzajarulasok(df)

    df = benchmark_sor(df)
    df = oszlopok_rendezese(df)

    return df