"""
Ez a fájl a teljes szimulációs és attribúciós folyamat fő futtatófájlja.
A modul létrehozza a benchmarkot, legenerálja az aktív portfóliókat,
kiszámítja a modellek eredményeit, majd elkészíti a rangsorokat és az
Excel-kimeneteket.
"""

import pandas as pd
from benchmark_setup import benchmark_kezdeti
from Black_Scholes import black_scholes_t0, black_scholes_t1
from piaci_allapotvaltozok import benchmark_piaci_allapotvaltozokkal
from hozamok import teljesitmeny_es_hozam_felbontas
from aktiv_portfoliok import aktivan_kezelt_portfoliok
from Brinson import pm, modell_eredmenyek, rangsor, felbontasok, osszefoglalo, nyertes_pm_excel


fajl_utvonal_osszefoglalo = r""
osszefoglalo_fajl_nev = "#név#.xlsx"
fajl_utvonal_nyertesek = r""
nyertes_fajl_nev = "#név#.xlsx"
port_men = pm


def benchmark() -> pd.DataFrame:
    df = benchmark_kezdeti()
    df = black_scholes_t0(df)
    df = benchmark_piaci_allapotvaltozokkal(df)
    df = black_scholes_t1(df)
    df = teljesitmeny_es_hozam_felbontas(df)

    return df


def aktivan_kezelt_portfolio(df: pd.DataFrame):
    return aktivan_kezelt_portfoliok(df, port_men)


def modellek(benchmark_df: pd.DataFrame, aktiv_portfoliok_df):
    return modell_eredmenyek(benchmark_df, aktiv_portfoliok_df)


def portfolio_menedzser_rangsor(modell_eredmenyek_lista):
    return rangsor(modell_eredmenyek_lista)



if __name__ == "__main__":
    #benchmark_df = benchmark()
    #aktiv_portfoliok = aktivan_kezelt_portfolio(benchmark_df)
    #negy_modell_eredmenyei = modellek(benchmark_df, aktiv_portfoliok)
    #port_men_rangsor = portfolio_menedzser_rangsor(negy_modell_eredmenyei)

    """
    legjobb_pm, legrosszabb_pm = osszefoglalo(
        benchmark_df=benchmark_df,
        negy_modell_eredmenyei=negy_modell_eredmenyei,
        aktiv_portfoliok=aktiv_portfoliok,
        port_men_rangsor=port_men_rangsor,
        fajl_utvonal=fajl_utvonal_osszefoglalo,
        fajlnev=osszefoglalo_fajl_nev
    )

    print("Az összefoglaló elkészült")
    """

    """
    nyertes_pm, pontozas_df = nyertes_pm_excel(
    eredmenyek=negy_modell_eredmenyei,
    aktiv_portfoliok=aktiv_portfoliok,
    fajl_utvonal=fajl_utvonal_nyertesek,
    fajlnev=nyertes_fajl_nev,
    modell_index=3,
    pont_kuszob=0.005,
    hasznossagi_kuszob=0.3
    )

    print(f"A kiválasztott portfóliómenedzser: PM {nyertes_pm}")
    """

    
    
