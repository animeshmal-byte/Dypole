#!/usr/bin/env python3
"""
predict_power.py

Fetches current weather for a lat/lon (via weather_api.weather.fetch_current),
runs it through the trained solar and wind power models, fills in the two
`None` output placeholders, and returns the modified dict.

Both models are autoregressive: they were trained on the *previous* power
reading as an input feature (power_lag_1/2/3 for solar, pow_out_lag for
wind), predicting the *next* one. A single live weather snapshot has no
such history on its own, so this script keeps a small JSON cache on disk
(keyed by lat/lon) of the last predictions and feeds those back in as the
lag inputs on the next run. On the very first run for a given location,
lags are bootstrapped to 0.0.

CHANGES FROM v1 (OOD safety):
    1. check_in_distribution() -- flags any raw input feature that falls
       outside the same sanity ranges the two training scripts used to
       DROP rows during cleaning. If training would have thrown a row
       away, inference has no business trusting a prediction on it
       either. Warnings are attached to the output under "_warnings"
       instead of silently trusting an extrapolated number.
    2. apply_solar_physics_floor() -- solar output is hard-clamped to 0.0
       whenever all three irradiance features are <= 0 (i.e. night).
       This is real physics, not something worth leaving to the network
       to infer purely statistically.
    3. apply_wind_cutout_ceiling() -- wind output is hard-clamped to 0.0
       once wind_speed reaches/exceeds a cut-out threshold, mirroring the
       cut-in check the training script already enforces on the low end.
       Without this, wind_speed_sq/cub features just keep extrapolating
       upward past the point real turbines shut down for safety.
    4. predict_with_uncertainty() -- optional MC-dropout uncertainty
       estimate (mean + std over several stochastic forward passes) so a
       caller can see when the model is unsure, e.g. on inputs near/at
       the edges of VALID_RANGES.

Place this file at backend/predict_power.py so the relative paths to
../models/*.pt and ./weather_api/weather.py resolve correctly.

Usage:
    python predict_power.py --lat 28.6 --lon 77.2
"""

import argparse
import json
import os
import sys

import numpy as np
import torch
import torch.nn as nn

# --------------------------------------------------------------------------
# Wire up to weather_api/weather.py (fetch_current + the shared column
# name constants), assuming this script lives alongside that folder.
# --------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather_api"))
from weather_api.weather import (  # noqa: E402
    fetch_current,
    TARGET_COL,       # "Power (MW)"        -- solar output key
    POW_TARGET_COL,   # "pow_out"           -- wind output key
)

_HERE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(_HERE, "..", "models")
SOLAR_CKPT_PATH = os.path.join(MODELS_DIR, "solar_power_model.pt")
WIND_CKPT_PATH = os.path.join(MODELS_DIR, "wind_power_model.pt")

CACHE_PATH = os.path.join(_HERE, ".pow_lag_cache.json")


# --------------------------------------------------------------------------
# Sanity ranges -- MUST stay in sync with VALID_RANGES in
# train_solar_power_model.py and train_wind_power_model.py. If training
# would have dropped a row for being outside these bounds, inference has
# no business trusting a prediction on it either.
# --------------------------------------------------------------------------
WEATHER_VALID_RANGES = {
    # wind-model raw feature names
    "wind_speed": (0, 60),
    "temp": (-60, 55),
    "prs": (800, 1100),
    "hum%": (0, 100),
    # solar-model raw feature names
    "Total solar irradiance (W/m2)": (0, 1500),
    "Direct normal irradiance (W/m2)": (0, 1500),
    "Global horizontal irradiance (W/m2)": (0, 1500),
    "Air temperature (°C)": (-40, 60),
    "Atmosphere (hpa)": (800, 1100),
    "Relative humidity (%)": (0, 100),
}

SOLAR_IRRADIANCE_COLS = [
    "Total solar irradiance (W/m2)",
    "Direct normal irradiance (W/m2)",
    "Global horizontal irradiance (W/m2)",
]

# Typical utility-scale turbine cut-out speed. Tune to your actual turbine
# spec if you have per-file capacity/model info available.
WIND_CUT_OUT_SPEED = 25.0


def check_in_distribution(raw, ranges=WEATHER_VALID_RANGES):
    """Return a list of human-readable warnings for any raw weather value
    that falls outside the ranges used to clean the training data. An
    empty list means the input looks like something the model actually
    trained on."""
    warnings = []
    for col, (lo, hi) in ranges.items():
        if col not in raw:
            continue
        v = raw[col]
        if v is None:
            continue
        if (lo is not None and v < lo) or (hi is not None and v > hi):
            warnings.append(f"{col}={v} is outside training range [{lo}, {hi}]")
    return warnings


def apply_solar_physics_floor(pred, raw):
    """Hard physics constraint: no sunlight in -> no power out, regardless
    of what the network extrapolated."""
    irradiance_vals = [raw.get(c) for c in SOLAR_IRRADIANCE_COLS]
    if all(v is not None and v <= 0 for v in irradiance_vals):
        return 0.0
    return pred


def apply_wind_cutout_ceiling(pred, raw, cutout=WIND_CUT_OUT_SPEED):
    """Hard physics constraint: turbines feather/shut down at high wind
    speed for safety, so power should collapse toward zero past cut-out --
    not keep climbing the way an unconstrained ws^2/ws^3 extrapolation
    would suggest."""
    ws = raw.get("wind_speed")
    if ws is not None and ws >= cutout:
        return 0.0
    return pred


# --------------------------------------------------------------------------
# Model architectures -- must match the two training scripts exactly so
# the saved state_dict keys line up.
# --------------------------------------------------------------------------
class SolarPowerMLP(nn.Module):
    """v1 architecture (train_solar_power_model.py): plain Linear/ReLU/Dropout,
    no BatchNorm."""

    def __init__(self, in_dim, hidden=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden, hidden // 2),
            nn.ReLU(),
            nn.Linear(hidden // 2, 1),
        )

    def forward(self, x):
        return self.net(x)


class WindPowerMLP(nn.Module):
    """v2 architecture (train_wind_power_model.py): BatchNorm after every
    Linear layer."""

    def __init__(self, in_dim, hidden=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.BatchNorm1d(hidden),
            nn.ReLU(),
            nn.Dropout(0.05),
            nn.Linear(hidden, hidden),
            nn.BatchNorm1d(hidden),
            nn.ReLU(),
            nn.Dropout(0.05),
            nn.Linear(hidden, hidden // 2),
            nn.BatchNorm1d(hidden // 2),
            nn.ReLU(),
            nn.Linear(hidden // 2, 1),
        )

    def forward(self, x):
        return self.net(x)


def _load_model(ckpt_path, model_cls, device):
    try:
        ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    except TypeError:
        # older torch versions don't have the weights_only kwarg
        ckpt = torch.load(ckpt_path, map_location=device)

    state_dict = ckpt["model_state_dict"]
    first_w = state_dict["net.0.weight"]  # shape: [hidden, in_dim]
    hidden, in_dim = first_w.shape
    model = model_cls(in_dim=in_dim, hidden=hidden).to(device)
    model.load_state_dict(state_dict)
    model.eval()
    return model, ckpt


def _predict(model, ckpt, feature_vec, device):
    """feature_vec: 1D sequence in the exact order of ckpt['feature_cols'].
    Scales with the checkpoint's saved x/y mean+std, runs the model, and
    returns the un-scaled scalar prediction."""
    x = np.asarray(feature_vec, dtype=np.float32).reshape(1, -1)
    x_mean, x_std = ckpt["x_mean"], ckpt["x_std"]
    y_mean, y_std = ckpt["y_mean"], ckpt["y_std"]

    x_scaled = ((x - x_mean) / x_std).astype(np.float32)
    with torch.no_grad():
        # BatchNorm layers are safe on a batch of 1 in eval mode -- they
        # use running stats, not batch stats.
        pred_scaled = model(torch.from_numpy(x_scaled).to(device))
    pred_scaled = pred_scaled.cpu().numpy()
    pred = pred_scaled * y_std + y_mean
    return float(pred.reshape(-1)[0])


def _predict_with_uncertainty(model, ckpt, feature_vec, device, n_samples=30):
    """Same as _predict, but runs n_samples stochastic forward passes with
    dropout left active (model.train()) to get a cheap mean/std estimate.
    A wide std on a given input is itself a signal the model is unsure --
    useful alongside check_in_distribution() for borderline inputs."""
    x = np.asarray(feature_vec, dtype=np.float32).reshape(1, -1)
    x_mean, x_std = ckpt["x_mean"], ckpt["x_std"]
    y_mean, y_std = ckpt["y_mean"], ckpt["y_std"]
    x_scaled = torch.from_numpy(((x - x_mean) / x_std).astype(np.float32)).to(device)

    was_training = model.training
    model.train()  # keep dropout active; BatchNorm still uses running stats fine on repeated calls
    preds = []
    with torch.no_grad():
        for _ in range(n_samples):
            preds.append(model(x_scaled).cpu().numpy())
    model.train(was_training)

    preds = np.stack(preds).reshape(n_samples)
    preds_unscaled = preds * y_std.reshape(-1)[0] + y_mean.reshape(-1)[0]
    return float(preds_unscaled.mean()), float(preds_unscaled.std())


# --------------------------------------------------------------------------
# Lag cache -- one entry per (lat, lon), bootstraps to 0.0 on first run.
# --------------------------------------------------------------------------
def _cache_key(lat, lon):
    return f"{lat:.4f}_{lon:.4f}"


def _load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def _get_location_state(cache, lat, lon):
    key = _cache_key(lat, lon)
    return cache.get(key, {"solar_power_history": [], "wind_pow_out_lag": 0.0})


def _set_location_state(cache, lat, lon, state):
    cache[_cache_key(lat, lon)] = state


# --------------------------------------------------------------------------
# Feature builders -- order MUST follow ckpt["feature_cols"], since that's
# what x_mean/x_std were fit against.
# --------------------------------------------------------------------------
def build_solar_feature_vec(raw, ckpt, power_history):
    """power_history: past Power (MW) predictions, oldest first.
    lag_k = value k steps back; missing history bootstraps to 0.0."""
    feature_cols = ckpt["feature_cols"]
    lags = ckpt.get("lags", [1, 2, 3])

    lag_values = {
        f"power_lag_{lag}": (power_history[-lag] if len(power_history) >= lag else 0.0)
        for lag in lags
    }

    vec = []
    for col in feature_cols:
        vec.append(lag_values[col] if col in lag_values else raw[col])
    return vec


def build_wind_feature_vec(raw, ckpt, pow_out_lag):
    feature_cols = ckpt["feature_cols"]  # base weather + pow_out_lag + ws^2 + ws^3
    ws = raw["wind_speed"]

    vec = []
    for col in feature_cols:
        if col == "pow_out_lag":
            vec.append(pow_out_lag)
        elif col == "wind_speed_sq":
            vec.append(ws ** 2)
        elif col == "wind_speed_cub":
            vec.append(ws ** 3)
        else:
            vec.append(raw[col])
    return vec


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def predict_power(lat, lon, device=None, estimate_uncertainty=False):
    device = device or torch.device("cpu")

    raw = fetch_current(lat, lon)

    # OOD check happens on the raw weather reading, before any prediction
    # is trusted -- if training would have dropped this row, we say so.
    ood_warnings = check_in_distribution(raw)

    solar_model, solar_ckpt = _load_model(SOLAR_CKPT_PATH, SolarPowerMLP, device)
    wind_model, wind_ckpt = _load_model(WIND_CKPT_PATH, WindPowerMLP, device)

    cache = _load_cache()
    state = _get_location_state(cache, lat, lon)

    solar_vec = build_solar_feature_vec(raw, solar_ckpt, state["solar_power_history"])
    solar_pred = _predict(solar_model, solar_ckpt, solar_vec, device)
    solar_pred = apply_solar_physics_floor(solar_pred, raw)

    wind_vec = build_wind_feature_vec(raw, wind_ckpt, state["wind_pow_out_lag"])
    wind_pred = _predict(wind_model, wind_ckpt, wind_vec, device)
    wind_pred = apply_wind_cutout_ceiling(wind_pred, raw)

    raw[TARGET_COL] = solar_pred
    raw[POW_TARGET_COL] = wind_pred

    if ood_warnings:
        raw["_warnings"] = ood_warnings

    if estimate_uncertainty:
        _, solar_std = _predict_with_uncertainty(solar_model, solar_ckpt, solar_vec, device)
        _, wind_std = _predict_with_uncertainty(wind_model, wind_ckpt, wind_vec, device)
        raw["_uncertainty"] = {
            f"{TARGET_COL}_std": solar_std,
            f"{POW_TARGET_COL}_std": wind_std,
        }

    max_lag = max(solar_ckpt.get("lags", [1, 2, 3]))
    state["solar_power_history"] = (state["solar_power_history"] + [solar_pred])[-max_lag:]
    state["wind_pow_out_lag"] = wind_pred
    _set_location_state(cache, lat, lon, state)
    _save_cache(cache)

    return raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--cuda", action="store_true", help="Use CUDA if available")
    parser.add_argument("--uncertainty", action="store_true",
                         help="Also estimate prediction std via MC-dropout")
    args = parser.parse_args()

    device = torch.device("cuda" if args.cuda and torch.cuda.is_available() else "cpu")
    result = predict_power(args.lat, args.lon, device=device,
                            estimate_uncertainty=args.uncertainty)

    if "_warnings" in result:
        print("WARNING: this prediction is extrapolating outside training data:")
        for w in result["_warnings"]:
            print("  -", w)

    print(result)


if __name__ == "__main__":
    main()