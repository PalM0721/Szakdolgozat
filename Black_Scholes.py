"""
Ez a fájl a Black-Scholes-modellhez tartozó opcióárazási és görög
betűs érzékenységi függvényeket tartalmazza.
A modul call és put opciókra számít árat, deltát, gammát, vegát,
thetát és rhót a kezdeti, illetve időszak végi piaci állapot alapján.

black_scholes_t0:
    A benchmark vagy portfólió opciósoraihoz kiszámítja a kezdeti
    Black-Scholes-árakat és görög betűket. Az eredményeket új t0
    oszlopokként adja vissza a bemeneti DataFrame-ben.

black_scholes_t1:
    A benchmark vagy portfólió opciósoraihoz kiszámítja az időszak
    végi Black-Scholes-árakat és görög betűket. Az eredményeket új t1
    oszlopokként adja vissza a bemeneti DataFrame-ben.
"""

import pandas as pd
import numpy as np
from scipy.stats import norm


def d1(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    return (np.log(s / k) + (r + 0.5 * sigma**2) * tau) / (sigma * np.sqrt(tau))


def d2(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    return d1(s, k, sigma, r, tau) - sigma * np.sqrt(tau)


def black_scholes_call_ar(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    d_1 = d1(s, k, sigma, r, tau)
    d_2 = d2(s, k, sigma, r, tau)
    return s * norm.cdf(d_1) - k * np.exp(-r * tau) * norm.cdf(d_2)


def black_scholes_put_ar(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    d_1 = d1(s, k, sigma, r, tau)
    d_2 = d2(s, k, sigma, r, tau)
    return k * np.exp(-r * tau) * norm.cdf(-d_2) - s * norm.cdf(-d_1)


def delta_call(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    d_1 = d1(s, k, sigma, r, tau)
    return norm.cdf(d_1)


def delta_put(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    d_1 = d1(s, k, sigma, r, tau)
    return norm.cdf(d_1) - 1


def gamma(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    d_1 = d1(s, k, sigma, r, tau)
    return norm.pdf(d_1) / (s * sigma * np.sqrt(tau))


def vega(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    d_1 = d1(s, k, sigma, r, tau)
    return s * norm.pdf(d_1) * np.sqrt(tau)


def theta_call(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    d_1 = d1(s, k, sigma, r, tau)
    d_2 = d2(s, k, sigma, r, tau)
    elso_tag = -(s * norm.pdf(d_1) * sigma) / (2 * np.sqrt(tau))
    masodik_tag = -r * k * np.exp(-r * tau) * norm.cdf(d_2)
    return elso_tag + masodik_tag


def theta_put(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    d_1 = d1(s, k, sigma, r, tau)
    d_2 = d2(s, k, sigma, r, tau)
    elso_tag = -(s * norm.pdf(d_1) * sigma) / (2 * np.sqrt(tau))
    masodik_tag = r * k * np.exp(-r * tau) * norm.cdf(-d_2)
    return elso_tag + masodik_tag


def rho_call(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    d_2 = d2(s, k, sigma, r, tau)
    return k * tau * np.exp(-r * tau) * norm.cdf(d_2)


def rho_put(s: float, k: float, sigma: float, r: float, tau: float) -> float:
    d_2 = d2(s, k, sigma, r, tau)
    return -k * tau * np.exp(-r * tau) * norm.cdf(-d_2)


def black_scholes_ertekek(s: float, k: float, sigma: float, r: float, tau: float, tipus: str) -> dict:
    """
    tipus: 'call' vagy 'put'
    """
    if tipus == "call":
        return {
            "ar": black_scholes_call_ar(s, k, sigma, r, tau),
            "delta": delta_call(s, k, sigma, r, tau),
            "gamma": gamma(s, k, sigma, r, tau),
            "vega": vega(s, k, sigma, r, tau),
            "theta": theta_call(s, k, sigma, r, tau),
            "rho": rho_call(s, k, sigma, r, tau)
        }

    if tipus == "put":
        return {
            "ar": black_scholes_put_ar(s, k, sigma, r, tau),
            "delta": delta_put(s, k, sigma, r, tau),
            "gamma": gamma(s, k, sigma, r, tau),
            "vega": vega(s, k, sigma, r, tau),
            "theta": theta_put(s, k, sigma, r, tau),
            "rho": rho_put(s, k, sigma, r, tau)
        }
    

def black_scholes_t0(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    opcio_maszk = df["nev"].str.startswith("Opció")

    df["ar_t0"] = np.nan
    df["delta_t0"] = np.nan
    df["gamma_t0"] = np.nan
    df["vega_t0"] = np.nan
    df["theta_t0"] = np.nan
    df["rho_t0"] = np.nan

    for idx in df.index[opcio_maszk]:
        s = float(df.loc[idx, "reszvenyarfolyam"])
        k = float(df.loc[idx, "kotesi_arfolyam"])
        sigma = float(df.loc[idx, "volatilitas"])
        r = float(df.loc[idx, "kockazatmentes_kamat"])
        tau = float(df.loc[idx, "hatralevo_ido"])
        tipus = str(df.loc[idx, "tipus"])

        eredmeny = black_scholes_ertekek(s, k, sigma, r, tau, tipus)

        df.loc[idx, "ar_t0"] = eredmeny["ar"]
        df.loc[idx, "delta_t0"] = eredmeny["delta"]
        df.loc[idx, "gamma_t0"] = eredmeny["gamma"]
        df.loc[idx, "vega_t0"] = eredmeny["vega"]
        df.loc[idx, "theta_t0"] = eredmeny["theta"]
        df.loc[idx, "rho_t0"] = eredmeny["rho"]

    return df


def black_scholes_t1(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    opcio_maszk = df["nev"].str.startswith("Opció")

    df["ar_t1"] = np.nan
    df["delta_t1"] = np.nan
    df["gamma_t1"] = np.nan
    df["vega_t1"] = np.nan
    df["theta_t1"] = np.nan
    df["rho_t1"] = np.nan

    for idx in df.index[opcio_maszk]:
        s = float(df.loc[idx, "reszvenyarfolyam_t1"])
        k = float(df.loc[idx, "kotesi_arfolyam"])
        sigma = float(df.loc[idx, "volatilitas_t1"])
        r = float(df.loc[idx, "kockazatmentes_kamat_t1"])
        tau = float(df.loc[idx, "hatralevo_ido_t1"])
        tipus = str(df.loc[idx, "tipus"])

        eredmeny = black_scholes_ertekek(s, k, sigma, r, tau, tipus)

        df.loc[idx, "ar_t1"] = eredmeny["ar"]
        df.loc[idx, "delta_t1"] = eredmeny["delta"]
        df.loc[idx, "gamma_t1"] = eredmeny["gamma"]
        df.loc[idx, "vega_t1"] = eredmeny["vega"]
        df.loc[idx, "theta_t1"] = eredmeny["theta"]
        df.loc[idx, "rho_t1"] = eredmeny["rho"]

    return df