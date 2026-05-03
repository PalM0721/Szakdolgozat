"""
Ez a fájl a benchmark portfólió időszak végi piaci állapotváltozóinak
szimulációjához szükséges paramétereket és segédfüggvényeket tartalmazza.
A modul részvényár-, volatilitás-, futamidő- és kamatlábváltozásokat
generál szektor- és opciónkénti sokkok alapján.

benchmark_piaci_allapotvaltozokkal:
    A benchmark portfólió opciósoraihoz szimulálja az időszak végi piaci
    állapotváltozókat. Az eredményeket új t1 oszlopokként adja vissza a
    bemeneti DataFrame-ben.
"""

import numpy as np
import pandas as pd

# ============================================================
# piaci állapotváltozók szimuláció paraméterei
# ============================================================
#eltelt idő
dt = 1 / 52

# drift
mu_min = -0.05
mu_max = 0.10
sigma_mu = 0.03

# részvényár faktor
rho_s = 0.4

# vol faktor
rho_sigma = 0.3

# leverage effect
rho_sv = -0.2

# vol dinamika
eta = 0.25

# vasicek kamatmodell
kappa_r = 1.5
theta_r = 0.04
sigma_r = 0.01


def szektor_driftek(szektorok_szama: int, mu_min: float, mu_max: float) -> np.ndarray:
    return np.random.uniform(mu_min, mu_max, size=szektorok_szama)


def reszvenyar_szektorfaktorok(szektorok_szama: int) -> np.ndarray:
    return np.random.normal(0, 1, size=szektorok_szama)


def volatilitas_szektorfaktorok(szektorok_szama: int) -> np.ndarray:
    return np.random.normal(0, 1, size=szektorok_szama)


def egyedi_drift(szektor_mu: float, n: int, sigma_mu: float) -> np.ndarray:
    return np.random.normal(szektor_mu, sigma_mu, size=n)


def reszvenyar_sokk(f_szektor: float, n: int, rho_s: float) -> np.ndarray:
    
    epsilon = np.random.normal(0, 1, size=n)
    
    return np.sqrt(rho_s) * f_szektor + np.sqrt(1 - rho_s) * epsilon


def volatilitas_sokk(f_szektor: float, n: int, rho_sigma: float) -> np.ndarray:
    
    epsilon = np.random.normal(0, 1, size=n)
    
    return np.sqrt(rho_sigma) * f_szektor + np.sqrt(1 - rho_sigma) * epsilon


def korrelalt_volatilitas_sokk(z_reszvenyar: np.ndarray, z_vol: np.ndarray, rho_sv: float) -> np.ndarray:
    
    return rho_sv * z_reszvenyar + np.sqrt(1 - rho_sv**2) * z_vol


def reszvenyar_t1(s0: np.ndarray, mu: np.ndarray, sigma0: np.ndarray, dt: float, z: np.ndarray) -> np.ndarray:
    
    return s0 * np.exp((mu - 0.5 * sigma0**2) * dt + sigma0 * np.sqrt(dt) * z)


def volatilitas_t1(sigma0: np.ndarray, eta: float, dt: float, u: np.ndarray) -> np.ndarray:
    
    return sigma0 * np.exp(eta * np.sqrt(dt) * u - 0.5 * eta**2 * dt)


def hatralevo_ido_t1(tau0: np.ndarray, dt: float) -> np.ndarray:
    
    return np.maximum(tau0 - dt, 1e-8)


def kockazatmentes_kamat_t1(r0: float, kappa_r: float, theta_r: float, sigma_r: float, dt: float) -> float:
    
    epsilon_r = np.random.normal(0, 1)
    
    return r0 + kappa_r * (theta_r - r0) * dt + sigma_r * np.sqrt(dt) * epsilon_r


def benchmark_piaci_allapotvaltozokkal(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    opcio_maszk = df["nev"].str.startswith("Opció")

    df["mu_szektor"] = np.nan
    df["mu"] = np.nan
    df["z_reszvenyar_szektor"] = np.nan
    df["z_reszvenyar"] = np.nan
    df["z_vol_szektor"] = np.nan
    df["u_vol"] = np.nan
    df["korrelalt_z_vol"] = np.nan
    df["reszvenyarfolyam_t1"] = np.nan
    df["volatilitas_t1"] = np.nan
    df["hatralevo_ido_t1"] = np.nan
    df["kockazatmentes_kamat_t1"] = np.nan

    df_opciok = df.loc[opcio_maszk].copy()

    szektor_nevek = df_opciok["nev"].str.extract(r"Opció (\d+),")[0].astype(int)
    df_opciok["szektor_id"] = szektor_nevek.values

    egyedi_szektorok = sorted(df_opciok["szektor_id"].unique())
    szektorok_szama = len(egyedi_szektorok)

    mu_szektorok = szektor_driftek(szektorok_szama, mu_min, mu_max)
    reszvenyar_faktorok = reszvenyar_szektorfaktorok(szektorok_szama)
    vol_faktorok = volatilitas_szektorfaktorok(szektorok_szama)

    rf_0 = df.loc[opcio_maszk, "kockazatmentes_kamat"].iloc[0]

    r1 = kockazatmentes_kamat_t1(
        r0=rf_0,
        kappa_r=kappa_r,
        theta_r=theta_r,
        sigma_r=sigma_r,
        dt=dt
    )

    for i, szektor in enumerate(egyedi_szektorok):

        szektor_indexek = df_opciok.index[df_opciok["szektor_id"] == szektor]
        n = len(szektor_indexek)

        s0 = df.loc[szektor_indexek, "reszvenyarfolyam"].astype(float).values
        sigma0 = df.loc[szektor_indexek, "volatilitas"].astype(float).values
        tau0 = df.loc[szektor_indexek, "hatralevo_ido"].astype(float).values

        mu_szektor = mu_szektorok[i]
        z_reszvenyar_szektor = reszvenyar_faktorok[i]
        z_vol_szektor = vol_faktorok[i]

        mu = egyedi_drift(mu_szektor, n, sigma_mu)

        z_reszvenyar = reszvenyar_sokk(z_reszvenyar_szektor, n, rho_s)
        u_vol = volatilitas_sokk(z_vol_szektor, n, rho_sigma)
        korrelalt_z_vol = korrelalt_volatilitas_sokk(z_reszvenyar, u_vol, rho_sv)

        s1 = reszvenyar_t1(s0, mu, sigma0, dt, z_reszvenyar)
        sigma1 = volatilitas_t1(sigma0, eta, dt, korrelalt_z_vol)
        tau1 = hatralevo_ido_t1(tau0, dt)

        df.loc[szektor_indexek, "mu_szektor"] = mu_szektor 
        df.loc[szektor_indexek, "mu"] = mu
        df.loc[szektor_indexek, "z_reszvenyar_szektor"] = z_reszvenyar_szektor
        df.loc[szektor_indexek, "z_reszvenyar"] = z_reszvenyar
        df.loc[szektor_indexek, "z_vol_szektor"] = z_vol_szektor
        df.loc[szektor_indexek, "u_vol"] = u_vol
        df.loc[szektor_indexek, "korrelalt_z_vol"] = korrelalt_z_vol
        df.loc[szektor_indexek, "reszvenyarfolyam_t1"] = s1
        df.loc[szektor_indexek, "volatilitas_t1"] = sigma1
        df.loc[szektor_indexek, "hatralevo_ido_t1"] = tau1
        df.loc[szektor_indexek, "kockazatmentes_kamat_t1"] = r1

    return df
