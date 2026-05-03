"""
Ez a fájl a klasszikus Brinson-modellek és a saját, görög betűkkel
kiegészített teljesítményattribúciós modellek számításait tartalmazza.
A modul portfóliómenedzseri eredményeket, rangsorokat, összefoglaló
táblákat, hasznossági metrikákat és exportálható inputokat állít elő.

modell_eredmenyek:
    Kiszámítja minden aktív portfólióra a klasszikus Brinson-modellek és
    a saját többletfelbontási modellek eredményeit. Az eredmény
    portfóliómenedzserenként négy attribúciós táblát tartalmaz.

rangsor:
    A portfóliómenedzsereket az aktív hozamuk alapján rangsorolja.
    A függvény visszaadja az aktív hozamokat és a rendezett rangsortáblát.

felbontasok:
    PM-szintű összefoglaló táblát készít a kiválasztott attribúciós modell
    eredményeiből. A táblázat az aktív hozamot, a Brinson-hatásokat és az
    aktív görög komponenseket tartalmazza.

osszefoglalo:
    Excel-fájlba menti a benchmarkot, a rangsort, valamint a legjobb és
    legrosszabb portfóliómenedzser részletes eredményeit. A függvény
    visszaadja a legjobb és legrosszabb portfóliómenedzser sorszámát.

portfoliok_hasznossaga:
    Hasznossági metrikák alapján értékeli, hogy a görög betűs felbontás
    mennyire ad többletinformációt az egyes portfóliókra. Az eredmény
    részletes PM-szintű táblát és kategória-összesítést tartalmaz.

szektorsuly_es_aktiv_opciosuly_tablazat_input:
    Összeállítja a szektorsúlyokat és a szektoron belüli átlagos aktív
    opciósúlyokat bemutató táblázat inputját. A függvény a benchmark és
    az aktív portfólió súlyait hasonlítja össze.

word_tablak_input:
    Előkészíti a Word-dokumentumba kerülő attribúciós táblázatokat egy
    kiválasztott portfóliómenedzserhez. A függvény a klasszikus és saját
    modellek eredményeit egységes táblázatos formában adja vissza.

pozitiv_allokacio_extrem_peldak_input:
    Kiválasztja a pozitív többletfelbontási modell allokációs blokkjának
    legnagyobb aktív görög komponenseit. A táblázat ezeket a klasszikus
    Brinson et al. allokációs hatással együtt mutatja be.

pozitiv_szelekcio_extrem_peldak_input:
    Kiválasztja a pozitív többletfelbontási modell szelekciós blokkjának
    legnagyobb aktív görög komponenseit. A táblázat ezeket a klasszikus
    Brinson et al. szelekciós hatással együtt mutatja be.

valtozo_allokacio_extrem_peldak_input:
    Kiválasztja a változó többletfelbontási modell allokációs blokkjának
    legnagyobb aktív görög komponenseit. A táblázat ezeket a klasszikus
    Brinson-Fachler allokációs hatással együtt mutatja be.

rho_adatok:
    Egy előre rögzített, rho-hatás szemléltetésére szolgáló példatáblát
    hoz létre. A táblázat a dolgozat magyarázó részeihez használható
    bemeneti adatokat tartalmazza.

nem_delta_arany_szamitas:
    Szektorszinten kiszámítja, hogy a nem delta jellegű komponensek mekkora
    arányt képviselnek a teljes aktív görög felbontásban. Az eredmény
    küszöbönként mutatja, hány szektor lépi át az adott arányt.

szektoros_felbontasok:
    A kiválasztott modell allokációs blokkjából szektoronként kigyűjti az
    aktív görög komponenseket. Az eredmény a nem delta arányok és ábrák
    számításának bemenete.

szektoros_szelekcio_felbontasok:
    A kiválasztott modell szelekciós blokkjából szektoronként kigyűjti az
    aktív görög komponenseket. Az eredmény a szelekciós nem delta arányok
    és ábrák számításának bemenete.

nem_delta_szelekcio_arany_szamitas:
    Szektorszinten kiszámítja, hogy a szelekciós nem delta komponensek
    mekkora arányt képviselnek a teljes szelekciós görög felbontásban.
    Az eredmény küszöbönként mutatja, hány szektor lépi át az adott arányt.

portfolio_nem_delta_aranyok_szamitas:
    Portfóliómenedzser-szinten számítja ki az allokációs és szelekciós
    nem delta arányokat. Az eredmény küszöbönként mutatja, hány portfólió
    esetén jelentős a nem delta komponensek szerepe.

nyertes_pm_excel:
    Kiválasztja a metrikák alapján nyertes portfóliómenedzsert, majd
    Excel-fájlba menti annak portfólióját és modell szerinti eredményeit.
    A függvény visszaadja a nyertes PM sorszámát és az összefoglaló rangsort.
"""

import os
import numpy as np
import pandas as pd
from typing import List
from aktiv_portfoliok import pm_db

#Portfólió menedzserek száma
pm = pm_db

def benchmark_adat_osszekeszites(df_benchmark: pd.DataFrame) -> dict:
    df_b = df_benchmark.copy()

    szektor = df_b["nev"].str.startswith("Szektor")
    opcio = df_b["nev"].str.startswith("Opció")

    gorog_oszlopok = [
        "r_delta",
        "r_gamma",
        "r_theta",
        "r_vega",
        "r_rho",
        "r_epsilon",
    ]

    benchmark_szektor = df_b.loc[szektor, ["szektor_id", "suly", "hozam"] + gorog_oszlopok].copy()
    benchmark_szektor = benchmark_szektor.rename(columns={
        "suly": "W_i",
        "hozam": "b_i",
        "r_delta": "B_delta",
        "r_gamma": "B_gamma",
        "r_theta": "B_theta",
        "r_vega": "B_vega",
        "r_rho": "B_rho",
        "r_epsilon": "B_epsilon",
    })

    benchmark_opcio = df_b.loc[opcio, ["nev", "szektor_id", "suly", "hozam"] + gorog_oszlopok].copy()
    benchmark_opcio = benchmark_opcio.rename(columns={
        "suly": "W_ij",
        "hozam": "r_ij",
    })

    benchmark_teljes_hozam = float(np.sum(benchmark_szektor["W_i"] * benchmark_szektor["b_i"]))

    benchmark_teljes_gorog = {
        "b_delta": float(np.sum(benchmark_szektor["W_i"] * benchmark_szektor["B_delta"])),
        "b_gamma": float(np.sum(benchmark_szektor["W_i"] * benchmark_szektor["B_gamma"])),
        "b_theta": float(np.sum(benchmark_szektor["W_i"] * benchmark_szektor["B_theta"])),
        "b_vega": float(np.sum(benchmark_szektor["W_i"] * benchmark_szektor["B_vega"])),
        "b_rho": float(np.sum(benchmark_szektor["W_i"] * benchmark_szektor["B_rho"])),
        "b_epsilon": float(np.sum(benchmark_szektor["W_i"] * benchmark_szektor["B_epsilon"])),
    }

    return {
        "benchmark_szektor": benchmark_szektor,
        "benchmark_opcio": benchmark_opcio,
        "benchmark_teljes_hozam": benchmark_teljes_hozam,
        "benchmark_teljes_gorog": benchmark_teljes_gorog,
    }


def portfolio_adat_osszekeszites(df_portfolio: pd.DataFrame, benchmark_adatok: dict) -> dict:
    df_p = df_portfolio.copy()
    df_b_opcio = benchmark_adatok["benchmark_opcio"].copy()

    szektor = df_p["nev"].str.startswith("Szektor")
    opcio = df_p["nev"].str.startswith("Opció")

    portfolio_szektor = df_p.loc[szektor, ["nev", "suly"]].copy()
    portfolio_szektor["szektor_id"] = (
        portfolio_szektor["nev"].str.extract(r"Szektor (\d+)")[0].astype(int)
    )
    portfolio_szektor = portfolio_szektor.rename(columns={"suly": "w_i"})

    portfolio_opcio = df_p.loc[opcio, ["nev", "suly"]].copy()
    portfolio_opcio["szektor_id"] = (
        portfolio_opcio["nev"].str.extract(r"Opció (\d+),")[0].astype(int)
    )
    portfolio_opcio = portfolio_opcio.rename(columns={"suly": "w_ij"})

    df_merge = pd.merge(
        portfolio_opcio,
        df_b_opcio,
        on=["nev", "szektor_id"],
        how="inner"
    )

    portfolio_szektor_hozam = (
        df_merge.groupby("szektor_id")
        .apply(lambda x: pd.Series({
            "r_i": np.sum(x["w_ij"] * x["r_ij"]),
            "R_delta": np.sum(x["w_ij"] * x["r_delta"]),
            "R_gamma": np.sum(x["w_ij"] * x["r_gamma"]),
            "R_theta": np.sum(x["w_ij"] * x["r_theta"]),
            "R_vega": np.sum(x["w_ij"] * x["r_vega"]),
            "R_rho": np.sum(x["w_ij"] * x["r_rho"]),
            "R_epsilon": np.sum(x["w_ij"] * x["r_epsilon"]),
        }))
        .reset_index()
    )

    portfolio_szektor = pd.merge(
        portfolio_szektor[["szektor_id", "w_i"]],
        portfolio_szektor_hozam,
        on="szektor_id",
        how="inner"
    )

    return {
        "portfolio_szektor": portfolio_szektor,
        "portfolio_opcio": portfolio_opcio,
    }


def brinson_fachler_1985_multiindex(benchmark_adatok: dict, portfolio_adatok: dict) -> pd.DataFrame:
    df_b = benchmark_adatok["benchmark_szektor"].copy()
    df_p = portfolio_adatok["portfolio_szektor"].copy()
    b = benchmark_adatok["benchmark_teljes_hozam"]

    df = pd.merge(df_b, df_p, on="szektor_id", how="inner")

    df["aktiv_hozam"] = df["r_i"] - df["b_i"]
    df["allokacio"] = (df["w_i"] - df["W_i"]) * (df["b_i"] - b)
    df["szelekcio"] = df["W_i"] * (df["r_i"] - df["b_i"])
    df["interakcio"] = (df["w_i"] - df["W_i"]) * (df["r_i"] - df["b_i"])

    sorok = []

    for _, row in df.iterrows():
        sorok.append({
            ("Szektor", ""): f"Szektor {int(row['szektor_id'])}",
            ("Súly", "Benchmark"): row["W_i"],
            ("Súly", "Portfólió"): row["w_i"],
            ("Hozam", "Benchmark"): row["b_i"],
            ("Hozam", "Portfólió"): row["r_i"],
            ("Aktív hozam", ""): row["aktiv_hozam"],
            ("Hatás", "Allokáció"): row["allokacio"],
            ("Hatás", "Szelekció"): row["szelekcio"],
            ("Hatás", "Interakció"): row["interakcio"],
        })

    df_out = pd.DataFrame(sorok)

    teljes_portfolio = float(np.sum(df["w_i"] * df["r_i"]))
    aktiv_total = teljes_portfolio - b

    osszesen = pd.DataFrame([{
        ("Szektor", ""): "Összesen",
        ("Súly", "Benchmark"): df["W_i"].sum(),
        ("Súly", "Portfólió"): df["w_i"].sum(),
        ("Hozam", "Benchmark"): b,
        ("Hozam", "Portfólió"): teljes_portfolio,
        ("Aktív hozam", ""): aktiv_total,
        ("Hatás", "Allokáció"): df["allokacio"].sum(),
        ("Hatás", "Szelekció"): df["szelekcio"].sum(),
        ("Hatás", "Interakció"): df["interakcio"].sum(),
    }])

    df_out = pd.concat([df_out, osszesen], ignore_index=True)

    oszlopok = [
        ("Szektor", ""),
        ("Súly", "Benchmark"),
        ("Súly", "Portfólió"),
        ("Hozam", "Benchmark"),
        ("Hozam", "Portfólió"),
        ("Aktív hozam", ""),
        ("Hatás", "Allokáció"),
        ("Hatás", "Szelekció"),
        ("Hatás", "Interakció"),
    ]

    df_out = df_out[oszlopok]
    df_out.columns = pd.MultiIndex.from_tuples(df_out.columns)

    return df_out


def brinson_bhb_1986_multiindex(benchmark_adatok: dict, portfolio_adatok: dict) -> pd.DataFrame:
    df_b = benchmark_adatok["benchmark_szektor"].copy()
    df_p = portfolio_adatok["portfolio_szektor"].copy()
    b = benchmark_adatok["benchmark_teljes_hozam"]

    df = pd.merge(df_b, df_p, on="szektor_id", how="inner")

    df["aktiv_hozam"] = df["r_i"] - df["b_i"]
    df["allokacio"] = (df["w_i"] - df["W_i"]) * df["b_i"]
    df["szelekcio"] = df["W_i"] * (df["r_i"] - df["b_i"])
    df["interakcio"] = (df["w_i"] - df["W_i"]) * (df["r_i"] - df["b_i"])

    sorok = []

    for _, row in df.iterrows():
        sorok.append({
            ("Szektor", ""): f"Szektor {int(row['szektor_id'])}",
            ("Súly", "Benchmark"): row["W_i"],
            ("Súly", "Portfólió"): row["w_i"],
            ("Hozam", "Benchmark"): row["b_i"],
            ("Hozam", "Portfólió"): row["r_i"],
            ("Aktív hozam", ""): row["aktiv_hozam"],
            ("Hatás", "Allokáció"): row["allokacio"],
            ("Hatás", "Szelekció"): row["szelekcio"],
            ("Hatás", "Interakció"): row["interakcio"],
        })

    df_out = pd.DataFrame(sorok)

    teljes_portfolio = float(np.sum(df["w_i"] * df["r_i"]))
    aktiv_total = teljes_portfolio - b

    osszesen = pd.DataFrame([{
        ("Szektor", ""): "Összesen",
        ("Súly", "Benchmark"): df["W_i"].sum(),
        ("Súly", "Portfólió"): df["w_i"].sum(),
        ("Hozam", "Benchmark"): b,
        ("Hozam", "Portfólió"): teljes_portfolio,
        ("Aktív hozam", ""): aktiv_total,
        ("Hatás", "Allokáció"): df["allokacio"].sum(),
        ("Hatás", "Szelekció"): df["szelekcio"].sum(),
        ("Hatás", "Interakció"): df["interakcio"].sum(),
    }])

    df_out = pd.concat([df_out, osszesen], ignore_index=True)

    oszlopok = [
        ("Szektor", ""),
        ("Súly", "Benchmark"),
        ("Súly", "Portfólió"),
        ("Hozam", "Benchmark"),
        ("Hozam", "Portfólió"),
        ("Aktív hozam", ""),
        ("Hatás", "Allokáció"),
        ("Hatás", "Szelekció"),
        ("Hatás", "Interakció"),
    ]

    df_out = df_out[oszlopok]
    df_out.columns = pd.MultiIndex.from_tuples(df_out.columns)

    return df_out


def pozitiv_tobblet_felbontas_multiindex(
    benchmark_adatok: dict,
    portfolio_adatok: dict
) -> pd.DataFrame:
    df_b = benchmark_adatok["benchmark_szektor"].copy()
    df_p = portfolio_adatok["portfolio_szektor"].copy()

    df = pd.merge(df_b, df_p, on="szektor_id", how="inner")

    df["aktiv_hozam"] = df["r_i"] - df["b_i"]

    df["allokacio"] = (df["w_i"] - df["W_i"]) * df["b_i"]
    df["szelekcio"] = df["W_i"] * (df["r_i"] - df["b_i"])
    df["interakcio"] = (df["w_i"] - df["W_i"]) * (df["r_i"] - df["b_i"])

    df["allokacio_delta"] = (df["w_i"] - df["W_i"]) * df["B_delta"]
    df["allokacio_gamma"] = (df["w_i"] - df["W_i"]) * df["B_gamma"]
    df["allokacio_theta"] = (df["w_i"] - df["W_i"]) * df["B_theta"]
    df["allokacio_vega"] = (df["w_i"] - df["W_i"]) * df["B_vega"]
    df["allokacio_rho"] = (df["w_i"] - df["W_i"]) * df["B_rho"]
    df["allokacio_residual"] = (df["w_i"] - df["W_i"]) * df["B_epsilon"]

    df["szelekcio_delta"] = df["W_i"] * (df["R_delta"] - df["B_delta"])
    df["szelekcio_gamma"] = df["W_i"] * (df["R_gamma"] - df["B_gamma"])
    df["szelekcio_theta"] = df["W_i"] * (df["R_theta"] - df["B_theta"])
    df["szelekcio_vega"] = df["W_i"] * (df["R_vega"] - df["B_vega"])
    df["szelekcio_rho"] = df["W_i"] * (df["R_rho"] - df["B_rho"])
    df["szelekcio_residual"] = df["W_i"] * (df["R_epsilon"] - df["B_epsilon"])

    sorok = []

    for _, row in df.iterrows():
        sorok.append({
            ("Szektor", ""): f"Szektor {int(row['szektor_id'])}",
            ("Súly", "Benchmark"): row["W_i"],
            ("Súly", "Portfólió"): row["w_i"],
            ("Hozam", "Benchmark"): row["b_i"],
            ("Hozam", "Portfólió"): row["r_i"],
            ("Aktív hozam", ""): row["aktiv_hozam"],
            ("Hatás", "Allokáció"): row["allokacio"],
            ("Hatás", "Szelekció"): row["szelekcio"],
            ("Hatás", "Interakció"): row["interakcio"],
            ("Allokáció", "Aktív delta"): row["allokacio_delta"],
            ("Allokáció", "Aktív gamma"): row["allokacio_gamma"],
            ("Allokáció", "Aktív theta"): row["allokacio_theta"],
            ("Allokáció", "Aktív vega"): row["allokacio_vega"],
            ("Allokáció", "Aktív rho"): row["allokacio_rho"],
            ("Allokáció", "Aktív residual"): row["allokacio_residual"],
            ("Szelekció", "Aktív delta"): row["szelekcio_delta"],
            ("Szelekció", "Aktív gamma"): row["szelekcio_gamma"],
            ("Szelekció", "Aktív theta"): row["szelekcio_theta"],
            ("Szelekció", "Aktív vega"): row["szelekcio_vega"],
            ("Szelekció", "Aktív rho"): row["szelekcio_rho"],
            ("Szelekció", "Aktív residual"): row["szelekcio_residual"],
        })

    df_out = pd.DataFrame(sorok)

    teljes_portfolio = float(np.sum(df["w_i"] * df["r_i"]))
    benchmark_teljes = float(np.sum(df["W_i"] * df["b_i"]))
    aktiv_total = teljes_portfolio - benchmark_teljes

    osszesen = pd.DataFrame([{
        ("Szektor", ""): "Összesen",
        ("Súly", "Benchmark"): df["W_i"].sum(),
        ("Súly", "Portfólió"): df["w_i"].sum(),
        ("Hozam", "Benchmark"): benchmark_teljes,
        ("Hozam", "Portfólió"): teljes_portfolio,
        ("Aktív hozam", ""): aktiv_total,
        ("Hatás", "Allokáció"): df["allokacio"].sum(),
        ("Hatás", "Szelekció"): df["szelekcio"].sum(),
        ("Hatás", "Interakció"): df["interakcio"].sum(),
        ("Allokáció", "Aktív delta"): df["allokacio_delta"].sum(),
        ("Allokáció", "Aktív gamma"): df["allokacio_gamma"].sum(),
        ("Allokáció", "Aktív theta"): df["allokacio_theta"].sum(),
        ("Allokáció", "Aktív vega"): df["allokacio_vega"].sum(),
        ("Allokáció", "Aktív rho"): df["allokacio_rho"].sum(),
        ("Allokáció", "Aktív residual"): df["allokacio_residual"].sum(),
        ("Szelekció", "Aktív delta"): df["szelekcio_delta"].sum(),
        ("Szelekció", "Aktív gamma"): df["szelekcio_gamma"].sum(),
        ("Szelekció", "Aktív theta"): df["szelekcio_theta"].sum(),
        ("Szelekció", "Aktív vega"): df["szelekcio_vega"].sum(),
        ("Szelekció", "Aktív rho"): df["szelekcio_rho"].sum(),
        ("Szelekció", "Aktív residual"): df["szelekcio_residual"].sum(),
    }])

    df_out = pd.concat([df_out, osszesen], ignore_index=True)

    oszlopok = [
        ("Szektor", ""),
        ("Súly", "Benchmark"),
        ("Súly", "Portfólió"),
        ("Hozam", "Benchmark"),
        ("Hozam", "Portfólió"),
        ("Aktív hozam", ""),
        ("Hatás", "Allokáció"),
        ("Hatás", "Szelekció"),
        ("Hatás", "Interakció"),
        ("Allokáció", "Aktív delta"),
        ("Allokáció", "Aktív gamma"),
        ("Allokáció", "Aktív theta"),
        ("Allokáció", "Aktív vega"),
        ("Allokáció", "Aktív rho"),
        ("Allokáció", "Aktív residual"),
        ("Szelekció", "Aktív delta"),
        ("Szelekció", "Aktív gamma"),
        ("Szelekció", "Aktív theta"),
        ("Szelekció", "Aktív vega"),
        ("Szelekció", "Aktív rho"),
        ("Szelekció", "Aktív residual"),
    ]

    df_out = df_out[oszlopok]
    df_out.columns = pd.MultiIndex.from_tuples(df_out.columns)

    return df_out


def valtozo_tobblet_felbontas_multiindex(
    benchmark_adatok: dict,
    portfolio_adatok: dict
) -> pd.DataFrame:
    df_b = benchmark_adatok["benchmark_szektor"].copy()
    df_p = portfolio_adatok["portfolio_szektor"].copy()
    benchmark_teljes_gorog = benchmark_adatok["benchmark_teljes_gorog"].copy()

    df = pd.merge(df_b, df_p, on="szektor_id", how="inner")

    b = benchmark_adatok["benchmark_teljes_hozam"]

    b_delta = benchmark_teljes_gorog["b_delta"]
    b_gamma = benchmark_teljes_gorog["b_gamma"]
    b_theta = benchmark_teljes_gorog["b_theta"]
    b_vega = benchmark_teljes_gorog["b_vega"]
    b_rho = benchmark_teljes_gorog["b_rho"]
    b_epsilon = benchmark_teljes_gorog["b_epsilon"]

    df["aktiv_hozam"] = df["r_i"] - df["b_i"]

    df["allokacio"] = (df["w_i"] - df["W_i"]) * (df["b_i"] - b)
    df["szelekcio"] = df["W_i"] * (df["r_i"] - df["b_i"])
    df["interakcio"] = (df["w_i"] - df["W_i"]) * (df["r_i"] - df["b_i"])

    df["allokacio_delta"] = (df["w_i"] - df["W_i"]) * (df["B_delta"] - b_delta)
    df["allokacio_gamma"] = (df["w_i"] - df["W_i"]) * (df["B_gamma"] - b_gamma)
    df["allokacio_theta"] = (df["w_i"] - df["W_i"]) * (df["B_theta"] - b_theta)
    df["allokacio_vega"] = (df["w_i"] - df["W_i"]) * (df["B_vega"] - b_vega)
    df["allokacio_rho"] = (df["w_i"] - df["W_i"]) * (df["B_rho"] - b_rho)
    df["allokacio_residual"] = (df["w_i"] - df["W_i"]) * (df["B_epsilon"] - b_epsilon)

    df["szelekcio_delta"] = df["W_i"] * (df["R_delta"] - df["B_delta"])
    df["szelekcio_gamma"] = df["W_i"] * (df["R_gamma"] - df["B_gamma"])
    df["szelekcio_theta"] = df["W_i"] * (df["R_theta"] - df["B_theta"])
    df["szelekcio_vega"] = df["W_i"] * (df["R_vega"] - df["B_vega"])
    df["szelekcio_rho"] = df["W_i"] * (df["R_rho"] - df["B_rho"])
    df["szelekcio_residual"] = df["W_i"] * (df["R_epsilon"] - df["B_epsilon"])

    sorok = []

    for _, row in df.iterrows():
        sorok.append({
            ("Szektor", ""): f"Szektor {int(row['szektor_id'])}",
            ("Súly", "Benchmark"): row["W_i"],
            ("Súly", "Portfólió"): row["w_i"],
            ("Hozam", "Benchmark"): row["b_i"],
            ("Hozam", "Portfólió"): row["r_i"],
            ("Aktív hozam", ""): row["aktiv_hozam"],
            ("Hatás", "Allokáció"): row["allokacio"],
            ("Hatás", "Szelekció"): row["szelekcio"],
            ("Hatás", "Interakció"): row["interakcio"],
            ("Allokáció", "Aktív delta"): row["allokacio_delta"],
            ("Allokáció", "Aktív gamma"): row["allokacio_gamma"],
            ("Allokáció", "Aktív theta"): row["allokacio_theta"],
            ("Allokáció", "Aktív vega"): row["allokacio_vega"],
            ("Allokáció", "Aktív rho"): row["allokacio_rho"],
            ("Allokáció", "Aktív residual"): row["allokacio_residual"],
            ("Szelekció", "Aktív delta"): row["szelekcio_delta"],
            ("Szelekció", "Aktív gamma"): row["szelekcio_gamma"],
            ("Szelekció", "Aktív theta"): row["szelekcio_theta"],
            ("Szelekció", "Aktív vega"): row["szelekcio_vega"],
            ("Szelekció", "Aktív rho"): row["szelekcio_rho"],
            ("Szelekció", "Aktív residual"): row["szelekcio_residual"],
        })

    df_out = pd.DataFrame(sorok)

    teljes_portfolio = float(np.sum(df["w_i"] * df["r_i"]))
    benchmark_teljes = float(np.sum(df["W_i"] * df["b_i"]))
    aktiv_total = teljes_portfolio - benchmark_teljes

    osszesen = pd.DataFrame([{
        ("Szektor", ""): "Összesen",
        ("Súly", "Benchmark"): df["W_i"].sum(),
        ("Súly", "Portfólió"): df["w_i"].sum(),
        ("Hozam", "Benchmark"): benchmark_teljes,
        ("Hozam", "Portfólió"): teljes_portfolio,
        ("Aktív hozam", ""): aktiv_total,
        ("Hatás", "Allokáció"): df["allokacio"].sum(),
        ("Hatás", "Szelekció"): df["szelekcio"].sum(),
        ("Hatás", "Interakció"): df["interakcio"].sum(),
        ("Allokáció", "Aktív delta"): df["allokacio_delta"].sum(),
        ("Allokáció", "Aktív gamma"): df["allokacio_gamma"].sum(),
        ("Allokáció", "Aktív theta"): df["allokacio_theta"].sum(),
        ("Allokáció", "Aktív vega"): df["allokacio_vega"].sum(),
        ("Allokáció", "Aktív rho"): df["allokacio_rho"].sum(),
        ("Allokáció", "Aktív residual"): df["allokacio_residual"].sum(),
        ("Szelekció", "Aktív delta"): df["szelekcio_delta"].sum(),
        ("Szelekció", "Aktív gamma"): df["szelekcio_gamma"].sum(),
        ("Szelekció", "Aktív theta"): df["szelekcio_theta"].sum(),
        ("Szelekció", "Aktív vega"): df["szelekcio_vega"].sum(),
        ("Szelekció", "Aktív rho"): df["szelekcio_rho"].sum(),
        ("Szelekció", "Aktív residual"): df["szelekcio_residual"].sum(),
    }])

    df_out = pd.concat([df_out, osszesen], ignore_index=True)

    oszlopok = [
        ("Szektor", ""),
        ("Súly", "Benchmark"),
        ("Súly", "Portfólió"),
        ("Hozam", "Benchmark"),
        ("Hozam", "Portfólió"),
        ("Aktív hozam", ""),
        ("Hatás", "Allokáció"),
        ("Hatás", "Szelekció"),
        ("Hatás", "Interakció"),
        ("Allokáció", "Aktív delta"),
        ("Allokáció", "Aktív gamma"),
        ("Allokáció", "Aktív theta"),
        ("Allokáció", "Aktív vega"),
        ("Allokáció", "Aktív rho"),
        ("Allokáció", "Aktív residual"),
        ("Szelekció", "Aktív delta"),
        ("Szelekció", "Aktív gamma"),
        ("Szelekció", "Aktív theta"),
        ("Szelekció", "Aktív vega"),
        ("Szelekció", "Aktív rho"),
        ("Szelekció", "Aktív residual"),
    ]

    df_out = df_out[oszlopok]
    df_out.columns = pd.MultiIndex.from_tuples(df_out.columns)

    return df_out

"""
0 = BF 1985
1 = BHB 1986
2 = pozitív többlet
3 = változó többlet
"""

def modell_eredmenyek(
    benchmark_df: pd.DataFrame,
    aktiv_portfoliok: List[pd.DataFrame]
) -> List[list[pd.DataFrame]]:
    benchmark_adatok = benchmark_adat_osszekeszites(benchmark_df)

    eredmenyek = []

    for df_portfolio in aktiv_portfoliok:
        portfolio_adatok = portfolio_adat_osszekeszites(
            df_portfolio,
            benchmark_adatok
        )

        bf_1985_df = brinson_fachler_1985_multiindex(
            benchmark_adatok,
            portfolio_adatok
        )

        bhb_1986_df = brinson_bhb_1986_multiindex(
            benchmark_adatok,
            portfolio_adatok
        )

        pozitiv_df = pozitiv_tobblet_felbontas_multiindex(
            benchmark_adatok,
            portfolio_adatok
        )

        valtozo_df = valtozo_tobblet_felbontas_multiindex(
            benchmark_adatok,
            portfolio_adatok
        )

        eredmenyek.append([
            bf_1985_df,
            bhb_1986_df,
            pozitiv_df,
            valtozo_df
        ])

    return eredmenyek


def rangsor(eredmenyek: list[list[pd.DataFrame]]) -> tuple[dict[int, float], pd.DataFrame]:
    aktiv_hozamok = {}

    for i, pm_eredmeny in enumerate(eredmenyek, start=1):
        bf_1985_df = pm_eredmeny[0]

        osszesen_sor = bf_1985_df[bf_1985_df["Szektor"] == "Összesen"]

        if osszesen_sor.empty:
            raise ValueError(f"A(z) PM {i} BF 1985 eredményében nincs 'Összesen' sor.")

        aktiv_hozam = float(osszesen_sor["Aktív hozam"].iloc[0])
        aktiv_hozamok[i] = aktiv_hozam

    rangsor_df = pd.DataFrame({
        "PM": list(aktiv_hozamok.keys()),
        "Aktív hozam": list(aktiv_hozamok.values())
    })

    rangsor_df = rangsor_df.sort_values(
        by="Aktív hozam",
        ascending=False
    ).reset_index(drop=True)

    rangsor_df["Helyezés"] = rangsor_df.index + 1

    rangsor_df = rangsor_df[["Helyezés", "PM", "Aktív hozam"]]

    return aktiv_hozamok, rangsor_df


def felbontasok(
    eredmenyek: list[list[pd.DataFrame]],
    modell_index: int = 2
) -> pd.DataFrame:
    """
    PM-szintű összefoglaló táblát készít a kiválasztott modell alapján.

    modell_index:
        0 = BF 1985
        1 = BHB 1986
        2 = pozitív többlet felbontás
        3 = változó többlet felbontás
    """

    sorok = []

    for pm_sorszam, pm_eredmeny in enumerate(eredmenyek, start=1):
        df_modell = pm_eredmeny[modell_index]

        osszesen_sor = df_modell[df_modell[("Szektor", "")] == "Összesen"]

        if osszesen_sor.empty:
            raise ValueError(f"A(z) PM {pm_sorszam} eredményében nincs 'Összesen' sor.")

        sor = osszesen_sor.iloc[0]

        sorok.append({
            "PM": pm_sorszam,
            "Aktív hozam": float(sor[("Aktív hozam", "")]),
            "Allokáció": float(sor[("Hatás", "Allokáció")]),
            "Szelekció": float(sor[("Hatás", "Szelekció")]),
            "Interakció": float(sor[("Hatás", "Interakció")]),

            "Allokáció - Aktív delta": float(sor[("Allokáció", "Aktív delta")]),
            "Allokáció - Aktív gamma": float(sor[("Allokáció", "Aktív gamma")]),
            "Allokáció - Aktív theta": float(sor[("Allokáció", "Aktív theta")]),
            "Allokáció - Aktív vega": float(sor[("Allokáció", "Aktív vega")]),
            "Allokáció - Aktív rho": float(sor[("Allokáció", "Aktív rho")]),
            "Allokáció - Aktív residual": float(sor[("Allokáció", "Aktív residual")]),

            "Szelekció - Aktív delta": float(sor[("Szelekció", "Aktív delta")]),
            "Szelekció - Aktív gamma": float(sor[("Szelekció", "Aktív gamma")]),
            "Szelekció - Aktív theta": float(sor[("Szelekció", "Aktív theta")]),
            "Szelekció - Aktív vega": float(sor[("Szelekció", "Aktív vega")]),
            "Szelekció - Aktív rho": float(sor[("Szelekció", "Aktív rho")]),
            "Szelekció - Aktív residual": float(sor[("Szelekció", "Aktív residual")]),
        })

    return pd.DataFrame(sorok)


def osszefoglalo(
    benchmark_df: pd.DataFrame,
    negy_modell_eredmenyei,
    aktiv_portfoliok,
    port_men_rangsor,
    fajl_utvonal: str,
    fajlnev: str
) -> tuple[int, int]:
    teljes_fajl_utvonal = os.path.join(fajl_utvonal, fajlnev)

    rangsor_df = port_men_rangsor[1]

    legjobb_pm = int(rangsor_df.iloc[0]["PM"])
    legrosszabb_pm = int(rangsor_df.iloc[-1]["PM"])

    legjobb_bf, legjobb_bhb, legjobb_poz, legjobb_valt = (
        negy_modell_eredmenyei[legjobb_pm - 1]
    )
    legrosszabb_bf, legrosszabb_bhb, legrosszabb_poz, legrosszabb_valt = (
        negy_modell_eredmenyei[legrosszabb_pm - 1]
    )

    legjobb_aktiv_portfolio = aktiv_portfoliok[legjobb_pm - 1]
    legrosszabb_aktiv_portfolio = aktiv_portfoliok[legrosszabb_pm - 1]

    osszegzes_df = pd.DataFrame({
        "Mutató": [
            "Legjobb portfóliómenedzser",
            "Legjobb portfóliómenedzser aktív hozama",
            "Legrosszabb portfóliómenedzser",
            "Legrosszabb portfóliómenedzser aktív hozama",
        ],
        "Érték": [
            legjobb_pm,
            float(rangsor_df.iloc[0]["Aktív hozam"]),
            legrosszabb_pm,
            float(rangsor_df.iloc[-1]["Aktív hozam"]),
        ]
    })

    with pd.ExcelWriter(teljes_fajl_utvonal, engine="openpyxl") as writer:
        benchmark_df.to_excel(writer, sheet_name="Benchmark", index=False)
        rangsor_df.to_excel(writer, sheet_name="Rangsor", index=False)
        osszegzes_df.to_excel(writer, sheet_name="Osszegzes", index=False)

        legjobb_aktiv_portfolio.to_excel(
            writer,
            sheet_name=f"Legjobb_PM{legjobb_pm}_AktivPortfolio",
            index=False
        )
        legjobb_bf.to_excel(
            writer,
            sheet_name=f"Legjobb_PM{legjobb_pm}_BF1985"
        )
        legjobb_bhb.to_excel(
            writer,
            sheet_name=f"Legjobb_PM{legjobb_pm}_BHB1986"
        )
        legjobb_poz.to_excel(
            writer,
            sheet_name=f"Legjobb_PM{legjobb_pm}_Pozitiv"
        )
        legjobb_valt.to_excel(
            writer,
            sheet_name=f"Legjobb_PM{legjobb_pm}_Valtozo"
        )

        legrosszabb_aktiv_portfolio.to_excel(
            writer,
            sheet_name=f"Legrosszabb_PM{legrosszabb_pm}_AktivPortfolio",
            index=False
        )
        legrosszabb_bf.to_excel(
            writer,
            sheet_name=f"Legrosszabb_PM{legrosszabb_pm}_BF1985"
        )
        legrosszabb_bhb.to_excel(
            writer,
            sheet_name=f"Legrosszabb_PM{legrosszabb_pm}_BHB1986"
        )
        legrosszabb_poz.to_excel(
            writer,
            sheet_name=f"Legrosszabb_PM{legrosszabb_pm}_Pozitiv"
        )
        legrosszabb_valt.to_excel(
            writer,
            sheet_name=f"Legrosszabb_PM{legrosszabb_pm}_Valtozo"
        )

    return legjobb_pm, legrosszabb_pm


def szektoros_felbontasok(eredmenyek, modell_index=3):
    sorok = []

    for pm_sorszam, pm_eredmeny in enumerate(eredmenyek, start=1):
        df_modell = pm_eredmeny[modell_index].copy()

        df_modell = df_modell[df_modell[("Szektor", "")] != "Összesen"]

        for _, sor in df_modell.iterrows():
            sorok.append({
                "delta": float(sor[("Allokáció", "Aktív delta")]),
                "gamma": float(sor[("Allokáció", "Aktív gamma")]),
                "theta": float(sor[("Allokáció", "Aktív theta")]),
                "vega": float(sor[("Allokáció", "Aktív vega")]),
                "rho": float(sor[("Allokáció", "Aktív rho")]),
                "residual": float(sor[("Allokáció", "Aktív residual")]),
            })

    return pd.DataFrame(sorok)


def nem_delta_arany_szamitas(df, lepes=1.0):
    df = df.copy()

    delta = df["delta"].abs()
    gamma = df["gamma"].abs()
    theta = df["theta"].abs()
    vega = df["vega"].abs()
    rho = df["rho"].abs()
    residual = df["residual"].abs()

    nem_delta = gamma + theta + vega + rho
    teljes = delta + nem_delta + residual

    eps = 1e-12

    df["arany"] = np.where(
        teljes > eps,
        nem_delta / teljes,
        0.0
    )

    kuszobok = np.arange(0, 101, lepes)

    eredmeny = []

    for k in kuszobok:
        k_arany = k / 100.0
        db = (df["arany"] > k_arany).sum()

        eredmeny.append({
            "Küszöb (%)": k,
            "Szektorok száma": db
        })

    return pd.DataFrame(eredmeny)


def szektoros_szelekcio_felbontasok(eredmenyek, modell_index=3):
    sorok = []

    for pm_sorszam, pm_eredmeny in enumerate(eredmenyek, start=1):
        df_modell = pm_eredmeny[modell_index].copy()

        df_modell = df_modell[df_modell[("Szektor", "")] != "Összesen"]

        for _, sor in df_modell.iterrows():
            sorok.append({
                "delta": float(sor[("Szelekció", "Aktív delta")]),
                "gamma": float(sor[("Szelekció", "Aktív gamma")]),
                "theta": float(sor[("Szelekció", "Aktív theta")]),
                "vega": float(sor[("Szelekció", "Aktív vega")]),
                "rho": float(sor[("Szelekció", "Aktív rho")]),
                "residual": float(sor[("Szelekció", "Aktív residual")]),
            })

    return pd.DataFrame(sorok)


def nem_delta_szelekcio_arany_szamitas(df, lepes=1.0):
    df = df.copy()

    delta = df["delta"].abs()
    gamma = df["gamma"].abs()
    theta = df["theta"].abs()
    vega = df["vega"].abs()
    rho = df["rho"].abs()
    residual = df["residual"].abs()

    nem_delta = gamma + theta + vega + rho

    teljes = delta + nem_delta + residual

    eps = 1e-12

    df["arany"] = np.where(
        teljes > eps,
        nem_delta / teljes,
        0.0
    )

    kuszobok = np.arange(0, 101, lepes)

    eredmeny = []

    for k in kuszobok:
        k_arany = k / 100.0
        db = (df["arany"] > k_arany).sum()

        eredmeny.append({
            "Küszöb (%)": k,
            "Szektorok száma": db
        })

    return pd.DataFrame(eredmeny)


def portfolio_nem_delta_aranyok_szamitas(df: pd.DataFrame, lepes: float = 1.0) -> pd.DataFrame:
    df = df.copy()

    allokacio_delta = df["Allokáció - Aktív delta"].abs()
    allokacio_gamma = df["Allokáció - Aktív gamma"].abs()
    allokacio_theta = df["Allokáció - Aktív theta"].abs()
    allokacio_vega = df["Allokáció - Aktív vega"].abs()
    allokacio_rho = df["Allokáció - Aktív rho"].abs()
    allokacio_residual = df["Allokáció - Aktív residual"].abs()

    szelekcio_delta = df["Szelekció - Aktív delta"].abs()
    szelekcio_gamma = df["Szelekció - Aktív gamma"].abs()
    szelekcio_theta = df["Szelekció - Aktív theta"].abs()
    szelekcio_vega = df["Szelekció - Aktív vega"].abs()
    szelekcio_rho = df["Szelekció - Aktív rho"].abs()
    szelekcio_residual = df["Szelekció - Aktív residual"].abs()

    allokacio_nem_delta = (
        allokacio_gamma + allokacio_theta + allokacio_vega + allokacio_rho
    )
    allokacio_teljes = (
        allokacio_delta + allokacio_gamma + allokacio_theta
        + allokacio_vega + allokacio_rho + allokacio_residual
    )

    szelekcio_nem_delta = (
        szelekcio_gamma + szelekcio_theta + szelekcio_vega + szelekcio_rho
    )
    szelekcio_teljes = (
        szelekcio_delta + szelekcio_gamma + szelekcio_theta
        + szelekcio_vega + szelekcio_rho + szelekcio_residual
    )

    eps = 1e-12

    df["allokacio_arany"] = np.where(
        allokacio_teljes > eps,
        allokacio_nem_delta / allokacio_teljes,
        0.0
    )

    df["szelekcio_arany"] = np.where(
        szelekcio_teljes > eps,
        szelekcio_nem_delta / szelekcio_teljes,
        0.0
    )

    kuszobok = np.arange(0, 101, lepes)

    sorok = []

    for k in kuszobok:
        k_arany = k / 100.0

        db_allokacio = int((df["allokacio_arany"] > k_arany).sum())
        db_szelekcio = int((df["szelekcio_arany"] > k_arany).sum())

        sorok.append({
            "Küszöb (%)": k,
            "Allokáció": db_allokacio,
            "Szelekció": db_szelekcio
        })

    return pd.DataFrame(sorok)


def hasznossagi_kategoria(M: float, pi: float, alfa: float = 0.7) -> tuple[str, float]:
    H = alfa * M + (1 - alfa) * pi

    if H < 0.2:
        kategoria = "Nem hasznos"
    elif H < 0.4:
        kategoria = "Gyengén hasznos"
    elif H < 0.6:
        kategoria = "Közepesen hasznos"
    elif H < 0.8:
        kategoria = "Hasznos"
    else:
        kategoria = "Nagyon hasznos"

    return kategoria, H


def kategoriapont(kategoria: str) -> int:
    sorrend = {
        "Nem besorolható": 0,
        "Nem hasznos": 1,
        "Gyengén hasznos": 2,
        "Közepesen hasznos": 3,
        "Hasznos": 4,
        "Nagyon hasznos": 5,
    }
    return sorrend[kategoria]


def pontbol_kategoria(pont: int) -> str:
    vissza = {
        0: "Nem besorolható",
        1: "Nem hasznos",
        2: "Gyengén hasznos",
        3: "Közepesen hasznos",
        4: "Hasznos",
        5: "Nagyon hasznos",
    }
    return vissza[pont]


def _M_ertek_szamitas(
    delta: float,
    gamma: float,
    theta: float,
    vega: float,
    rho: float,
    residual: float
) -> float:
    delta = abs(float(delta))
    gamma = abs(float(gamma))
    theta = abs(float(theta))
    vega = abs(float(vega))
    rho = abs(float(rho))
    residual = abs(float(residual))

    nevezo = delta + gamma + theta + vega + rho + residual
    szamlalo = gamma + theta + vega + rho

    if nevezo > 1e-12:
        return szamlalo / nevezo

    return 0.0


def portfoliok_hasznossaga(
    eredmenyek: list[list[pd.DataFrame]],
    modell_index: int = 3,
    kuszob: float = 0.3,
    alfa: float = 0.7
) -> tuple[pd.DataFrame, pd.DataFrame]:
    sorok = []

    for pm_sorszam, pm_eredmeny in enumerate(eredmenyek, start=1):
        df_modell = pm_eredmeny[modell_index].copy()

        df_szektor = df_modell[df_modell[("Szektor", "")] != "Összesen"].copy()
        df_osszesen = df_modell[df_modell[("Szektor", "")] == "Összesen"].copy()

        if df_osszesen.empty:
            raise ValueError(f"A(z) PM {pm_sorszam} eredményében nincs 'Összesen' sor.")

        M_szektor = []
        M_szektor_A = []
        M_szektor_S = []

        for _, sor in df_szektor.iterrows():
            M_i_A = _M_ertek_szamitas(
                sor[("Allokáció", "Aktív delta")],
                sor[("Allokáció", "Aktív gamma")],
                sor[("Allokáció", "Aktív theta")],
                sor[("Allokáció", "Aktív vega")],
                sor[("Allokáció", "Aktív rho")],
                sor[("Allokáció", "Aktív residual")]
            )

            M_i_S = _M_ertek_szamitas(
                sor[("Szelekció", "Aktív delta")],
                sor[("Szelekció", "Aktív gamma")],
                sor[("Szelekció", "Aktív theta")],
                sor[("Szelekció", "Aktív vega")],
                sor[("Szelekció", "Aktív rho")],
                sor[("Szelekció", "Aktív residual")]
            )

            M_i = max(M_i_A, M_i_S)

            M_szektor_A.append(M_i_A)
            M_szektor_S.append(M_i_S)
            M_szektor.append(M_i)

        pi_A = float(np.mean(np.array(M_szektor_A) > kuszob))
        pi_S = float(np.mean(np.array(M_szektor_S) > kuszob))
        pi = float(np.mean(np.array(M_szektor) > kuszob))

        sor_pm = df_osszesen.iloc[0]

        M_p_A = _M_ertek_szamitas(
            sor_pm[("Allokáció", "Aktív delta")],
            sor_pm[("Allokáció", "Aktív gamma")],
            sor_pm[("Allokáció", "Aktív theta")],
            sor_pm[("Allokáció", "Aktív vega")],
            sor_pm[("Allokáció", "Aktív rho")],
            sor_pm[("Allokáció", "Aktív residual")]
        )

        M_p_S = _M_ertek_szamitas(
            sor_pm[("Szelekció", "Aktív delta")],
            sor_pm[("Szelekció", "Aktív gamma")],
            sor_pm[("Szelekció", "Aktív theta")],
            sor_pm[("Szelekció", "Aktív vega")],
            sor_pm[("Szelekció", "Aktív rho")],
            sor_pm[("Szelekció", "Aktív residual")]
        )

        M_p = max(M_p_A, M_p_S)
        kategoria, H = hasznossagi_kategoria(M_p, pi, alfa)

        sorok.append({
            "PM": pm_sorszam,
            "M_pm,p^A": M_p_A,
            "M_pm,p^S": M_p_S,
            "pi^A": pi_A,
            "pi^S": pi_S,
            "M_pm,p": M_p,
            "pi": pi,
            "H": H,
            "Kategória": kategoria
        })

    reszletes_df = pd.DataFrame(sorok)

    kategoriak_sorrendben = [
        "Nem hasznos",
        "Gyengén hasznos",
        "Közepesen hasznos",
        "Hasznos",
        "Nagyon hasznos",
    ]

    osszesites_df = (
        reszletes_df["Kategória"]
        .value_counts()
        .reindex(kategoriak_sorrendben, fill_value=0)
        .reset_index()
    )
    osszesites_df.columns = ["Kategória", "Darabszám"]

    return reszletes_df, osszesites_df


def multiindex_oszlopok_lapitasa(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):
        uj_oszlopok = []

        for col in df.columns:
            reszek = [str(x) for x in col if str(x) != ""]
            uj_oszlopok.append(" - ".join(reszek))

        df.columns = uj_oszlopok

    return df


def pm_pontozas(
    eredmenyek: list[list[pd.DataFrame]],
    modell_index: int = 3,
    kuszob: float = 0.005
) -> pd.DataFrame:
    df = felbontasok(eredmenyek, modell_index=modell_index).copy()

    pontozando_oszlopok = [
        "Allokáció - Aktív delta",
        "Allokáció - Aktív gamma",
        "Allokáció - Aktív theta",
        "Allokáció - Aktív vega",
        "Allokáció - Aktív rho",
        "Szelekció - Aktív delta",
        "Szelekció - Aktív gamma",
        "Szelekció - Aktív theta",
        "Szelekció - Aktív vega",
        "Szelekció - Aktív rho",
    ]

    for oszlop in pontozando_oszlopok:
        df[f"Pont - {oszlop}"] = (df[oszlop].abs() > kuszob).astype(int)

    pont_oszlopok = [f"Pont - {oszlop}" for oszlop in pontozando_oszlopok]
    df["Pontszám"] = df[pont_oszlopok].sum(axis=1)

    return df


def pm_metrikak_es_kategoriak(
    eredmenyek: list[list[pd.DataFrame]],
    pm_sorszam: int,
    modell_index: int = 3,
    kuszob: float = 0.3,
    alfa: float = 0.7
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_modell = eredmenyek[pm_sorszam - 1][modell_index].copy()

    df_szektor = df_modell[df_modell[("Szektor", "")] != "Összesen"].copy()
    df_osszesen = df_modell[df_modell[("Szektor", "")] == "Összesen"].copy()

    if df_osszesen.empty:
        raise ValueError("A kiválasztott modell eredményében nincs Összesen sor.")

    szektor_sorok = []

    for _, sor in df_szektor.iterrows():
        M_i_A = _M_ertek_szamitas(
            sor[("Allokáció", "Aktív delta")],
            sor[("Allokáció", "Aktív gamma")],
            sor[("Allokáció", "Aktív theta")],
            sor[("Allokáció", "Aktív vega")],
            sor[("Allokáció", "Aktív rho")],
            sor[("Allokáció", "Aktív residual")]
        )

        M_i_S = _M_ertek_szamitas(
            sor[("Szelekció", "Aktív delta")],
            sor[("Szelekció", "Aktív gamma")],
            sor[("Szelekció", "Aktív theta")],
            sor[("Szelekció", "Aktív vega")],
            sor[("Szelekció", "Aktív rho")],
            sor[("Szelekció", "Aktív residual")]
        )

        M_i = max(M_i_A, M_i_S)

        szektor_sorok.append({
            "Szektor": sor[("Szektor", "")],
            "M_pm,i^A": M_i_A,
            "M_pm,i^S": M_i_S,
            "M_pm,i": M_i,
        })

    szektor_metrikak_df = pd.DataFrame(szektor_sorok)

    pi_A = float(np.mean(szektor_metrikak_df["M_pm,i^A"] > kuszob))
    pi_S = float(np.mean(szektor_metrikak_df["M_pm,i^S"] > kuszob))
    pi = float(np.mean(szektor_metrikak_df["M_pm,i"] > kuszob))

    sor_pm = df_osszesen.iloc[0]

    M_p_A = _M_ertek_szamitas(
        sor_pm[("Allokáció", "Aktív delta")],
        sor_pm[("Allokáció", "Aktív gamma")],
        sor_pm[("Allokáció", "Aktív theta")],
        sor_pm[("Allokáció", "Aktív vega")],
        sor_pm[("Allokáció", "Aktív rho")],
        sor_pm[("Allokáció", "Aktív residual")]
    )

    M_p_S = _M_ertek_szamitas(
        sor_pm[("Szelekció", "Aktív delta")],
        sor_pm[("Szelekció", "Aktív gamma")],
        sor_pm[("Szelekció", "Aktív theta")],
        sor_pm[("Szelekció", "Aktív vega")],
        sor_pm[("Szelekció", "Aktív rho")],
        sor_pm[("Szelekció", "Aktív residual")]
    )

    M_p = max(M_p_A, M_p_S)
    vegso_kategoria, H = hasznossagi_kategoria(M_p, pi, alfa)
    vegso_kategoria_pont = kategoriapont(vegso_kategoria)

    portfolio_metrikak_df = pd.DataFrame({
        "Mutató": [
            "M_pm,p^A",
            "M_pm,p^S",
            "pi^A",
            "pi^S",
            "M_pm,p",
            "pi",
            "H",
            "Végső kategória",
            "Végső kategória pont",
        ],
        "Érték": [
            M_p_A,
            M_p_S,
            pi_A,
            pi_S,
            M_p,
            pi,
            H,
            vegso_kategoria,
            vegso_kategoria_pont,
        ]
    })

    return szektor_metrikak_df, portfolio_metrikak_df


def pm_osszefoglalo_rangsor(
    eredmenyek: list[list[pd.DataFrame]],
    modell_index: int = 3,
    pont_kuszob: float = 0.005,
    hasznossagi_kuszob: float = 0.3,
    alfa: float = 0.7
) -> pd.DataFrame:
    pontozas_df = pm_pontozas(
        eredmenyek=eredmenyek,
        modell_index=modell_index,
        kuszob=pont_kuszob
    )

    sorok = []

    for _, sor in pontozas_df.iterrows():
        pm_sorszam = int(sor["PM"])

        _, portfolio_metrikak_df = pm_metrikak_es_kategoriak(
            eredmenyek=eredmenyek,
            pm_sorszam=pm_sorszam,
            modell_index=modell_index,
            kuszob=hasznossagi_kuszob,
            alfa=alfa
        )

        metrikak = dict(zip(
            portfolio_metrikak_df["Mutató"],
            portfolio_metrikak_df["Érték"]
        ))

        sorok.append({
            "PM": pm_sorszam,
            "Aktív hozam": float(sor["Aktív hozam"]),
            "Pontszám": int(sor["Pontszám"]),
            "M_pm,p^A": float(metrikak["M_pm,p^A"]),
            "M_pm,p^S": float(metrikak["M_pm,p^S"]),
            "pi^A": float(metrikak["pi^A"]),
            "pi^S": float(metrikak["pi^S"]),
            "M_pm,p": float(metrikak["M_pm,p"]),
            "pi": float(metrikak["pi"]),
            "H": float(metrikak["H"]),
            "Végső kategória": str(metrikak["Végső kategória"]),
            "Végső kategória pont": int(metrikak["Végső kategória pont"]),
        })

    df = pd.DataFrame(sorok)

    df = df.sort_values(
        by=["Pontszám", "H", "Aktív hozam", "PM"],
        ascending=[False, False, False, True]
    ).reset_index(drop=True)

    return df


def nyertes_pm_kivalasztasa(
    eredmenyek: list[list[pd.DataFrame]],
    modell_index: int = 3,
    pont_kuszob: float = 0.005,
    hasznossagi_kuszob: float = 0.3,
    alfa: float = 0.7
) -> tuple[int, pd.DataFrame]:
    osszefoglalo_df = pm_osszefoglalo_rangsor(
        eredmenyek=eredmenyek,
        modell_index=modell_index,
        pont_kuszob=pont_kuszob,
        hasznossagi_kuszob=hasznossagi_kuszob,
        alfa=alfa
    )

    nyertes_pm = int(osszefoglalo_df.iloc[0]["PM"])

    return nyertes_pm, osszefoglalo_df


def nyertes_pm_excel(
    eredmenyek: list[list[pd.DataFrame]],
    aktiv_portfoliok: list[pd.DataFrame],
    fajl_utvonal: str,
    fajlnev: str,
    modell_index: int = 3,
    pont_kuszob: float = 0.005,
    hasznossagi_kuszob: float = 0.3,
    alfa: float = 0.7
) -> tuple[int, pd.DataFrame]:
    teljes_fajl_utvonal = os.path.join(fajl_utvonal, fajlnev)

    nyertes_pm, osszefoglalo_df = nyertes_pm_kivalasztasa(
        eredmenyek=eredmenyek,
        modell_index=modell_index,
        pont_kuszob=pont_kuszob,
        hasznossagi_kuszob=hasznossagi_kuszob,
        alfa=alfa
    )

    aktiv_portfolio_df = aktiv_portfoliok[nyertes_pm - 1].copy()

    bf_1985_df = eredmenyek[nyertes_pm - 1][0].copy()
    bhb_1986_df = eredmenyek[nyertes_pm - 1][1].copy()
    pozitiv_df = eredmenyek[nyertes_pm - 1][2].copy()
    valtozo_df = eredmenyek[nyertes_pm - 1][3].copy()

    szektor_metrikak_df, portfolio_metrikak_df = pm_metrikak_es_kategoriak(
        eredmenyek=eredmenyek,
        pm_sorszam=nyertes_pm,
        modell_index=modell_index,
        kuszob=hasznossagi_kuszob,
        alfa=alfa
    )

    nyertes_info_df = osszefoglalo_df[
        osszefoglalo_df["PM"] == nyertes_pm
    ].copy()

    bf_1985_df = multiindex_oszlopok_lapitasa(bf_1985_df)
    bhb_1986_df = multiindex_oszlopok_lapitasa(bhb_1986_df)
    pozitiv_df = multiindex_oszlopok_lapitasa(pozitiv_df)
    valtozo_df = multiindex_oszlopok_lapitasa(valtozo_df)

    with pd.ExcelWriter(teljes_fajl_utvonal, engine="openpyxl") as writer:
        aktiv_portfolio_df.to_excel(
            writer,
            sheet_name="Aktiv_portfolio",
            index=False
        )
        bf_1985_df.to_excel(writer, sheet_name="BF_1985", index=False)
        bhb_1986_df.to_excel(writer, sheet_name="BHB_1986", index=False)
        valtozo_df.to_excel(writer, sheet_name="Valtozo_tobblet", index=False)
        pozitiv_df.to_excel(writer, sheet_name="Pozitiv_tobblet", index=False)

        nyertes_info_df.to_excel(
            writer,
            sheet_name="Metrikak",
            index=False,
            startrow=0
        )

        szektor_metrikak_df.to_excel(
            writer,
            sheet_name="Metrikak",
            index=False,
            startrow=len(nyertes_info_df) + 3
        )

        portfolio_metrikak_df.to_excel(
            writer,
            sheet_name="Metrikak",
            index=False,
            startrow=len(nyertes_info_df) + len(szektor_metrikak_df) + 6
        )

    return nyertes_pm, osszefoglalo_df


def szektorsuly_es_aktiv_opciosuly_tablazat_input(
    benchmark_df: pd.DataFrame,
    aktiv_portfolio_df: pd.DataFrame
) -> pd.DataFrame:
    benchmark = benchmark_df.copy()
    portfolio = aktiv_portfolio_df.copy()

    benchmark_szektor = benchmark[benchmark["nev"].str.startswith("Szektor")][["nev", "suly"]].copy()
    portfolio_szektor = portfolio[portfolio["nev"].str.startswith("Szektor")][["nev", "suly"]].copy()

    benchmark_szektor["szektor_id"] = benchmark_szektor["nev"].str.extract(r"Szektor (\d+)")[0].astype(int)
    portfolio_szektor["szektor_id"] = portfolio_szektor["nev"].str.extract(r"Szektor (\d+)")[0].astype(int)

    benchmark_szektor = benchmark_szektor.rename(columns={"suly": "Benchmark"})
    portfolio_szektor = portfolio_szektor.rename(columns={"suly": "Portfólió"})

    szektor_df = pd.merge(
        portfolio_szektor[["szektor_id", "Portfólió"]],
        benchmark_szektor[["szektor_id", "Benchmark"]],
        on="szektor_id",
        how="inner"
    )

    benchmark_opcio = benchmark[benchmark["nev"].str.startswith("Opció")][["nev", "suly"]].copy()
    portfolio_opcio = portfolio[portfolio["nev"].str.startswith("Opció")][["nev", "suly"]].copy()

    benchmark_opcio["szektor_id"] = benchmark_opcio["nev"].str.extract(r"Opció (\d+),")[0].astype(int)
    portfolio_opcio["szektor_id"] = portfolio_opcio["nev"].str.extract(r"Opció (\d+),")[0].astype(int)

    benchmark_opcio = benchmark_opcio.rename(columns={"suly": "benchmark_opcio_suly"})
    portfolio_opcio = portfolio_opcio.rename(columns={"suly": "portfolio_opcio_suly"})

    opcio_df = pd.merge(
        portfolio_opcio[["nev", "szektor_id", "portfolio_opcio_suly"]],
        benchmark_opcio[["nev", "szektor_id", "benchmark_opcio_suly"]],
        on=["nev", "szektor_id"],
        how="inner"
    )

    opcio_df["aktiv_opcio_suly"] = (
        opcio_df["portfolio_opcio_suly"] - opcio_df["benchmark_opcio_suly"]
    ).abs()

    aktiv_opcio_atlag = (
        opcio_df
        .groupby("szektor_id")["aktiv_opcio_suly"]
        .mean()
        .reset_index()
        .rename(columns={"aktiv_opcio_suly": "Szektoron belüli átlagos aktív opciósúly"})
    )

    vegso_df = pd.merge(
        szektor_df,
        aktiv_opcio_atlag,
        on="szektor_id",
        how="inner"
    )

    vegso_df["Aktív"] = vegso_df["Portfólió"] - vegso_df["Benchmark"]
    vegso_df["Szektor"] = vegso_df["szektor_id"].apply(lambda x: f"Szektor {x}")

    vegso_df = vegso_df[
        [
            "Szektor",
            "Portfólió",
            "Benchmark",
            "Aktív",
            "Szektoron belüli átlagos aktív opciósúly"
        ]
    ]

    return vegso_df


def word_tablak_input(eredmenyek, pm_sorszam: int) -> dict:
    pm_eredmeny = eredmenyek[pm_sorszam - 1]

    return {
        "Brinson et al. (1986)": pm_eredmeny[1].copy(),
        "Brinson és Fachler (1985)": pm_eredmeny[0].copy(),
        "Pozitív többlet - allokáció": aktiv_gorog_word_input(pm_eredmeny[2], "Allokáció"),
        "Pozitív többlet - szelekció": aktiv_gorog_word_input(pm_eredmeny[2], "Szelekció"),
        "Változó többlet - allokáció": aktiv_gorog_word_input(pm_eredmeny[3], "Allokáció"),
        "Változó többlet - szelekció": aktiv_gorog_word_input(pm_eredmeny[3], "Szelekció"),
    }


def aktiv_gorog_word_input(df_modell: pd.DataFrame, blokk: str) -> pd.DataFrame:
    df = df_modell.copy()

    oszlopok = [
        ("Szektor", ""),
        ("Súly", "Portfólió"),
        ("Súly", "Benchmark"),
        (blokk, "Aktív delta"),
        (blokk, "Aktív gamma"),
        (blokk, "Aktív theta"),
        (blokk, "Aktív vega"),
        (blokk, "Aktív rho"),
        (blokk, "Aktív residual"),
    ]

    df = df[oszlopok].copy()

    uj_oszlopok = [
        ("Szektor", ""),
        ("Súly", "Portfólió"),
        ("Súly", "Benchmark"),
        (blokk, "A_d"),
        (blokk, "A_g"),
        (blokk, "A_t"),
        (blokk, "A_v"),
        (blokk, "A_r"),
        (blokk, "A_e"),
    ]

    df.columns = pd.MultiIndex.from_tuples(uj_oszlopok)

    return df


def komponens_extrem_peldak_input(
    eredmenyek: list[list[pd.DataFrame]],
    modell_index: int = 3,
    blokk: str = "Allokáció"
) -> pd.DataFrame:
    komponensek = [
        ("Aktív delta", "Aktív delta"),
        ("Aktív gamma", "Aktív gamma"),
        ("Aktív theta", "Aktív theta"),
        ("Aktív vega", "Aktív vega"),
        ("Aktív rho", "Aktív rho"),
    ]

    sorok = []

    for komponens_nev, komponens_oszlop in komponensek:
        legjobb = None

        for pm_sorszam, pm_eredmeny in enumerate(eredmenyek, start=1):
            df_modell = pm_eredmeny[modell_index].copy()
            df_szektor = df_modell[df_modell[("Szektor", "")] != "Összesen"].copy()

            for _, sor in df_szektor.iterrows():
                ertek = float(sor[(blokk, komponens_oszlop)])

                if legjobb is None or abs(ertek) > abs(legjobb["ertek"]):
                    legjobb = {
                        "PM": pm_sorszam,
                        "Szektor": sor[("Szektor", "")],
                        "Portfóliósúly": float(sor[("Súly", "Portfólió")]),
                        "Benchmarksúly": float(sor[("Súly", "Benchmark")]),
                        "Aktív delta": float(sor[(blokk, "Aktív delta")]),
                        "Aktív gamma": float(sor[(blokk, "Aktív gamma")]),
                        "Aktív theta": float(sor[(blokk, "Aktív theta")]),
                        "Aktív vega": float(sor[(blokk, "Aktív vega")]),
                        "Aktív rho": float(sor[(blokk, "Aktív rho")]),
                        "ertek": ertek,
                    }

        sorok.append({
            "Komponens": komponens_nev,
            "PM": legjobb["PM"],
            "Szektor": legjobb["Szektor"],
            "Portfóliósúly": legjobb["Portfóliósúly"],
            "Benchmarksúly": legjobb["Benchmarksúly"],
            "Aktív delta": legjobb["Aktív delta"],
            "Aktív gamma": legjobb["Aktív gamma"],
            "Aktív theta": legjobb["Aktív theta"],
            "Aktív vega": legjobb["Aktív vega"],
            "Aktív rho": legjobb["Aktív rho"],
        })

    return pd.DataFrame(sorok)


def komponens_extrem_peldak_brinson_hatassal_input(
    eredmenyek: list[list[pd.DataFrame]],
    sajat_modell_index: int,
    sajat_blokk: str,
    klasszikus_modell_index: int,
    klasszikus_hatas: str
) -> pd.DataFrame:

    komponensek = [
        "Aktív delta",
        "Aktív gamma",
        "Aktív theta",
        "Aktív vega",
        "Aktív rho",
    ]

    sorok = []

    for komponens in komponensek:
        legjobb = None

        for pm_sorszam, pm_eredmeny in enumerate(eredmenyek, start=1):
            df_sajat = pm_eredmeny[sajat_modell_index].copy()
            df_klasszikus = pm_eredmeny[klasszikus_modell_index].copy()

            df_sajat = df_sajat[df_sajat[("Szektor", "")] != "Összesen"].copy()
            df_klasszikus = df_klasszikus[df_klasszikus[("Szektor", "")] != "Összesen"].copy()

            for _, sor in df_sajat.iterrows():
                szektor = sor[("Szektor", "")]
                ertek = float(sor[(sajat_blokk, komponens)])

                klasszikus_sor = df_klasszikus[
                    df_klasszikus[("Szektor", "")] == szektor
                ]

                if klasszikus_sor.empty:
                    raise ValueError(
                        f"Nem található klasszikus modell sor: PM {pm_sorszam}, {szektor}"
                    )

                klasszikus_ertek = float(
                    klasszikus_sor.iloc[0][("Hatás", klasszikus_hatas)]
                )

                if legjobb is None or abs(ertek) > abs(legjobb["ertek"]):
                    legjobb = {
                        "PM": pm_sorszam,
                        "Szektor": szektor,
                        "Portfóliósúly": float(sor[("Súly", "Portfólió")]),
                        "Benchmarksúly": float(sor[("Súly", "Benchmark")]),
                        "Aktív delta": float(sor[(sajat_blokk, "Aktív delta")]),
                        "Aktív gamma": float(sor[(sajat_blokk, "Aktív gamma")]),
                        "Aktív theta": float(sor[(sajat_blokk, "Aktív theta")]),
                        "Aktív vega": float(sor[(sajat_blokk, "Aktív vega")]),
                        "Aktív rho": float(sor[(sajat_blokk, "Aktív rho")]),
                        klasszikus_hatas: klasszikus_ertek,
                        "ertek": ertek,
                    }

        sorok.append({
            "PM": legjobb["PM"],
            "Szektor": legjobb["Szektor"],
            "Portfóliósúly": legjobb["Portfóliósúly"],
            "Benchmarksúly": legjobb["Benchmarksúly"],
            "Aktív delta": legjobb["Aktív delta"],
            "Aktív gamma": legjobb["Aktív gamma"],
            "Aktív theta": legjobb["Aktív theta"],
            "Aktív vega": legjobb["Aktív vega"],
            "Aktív rho": legjobb["Aktív rho"],
            klasszikus_hatas: legjobb[klasszikus_hatas],
        })

    return pd.DataFrame(sorok)


def pozitiv_allokacio_extrem_peldak_input(
    eredmenyek: list[list[pd.DataFrame]]
) -> pd.DataFrame:
    return komponens_extrem_peldak_brinson_hatassal_input(
        eredmenyek=eredmenyek,
        sajat_modell_index=2,
        sajat_blokk="Allokáció",
        klasszikus_modell_index=1,
        klasszikus_hatas="Allokáció"
    ).rename(columns={
        "Allokáció": "Brinson et al. (1986) allokáció"
    })


def pozitiv_szelekcio_extrem_peldak_input(
    eredmenyek: list[list[pd.DataFrame]]
) -> pd.DataFrame:
    return komponens_extrem_peldak_brinson_hatassal_input(
        eredmenyek=eredmenyek,
        sajat_modell_index=2,
        sajat_blokk="Szelekció",
        klasszikus_modell_index=1,
        klasszikus_hatas="Szelekció"
    ).rename(columns={
        "Szelekció": "Brinson et al. (1986) szelekció"
    })


def valtozo_allokacio_extrem_peldak_input(
    eredmenyek: list[list[pd.DataFrame]]
) -> pd.DataFrame:
    return komponens_extrem_peldak_brinson_hatassal_input(
        eredmenyek=eredmenyek,
        sajat_modell_index=3,
        sajat_blokk="Allokáció",
        klasszikus_modell_index=0,
        klasszikus_hatas="Allokáció"
    ).rename(columns={
        "Allokáció": "Brinson–Fachler (1985) allokáció"
    })


def rho_adatok():

    df = pd.DataFrame([
        ["Szektor 1", 0.4000, 0.5000, 0.3086, -0.4207, -0.0002, 0.3189, -0.0103, -0.0044, -0.4554, 0.0392, -0.0028, 0.3647, -0.0729, 0.0421, 0.0021, 0.3872, -0.0248, -0.0003, -0.0039, 0.0013, 0.0004, 0.0455, -0.0039],
        ["Call", 1.5000, -0.5000, 0.1263, -0.1263, -0.0012, 0.1253, 0.0021, 0.0012, -0.1253, -0.0021, None, None, None, None, None, None, None, None, None, None, None, None, None],
        ["Put", -0.5000, 1.5000, 0.2384, -0.2384, 0.0033, 0.2618, -0.0268, -0.0033, -0.2618, 0.0268, None, None, None, None, None, None, None, None, None, None, None, None, None],
        ["Szektor 2", 0.6000, 0.5000, 0.2785, -0.4760, 0.0023, 0.2982, -0.0219, -0.0094, -0.5327, 0.0649, -0.0028, 0.3773, 0.0755, -0.0476, 0.0059, 0.4155, -0.0434, -0.0003, -0.0039, 0.0013, -0.0009, -0.0533, 0.0065],
        ["Call", 1.5000, -0.5000, 0.0899, -0.0899, -0.0005, 0.0906, -0.0001, 0.0005, -0.0906, 0.0001, None, None, None, None, None, None, None, None, None, None, None, None, None],
        ["Put", -0.5000, 1.5000, 0.2873, -0.2873, 0.0061, 0.3246, -0.0434, -0.0061, -0.3246, 0.0434, None, None, None, None, None, None, None, None, None, None, None, None, None],
        ["Összesen", 1.0000, 1.0000, 0.2906, -0.4484, 0.0013, 0.3065, -0.0173, -0.0069, -0.4941, 0.0521, -0.0056, 0.7420, 0.0025, -0.0055, 0.0080, 0.8028, -0.0682, -0.0006, -0.0078, 0.0026, -0.0005, -0.0078, 0.0026]
    ],
    columns=[
        "Név",
        "Portfólió súly", "Benchmark súly",
        "Portfólió hozam", "Benchmark hozam",
        "θ (portf.)", "ρ (portf.)", "ε (portf.)",
        "θ (bench)", "ρ (bench)", "ε (bench)",
        "BF 1985 allokáció", "Szelekció", "Interakció",
        "BHB 1986 allokáció",
        "Szel. θ", "Szel. ρ", "Szel. ε",
        "Vált. allok. θ", "Vált. allok. ρ", "Vált. allok. ε",
        "Poz. allok. θ", "Poz. allok. ρ", "Poz. allok. ε"
    ])
    df["Új opció ár"] = [
    None,      
    16.6759,   
    2.3035,    
    None,      
    24.5699,   
    0.6833,    
    None       
    ]

    return df

