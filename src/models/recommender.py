def rank_materials(df, top_n=5):
    df["final_rank_score"] = (
        0.5 * df["sustainability_score"] +
        0.3 * (1 / df["predicted_co2"]) +
        0.2 * (1 / df["predicted_cost"])
    )

    return df.sort_values(
        by="final_rank_score",
        ascending=False
    ).head(top_n)
