from __future__ import annotations

from pathlib import Path
import pickle

from loguru import logger
import pandas as pd
from sklearn.cluster import KMeans

from science_the_data.helpers.splits_io import load_splits
from science_the_data.helpers.types import DataSplits, PipelineStage

EDA_CACHE_DIR = Path("eda_cache")
N_GEO_CLUSTERS = 20


def eda_pre_prune_pipeline(splits: DataSplits) -> None:
    logger.info("=== EDA Pre-Prune Pipeline ===")

    stage = PipelineStage.PROCESSED
    df_train, _, _ = load_splits(*splits.as_tuple(), stage)
    logger.info("Pre-prune train set: {:,} rows × {} cols", len(df_train), df_train.shape[1])

    payload: dict = {"stage": "pre_prune"}

    if {"Latitude", "Longitude"}.issubset(df_train.columns):
        logger.info("Fitting geo clusters (k={}) ...", N_GEO_CLUSTERS)

        coords = df_train[["Latitude", "Longitude"]].dropna()
        missing_pct = df_train[["Latitude", "Longitude"]].isna().mean().to_dict()

        kmeans = KMeans(n_clusters=N_GEO_CLUSTERS, random_state=42, n_init=10)
        df_train.loc[coords.index, "geo_cluster"] = kmeans.fit_predict(coords)
        df_train["geo_cluster"] = df_train["geo_cluster"].fillna(-1).astype(int)

        cluster_fail_rate = df_train.groupby("geo_cluster")["Results"].mean().to_dict()

        cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=["Latitude", "Longitude"])
        cluster_centers["cluster"] = range(N_GEO_CLUSTERS)
        cluster_centers["fail_rate"] = [
            cluster_fail_rate.get(i, None) for i in range(N_GEO_CLUSTERS)
        ]

        payload["geo_clusters"] = {
            "missing_pct": missing_pct,
            "n_clusters": N_GEO_CLUSTERS,
            "cluster_fail_rate": cluster_fail_rate,
            "cluster_centers": cluster_centers.to_dict(orient="records"),
            "cluster_sizes": df_train["geo_cluster"].value_counts().sort_index().to_dict(),
        }

        logger.info(
            "Geo clusters done — highest-risk cluster: {} ({:.1%} fail rate)",
            max(cluster_fail_rate, key=cluster_fail_rate.get),  # type: ignore
            max(cluster_fail_rate.values()),
        )
    else:
        logger.warning("Lat/Lon columns not found — skipping geo clustering")

    TARGET = "Results"

    if "Facility Type" in df_train.columns:
        logger.info("Computing facility type stats ...")
        payload["top_facility_types"] = (
            df_train["Facility Type"].value_counts().head(15)
        )
        payload["facility_fail_rates"] = (
            df_train.groupby("Facility Type")[TARGET]
            .agg(total="count", failures="sum")
            .assign(fail_rate=lambda d: d["failures"] / d["total"])
            .query("total >= 50")           # drop statistically thin slices
            .sort_values("fail_rate", ascending=False)
            .reset_index()
        )
        logger.info(
            "Highest-risk facility type: {} ({:.1%})",
            payload["facility_fail_rates"].iloc[0]["Facility Type"],
            payload["facility_fail_rates"].iloc[0]["fail_rate"],
        )

    if "Risk" in df_train.columns:
        logger.info("Computing risk level vs actual outcome ...")
        payload["risk_distribution"] = df_train["Risk"].value_counts()
        payload["risk_vs_outcome"] = (
            df_train.groupby("Risk")[TARGET]
            .agg(total="count", failures="sum")
            .assign(fail_rate=lambda d: d["failures"] / d["total"])
            .reset_index()
        )

    EDA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = EDA_CACHE_DIR / "eda_pre_prune_payload.pkl"
    with open(cache_path, "wb") as f:
        pickle.dump(payload, f)

    logger.success("Pre-prune EDA cache written → {}", cache_path)
    logger.info("=== EDA Pre-Prune Pipeline complete ===")
