"""
Ez a fájl a szimulációs eredmények és attribúciós felbontások
grafikus megjelenítéséhez szükséges függvényeket tartalmazza.
A modul benchmark-, portfólió-, görög betűs, nem delta arány- és
szemléltető ábrákat készít matplotlib segítségével.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.ticker as ticker
from matplotlib.patches import Rectangle

from benchmark_setup import benchmark_kezdeti
from Black_Scholes import black_scholes_t0, black_scholes_t1
from piaci_allapotvaltozok import benchmark_piaci_allapotvaltozokkal
from hozamok import teljesitmeny_es_hozam_felbontas
from aktiv_portfoliok import aktivan_kezelt_portfoliok
from Brinson import (
    pm,
    modell_eredmenyek,
    rangsor,
    felbontasok,
    nem_delta_arany_szamitas,
    szektoros_felbontasok,
    szektoros_szelekcio_felbontasok,
    nem_delta_szelekcio_arany_szamitas,
    portfolio_nem_delta_aranyok_szamitas
)

def benchmark() -> pd.DataFrame:
    df = benchmark_kezdeti()
    df = black_scholes_t0(df)
    df = benchmark_piaci_allapotvaltozokkal(df)
    df = black_scholes_t1(df)
    df = teljesitmeny_es_hozam_felbontas(df)
    return df


def benchmark_szektorsuly_grafikon(df: pd.DataFrame):
    szektor_df = df[df["nev"].str.startswith("Szektor")].copy()

    plt.figure(figsize=(10, 5))
    plt.bar(szektor_df["nev"], szektor_df["suly"])
    plt.xticks(rotation=45)
    plt.ylabel("Súly")
    plt.xlabel("Szektor")
    plt.title("A benchmark portfólió szektorsúlyai")
    plt.tight_layout()
    plt.show()


def szektoron_beluli_suly_histogram(df: pd.DataFrame) -> None:
    opcio_df = df[df["nev"].str.startswith("Opció")].copy()
    sulyok = opcio_df["suly"]

    plt.figure(figsize=(9, 5))

    plt.hist(
        sulyok,
        bins=40,
        edgecolor="black"
    )
    plt.axvline(
        0,
        color="black",
        linewidth=3
    )
    plt.xlabel("Szektoron belüli súly")
    plt.ylabel("Gyakoriság")
    plt.title("Szektoron belüli opciósúlyok eloszlása")

    plt.tight_layout()
    plt.show()


def moneyness_kategoria(tipus: str, k: float, s0: float) -> str:
    m = k / s0

    # 1.5% sáv
    atm_low = 0.985
    atm_high = 1.015

    if tipus == "call":
        if atm_low <= m <= atm_high:
            return "ATM"
        elif m < atm_low:
            return "ITM"
        else:
            return "OTM"

    elif tipus == "put":
        if atm_low <= m <= atm_high:
            return "ATM"
        elif m > atm_high:
            return "ITM"
        else:
            return "OTM"

    else:
        raise ValueError("Ismeretlen típus")


def opcio_tipus_es_moneyness_grafikon(df: pd.DataFrame) -> None:
    opcio_df = df[df["nev"].str.startswith("Opció")].copy()

    opcio_df["fo_kategoria"] = (
        opcio_df["irany"].str.capitalize() + " " + opcio_df["tipus"]
    )

    opcio_df["moneyness_kategoria"] = opcio_df.apply(
        lambda row: moneyness_kategoria(
            row["tipus"],
            float(row["kotesi_arfolyam"]),
            float(row["reszvenyarfolyam"])
        ),
        axis=1
    )

    fo_kategoriak = ["Long call", "Short call", "Long put", "Short put"]
    moneyness_kategoriak = ["ITM", "ATM", "OTM"]

    tabla = (
        opcio_df
        .groupby(["fo_kategoria", "moneyness_kategoria"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=fo_kategoriak, columns=moneyness_kategoriak, fill_value=0)
    )

    x = np.arange(len(fo_kategoriak))
    szelesseg = 0.25

    plt.figure(figsize=(12, 6))

    for i, kat in enumerate(moneyness_kategoriak):
        plt.bar(
            x + (i - 1) * szelesseg,
            tabla[kat].values,
            width=szelesseg,
            label=kat,
            edgecolor="black"
        )

    plt.xticks(x, fo_kategoriak)
    plt.xlabel("Opció típusa")
    plt.ylabel("Opciók száma")
    plt.title("Opciók megoszlása típus és moneyness szerint")

    plt.legend()
    plt.tight_layout()
    plt.show()


def szektor_elmeleti_hozamok(df: pd.DataFrame) -> dict:
    opcio_df = df[df["nev"].str.startswith("Opció")].copy()

    opcio_df["szektor_id"] = (
        opcio_df["nev"].str.extract(r"Opció (\d+),")[0].astype(int)
    )

    dt = 1 / 52
    sigma = (0.15 + 0.30) / 2  # 0.225

    elmeleti = {}

    for szektor in sorted(opcio_df["szektor_id"].unique()):
        mu_i = opcio_df.loc[
            opcio_df["szektor_id"] == szektor, "mu_szektor"
        ].iloc[0]

        r = np.exp((mu_i - 0.5 * sigma**2) * dt) - 1
        elmeleti[szektor] = r

    return elmeleti

def szektoronkenti_reszvenyhozam_boxplot(df: pd.DataFrame) -> None:
    opcio_df = df[df["nev"].str.startswith("Opció")].copy()

    opcio_df["szektor_id"] = (
        opcio_df["nev"].str.extract(r"Opció (\d+),")[0].astype(int)
    )

    opcio_df["hozam"] = (
        opcio_df["reszvenyarfolyam_t1"] / opcio_df["reszvenyarfolyam"] - 1
    )

    szektorok = sorted(opcio_df["szektor_id"].unique())

    adatok = [
        opcio_df.loc[opcio_df["szektor_id"] == i, "hozam"].values
        for i in szektorok
    ]

    plt.figure(figsize=(11, 6))
    plt.boxplot(adatok, tick_labels=[f"Szektor {i}" for i in szektorok])

    # elméleti hozamok
    elmeleti = szektor_elmeleti_hozamok(df)

    x = np.arange(1, len(szektorok) + 1)
    y = [elmeleti[i] for i in szektorok]

    plt.scatter(x, y, marker="D")  

    plt.axhline(0, color="black", linewidth=2)

    plt.ylabel("Részvényhozam")
    plt.xlabel("Szektor")
    plt.title("Részvényhozamok eloszlása és elméleti szektorhozamok")

    plt.tight_layout()
    plt.show()


def volatilitas_valtozas_boxplot(df: pd.DataFrame) -> None:
    opcio_df = df[df["nev"].str.startswith("Opció")].copy()

    opcio_df["szektor_id"] = (
        opcio_df["nev"].str.extract(r"Opció (\d+),")[0].astype(int)
    )

    opcio_df["dSigma"] = (
        opcio_df["volatilitas_t1"] - opcio_df["volatilitas"]
    )

    szektorok = sorted(opcio_df["szektor_id"].unique())

    adatok = [
        opcio_df.loc[opcio_df["szektor_id"] == i, "dSigma"].values
        for i in szektorok
    ]

    plt.figure(figsize=(11, 6))
    plt.boxplot(adatok, tick_labels=[f"Szektor {i}" for i in szektorok])

    plt.axhline(0, color="black", linewidth=1, alpha=0.3)

    plt.xlabel("Szektor")
    plt.ylabel("Volatilitás változás (Δσ)")
    plt.title("Volatilitás változása szektoronként")

    plt.tight_layout()
    plt.show()


def szektor_es_benchmark_gorog_stacked(df: pd.DataFrame) -> None:
    szektor_df = df[
        df["nev"].str.startswith("Szektor") | (df["nev"] == "Benchmark")
    ].copy()

    szektorok = szektor_df[szektor_df["nev"].str.startswith("Szektor")].copy()
    szektorok["szektor_id"] = (
        szektorok["nev"].str.extract(r"Szektor (\d+)")[0].astype(int)
    )
    szektorok = szektorok.sort_values("szektor_id")

    benchmark = szektor_df[szektor_df["nev"] == "Benchmark"].copy()

    plot_df = pd.concat([szektorok, benchmark], ignore_index=True)

    komponensek = [
        "r_delta",
        "r_gamma",
        "r_theta",
        "r_vega",
        "r_rho",
        "r_epsilon"
    ]

    x = np.arange(len(plot_df))
    pozitiv_bottom = np.zeros(len(plot_df))
    negativ_bottom = np.zeros(len(plot_df))

    plt.figure(figsize=(13, 6))

    for k in komponensek:
        ertekek = plot_df[k].astype(float).values

        pozitiv = np.where(ertekek > 0, ertekek, 0)
        negativ = np.where(ertekek < 0, ertekek, 0)

        plt.bar(
            x,
            pozitiv,
            bottom=pozitiv_bottom,
            label=k,
            edgecolor="black"
        )

        plt.bar(
            x,
            negativ,
            bottom=negativ_bottom,
            edgecolor="black"
        )

        pozitiv_bottom += pozitiv
        negativ_bottom += negativ

    plt.axhline(0, color="black", linewidth=1, alpha=0.4)

    plt.xticks(x, plot_df["nev"], rotation=45)
    plt.ylabel("Hozam")
    plt.xlabel("Szektor")
    plt.title("Szektor- és benchmarkhozamok görög betűk szerinti felbontása")

    plt.legend()
    plt.tight_layout()
    plt.show()


def opcios_poziciohozam_histogram(df: pd.DataFrame, bins: int = 30) -> None:
    opcio_df = df[df["nev"].str.startswith("Opció")].copy()

    if "pozicio_hozam" not in opcio_df.columns:
        raise ValueError("Hiányzik a 'pozicio_hozam' oszlop.")

    hozamok = opcio_df["pozicio_hozam"].astype(float)

    plt.figure(figsize=(10, 5))

    plt.hist(
        hozamok,
        bins=bins,
        edgecolor="black"
    )

    plt.axvline(0, color="black", linewidth=2)

    plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.xlabel("Pozícióhozam")
    plt.ylabel("Gyakoriság")
    plt.title("Opciós pozíciók hozamának eloszlása")

    plt.tight_layout()
    plt.show()


def aktiv_szektor_suly_histogram(
    benchmark_df: pd.DataFrame,
    aktiv_portfoliok: list[pd.DataFrame],
    bins: int = 30
) -> None:
    benchmark_szektor = benchmark_df[
        benchmark_df["nev"].str.startswith("Szektor")
    ].copy()

    benchmark_szektor["szektor_id"] = (
        benchmark_szektor["nev"].str.extract(r"Szektor (\d+)")[0].astype(int)
    )

    benchmark_sulyok = dict(
        zip(benchmark_szektor["szektor_id"], benchmark_szektor["suly"])
    )

    aktiv_sulyok = []

    for df_pm in aktiv_portfoliok:
        pm_szektor = df_pm[df_pm["nev"].str.startswith("Szektor")].copy()

        pm_szektor["szektor_id"] = (
            pm_szektor["nev"].str.extract(r"Szektor (\d+)")[0].astype(int)
        )

        for _, row in pm_szektor.iterrows():
            szektor_id = int(row["szektor_id"])
            w_port = float(row["suly"])
            w_bench = float(benchmark_sulyok[szektor_id])
            aktiv_sulyok.append(w_port - w_bench)

    plt.figure(figsize=(10, 5))

    plt.hist(
        aktiv_sulyok,
        bins=bins,
        edgecolor="black"
    )

    plt.axvline(0, color="black", linewidth=2)

    plt.xlabel("Aktív szektorsúly")
    plt.ylabel("Gyakoriság")
    plt.title("Az összes portfóliómenedzser szektorainak aktív súlyeloszlása")

    plt.tight_layout()
    plt.show()


def aktiv_hozam_histogram(rangsor_df: pd.DataFrame, bins: int = 20) -> None:
    aktiv_hozamok = rangsor_df["Aktív hozam"].astype(float)

    plt.figure(figsize=(10, 5))

    plt.hist(
        aktiv_hozamok,
        bins=bins,
        edgecolor="black"
    )

    plt.axvline(0, color="black", linewidth=2)

    plt.xlabel("Aktív hozam")
    plt.ylabel("Gyakoriság")
    plt.title("A portfóliómenedzserek aktív hozamának eloszlása")

    plt.tight_layout()
    plt.show()


def gorog_kuszob_darabszam_oszlopdiagram(
    df: pd.DataFrame,
    kuszob: float = 0.005
) -> None:

    oszlopok = [
        "Allokáció - Aktív delta",
        "Allokáció - Aktív gamma",
        "Allokáció - Aktív theta",
        "Allokáció - Aktív vega",
        "Allokáció - Aktív rho",
        "Allokáció - Aktív residual",
        "Szelekció - Aktív delta",
        "Szelekció - Aktív gamma",
        "Szelekció - Aktív theta",
        "Szelekció - Aktív vega",
        "Szelekció - Aktív rho",
        "Szelekció - Aktív residual",
    ]

    darabszamok = []

    for oszlop in oszlopok:
        db = (df[oszlop].abs() > kuszob).sum()
        darabszamok.append(db)

    eredmeny_df = pd.DataFrame({
        "Komponens": oszlopok,
        "Darabszám": darabszamok
    })

    plt.figure(figsize=(14, 6))
    plt.bar(eredmeny_df["Komponens"], eredmeny_df["Darabszám"], edgecolor="black")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Darabszám")
    plt.xlabel("Komponens")
    plt.title(f"{kuszob} küszöbnél nagyobb abszolút értékű komponensek száma")
    plt.tight_layout()
    plt.show()


def nem_delta_arany_ket_modell_abra(df_pozitiv, df_valtozo, lepes=0.01):
    pozitiv_df = nem_delta_arany_szamitas(df_pozitiv, lepes)
    valtozo_df = nem_delta_arany_szamitas(df_valtozo, lepes)

    plt.figure(figsize=(10, 6))

    plt.step(
        pozitiv_df["Küszöb (%)"],
        pozitiv_df["Szektorok száma"],
        where="post",
        linewidth=2,
        label="Pozitív többlet felbontás"
    )

    plt.step(
        valtozo_df["Küszöb (%)"],
        valtozo_df["Szektorok száma"],
        where="post",
        linewidth=2,
        label="Változó többlet felbontás"
    )

    plt.xlim(0, 100)
    plt.ylim(0, 1200)

    yticks = list(np.arange(0, 1001, 200))
    if 1100 not in yticks:
        yticks.append(1100)
    plt.yticks(sorted(yticks))

    plt.xlabel("Küszöbérték (%)")
    plt.ylabel("Szektorok száma")
    plt.title("Nem-delta komponensek aránya az allokációs hatáson belül")
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.show()


def nem_delta_szelekcio_arany_abra(df, lepes=0.01):
    eredmeny_df = nem_delta_szelekcio_arany_szamitas(df, lepes)

    plt.figure(figsize=(10, 6))
    plt.step(
        eredmeny_df["Küszöb (%)"],
        eredmeny_df["Szektorok száma"],
        where="post",
        linewidth=2
    )

    plt.xlim(0, 100)
    plt.ylim(0, 1200)

    yticks = list(np.arange(0, 1001, 200))
    if 1100 not in yticks:
        yticks.append(1100)
    plt.yticks(sorted(yticks))

    plt.xlabel("Küszöbérték (%)")
    plt.ylabel("Szektorok száma")
    plt.title("Nem-delta komponensek aránya a szelekciós hatáson belül")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def portfolio_nem_delta_ket_gorbe_abra(df: pd.DataFrame, lepes: float = 1.0) -> None:
    eredmeny_df = portfolio_nem_delta_aranyok_szamitas(df, lepes)

    plt.figure(figsize=(10, 6))

    plt.step(
        eredmeny_df["Küszöb (%)"],
        eredmeny_df["Allokáció"],
        where="post",
        linewidth=2,
        label="Allokáció"
    )

    plt.step(
        eredmeny_df["Küszöb (%)"],
        eredmeny_df["Szelekció"],
        where="post",
        linewidth=2,
        label="Szelekció"
    )

    plt.xlim(0, 102)
    plt.ylim(0, 105)

    yticks = list(range(0, 101, 20))
    if 100 not in yticks:
        yticks.append(100)
    plt.yticks(sorted(yticks))

    plt.xlabel("Küszöbérték (%)")
    plt.ylabel("Portfóliómenedzserek száma")
    plt.title("Nem-delta komponensek aránya az aktív portfóliók hozamának felbontásában")
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.show()


def benchmark_rezidualis_mutatok(df: pd.DataFrame) -> dict:
    df = df.copy()

    opcio = df["nev"].str.startswith("Opció")

    eps = 1e-12

    abs_eps = df.loc[opcio, "hozzajarulas_epsilon"].abs().sum()

    abs_delta = df.loc[opcio, "hozzajarulas_delta"].abs().sum()
    abs_gamma = df.loc[opcio, "hozzajarulas_gamma"].abs().sum()
    abs_theta = df.loc[opcio, "hozzajarulas_theta"].abs().sum()
    abs_vega = df.loc[opcio, "hozzajarulas_vega"].abs().sum()
    abs_rho = df.loc[opcio, "hozzajarulas_rho"].abs().sum()

    abs_total = df.loc[opcio, "hozzajarulas"].abs().sum()

    teljes_felbontas = (
        abs_delta + abs_gamma + abs_theta +
        abs_vega + abs_rho + abs_eps
    )

    arany_felbontas = abs_eps / teljes_felbontas if teljes_felbontas > eps else np.nan
    arany_teljes = abs_eps / abs_total if abs_total > eps else np.nan

    return {
        "abs_rezidualis": abs_eps,
        "rezidualis_arany_felbontas": arany_felbontas,
        "rezidualis_arany_teljes": arany_teljes
    }


def pozitiv_tobblet_felbontas_abra():
    fig, ax = plt.subplots(figsize=(13, 6.5))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    x0 = 3.0
    x1 = 5.8
    x2 = 8.9

    y0 = 0.8
    h = 0.68

    bal_szovegek = [
        r"$B_{i,\Delta}$",
        r"$B_{i,\Delta}+B_{i,\Gamma}$",
        r"$B_{i,\Delta}+B_{i,\Gamma}+B_{i,\Theta}$",
        r"$B_{i,\Delta}+B_{i,\Gamma}+B_{i,\Theta}+B_{i,\nu}$",
        r"$B_{i,\Delta}+B_{i,\Gamma}+B_{i,\Theta}+B_{i,\nu}+B_{i,\rho}$",
        r"$B_i$",
    ]

    jobb_szovegek = [
        r"$Ad_i^A$",
        r"$Ag_i^A$",
        r"$At_i^A$",
        r"$Av_i^A$",
        r"$Ar_i^A$",
        r"$Ae_i^A$",
    ]

    szinek = [
        "#eeeeee",
        "#cfcfcf",
        "#f3ddcf",
        "#bfe8c6",
        "#e5bce5",
        "#fff200",
    ]

    for k in range(6):
        y = y0 + k * h

        ax.add_patch(Rectangle(
            (x0, y),
            x1 - x0,
            h,
            facecolor="#d9e8f6",
            edgecolor="black",
            linewidth=1.1
        ))

        ax.add_patch(Rectangle(
            (x1, y),
            x2 - x1,
            h,
            facecolor=szinek[k],
            edgecolor="black",
            linewidth=1.1
        ))

        ax.text(
            x0 - 0.25,
            y + h / 2,
            bal_szovegek[k],
            ha="right",
            va="center",
            fontsize=16,
            fontstyle="italic"
        )

        ax.text(
            (x1 + x2) / 2,
            y + h / 2,
            jobb_szovegek[k],
            ha="center",
            va="center",
            fontsize=18,
            fontstyle="italic"
        )

    top_y = y0 + 6 * h

    ax.add_patch(Rectangle(
        (x0, top_y),
        x1 - x0,
        h * 1.35,
        facecolor="#e5bce5",
        edgecolor="black",
        linewidth=1.1
    ))

    ax.add_patch(Rectangle(
        (x1, top_y),
        x2 - x1,
        h * 1.35,
        facecolor="#8dd373",
        edgecolor="black",
        linewidth=1.1
    ))

    ax.text(
        (x0 + x1) / 2,
        top_y + h * 0.675,
        r"$S_i$",
        ha="center",
        va="center",
        fontsize=26,
        fontstyle="italic"
    )

    ax.text(
        (x1 + x2) / 2,
        top_y + h * 0.675,
        r"$I_i$",
        ha="center",
        va="center",
        fontsize=26,
        fontstyle="italic"
    )

    ax.text(
        (x0 + x1) / 2,
        y0 + 3 * h,
        r"$W_i^{bench}B_i$",
        ha="center",
        va="center",
        fontsize=30,
        fontstyle="italic"
    )

    ax.text(
        (x1 + x2) / 2,
        top_y - 0.15,
        r"$A_i=\sum_k Ak_i^A$",
        ha="center",
        va="top",
        fontsize=18,
        fontstyle="italic"
    )

    ax.plot([x0, x0], [0.35, top_y + h * 1.35 + 0.85], color="black", linewidth=1.3)
    ax.plot([x1, x1], [0.35, top_y + h * 1.35 + 0.85], color="black", linewidth=1.3)
    ax.plot([x2, x2], [0.35, top_y + h * 1.35 + 0.85], color="black", linewidth=1.3)

    ax.plot([0.65, 9.65], [y0, y0], color="black", linewidth=1.3)
    ax.plot([0.65, 9.65], [top_y + h * 1.35, top_y + h * 1.35], color="black", linewidth=1.3)

    ax.text(
        x0 - 0.7,
        top_y + h * 1.35 + 0.25,
        r"$R_i$",
        ha="center",
        va="bottom",
        fontsize=18,
        fontstyle="italic"
    )

    ax.text(
        x1,
        0.45,
        r"$W_i^{bench}$",
        ha="center",
        va="top",
        fontsize=18,
        fontstyle="italic"
    )

    ax.text(
        x2,
        0.45,
        r"$W_i^{port}$",
        ha="center",
        va="top",
        fontsize=18,
        fontstyle="italic"
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    #df = benchmark()
    
    #benchmark_szektorsuly_grafikon(df)
    #szektoron_beluli_suly_histogram(df)
    #opcio_tipus_es_moneyness_grafikon(df)
    #szektoronkenti_reszvenyhozam_boxplot(df)
    #volatilitas_valtozas_boxplot(df)
    #szektor_es_benchmark_gorog_stacked(df)
    #opcios_poziciohozam_histogram(df)

    #aktiv_portfoliok = aktivan_kezelt_portfoliok(df, pm)
    #aktiv_szektor_suly_histogram(df, aktiv_portfoliok)

    #negy_modell_eredmenyei = modell_eredmenyek(df, aktiv_portfoliok)
    #port_men_rangsor = rangsor(negy_modell_eredmenyei)
    #rangsor_df = port_men_rangsor[1]
    #aktiv_hozam_histogram(rangsor_df)

    #df_felbontas = felbontasok(negy_modell_eredmenyei, modell_index=3)
    #gorog_kuszob_darabszam_oszlopdiagram(df_felbontas, kuszob=0.005)

    #df_szektorok = szektoros_felbontasok(negy_modell_eredmenyei, modell_index=3)
    #nem_delta_arany_abra(df_szektorok, lepes=0.05)

    #df_szelekcio_szektorok = szektoros_szelekcio_felbontasok(negy_modell_eredmenyei, modell_index=3)
    #nem_delta_szelekcio_arany_abra(df_szelekcio_szektorok, lepes=0.05)

    #portfolio_nem_delta_ket_gorbe_abra(df_felbontas, lepes=0.01)
    #print(benchmark_rezidualis_mutatok(df))
    #pozitiv_tobblet_felbontas_abra()

    #df_szektorok_pozitiv = szektoros_felbontasok(negy_modell_eredmenyei, modell_index=2)
    #df_szektorok_valtozo = szektoros_felbontasok(negy_modell_eredmenyei, modell_index=3)

    """
    nem_delta_arany_ket_modell_abra(
        df_szektorok_pozitiv,
        df_szektorok_valtozo,
        lepes=0.05
    )
    """
