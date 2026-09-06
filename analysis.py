"""
Week 1 - E-Governance Data Exploration
Author: Mayank
Purpose: Clean, validate, summarize and visualize public-service/grievance data.

IMPORTANT:
The included CSV is an ILLUSTRATIVE demonstration dataset created for the internship report.
It is NOT official government statistics. Replace it with a verified public dataset before
making real-world claims.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "illustrative_e_governance_data.csv"
PROCESSED_FILE = ROOT / "data" / "processed" / "cleaned_e_governance_data.csv"
FIG_DIR = ROOT / "figures"


def load_data(path=RAW_FILE):
    """Load the CSV dataset."""
    return pd.read_csv(path)


def clean_data(df):
    """Basic cleaning and derived metric creation."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
    )

    numeric_cols = [
        "grievances_received",
        "grievances_disposed",
        "avg_resolution_days",
        "digital_service_score",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates()

    df["disposal_rate_percent"] = (
        df["grievances_disposed"] / df["grievances_received"] * 100
    ).round(2)

    return df


def validate_data(df):
    """Return simple validation results."""
    checks = {
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_values": int(df.isna().sum().sum()),
        "negative_received": int((df["grievances_received"] < 0).sum()),
        "negative_disposed": int((df["grievances_disposed"] < 0).sum()),
        "disposed_greater_than_received": int(
            (df["grievances_disposed"] > df["grievances_received"]).sum()
        ),
        "invalid_disposal_rate": int(
            ((df["disposal_rate_percent"] < 0) | (df["disposal_rate_percent"] > 100)).sum()
        ),
    }
    return checks


def descriptive_statistics(df):
    cols = [
        "grievances_received",
        "grievances_disposed",
        "disposal_rate_percent",
        "avg_resolution_days",
        "digital_service_score",
    ]
    return df[cols].describe().round(2)


def make_figures(df):
    FIG_DIR.mkdir(exist_ok=True)

    # Received vs disposed
    x = range(len(df))
    plt.figure(figsize=(10, 5))
    plt.bar([i - 0.2 for i in x], df["grievances_received"], width=0.4, label="Received")
    plt.bar([i + 0.2 for i in x], df["grievances_disposed"], width=0.4, label="Disposed")
    plt.xticks(list(x), df["state_ut"], rotation=45, ha="right")
    plt.ylabel("Number of grievances")
    plt.title("Illustrative Grievance Volume: Received vs Disposed")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "received_vs_disposed.png", dpi=180)
    plt.close()

    # Disposal rate
    tmp = df.sort_values("disposal_rate_percent", ascending=False)
    plt.figure(figsize=(10, 5))
    plt.bar(tmp["state_ut"], tmp["disposal_rate_percent"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Disposal rate (%)")
    plt.title("Illustrative Disposal Rate by State/UT")
    plt.ylim(0, 105)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "disposal_rate.png", dpi=180)
    plt.close()

    # Resolution time
    tmp = df.sort_values("avg_resolution_days")
    plt.figure(figsize=(10, 5))
    plt.bar(tmp["state_ut"], tmp["avg_resolution_days"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Average resolution time (days)")
    plt.title("Illustrative Average Resolution Time")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "resolution_time.png", dpi=180)
    plt.close()


def run():
    df = clean_data(load_data())
    checks = validate_data(df)
    print("Validation:", checks)
    print("\nDescriptive statistics:\n")
    print(descriptive_statistics(df))
    PROCESSED_FILE.parent.mkdir(exist_ok=True)
    df.to_csv(PROCESSED_FILE, index=False)
    make_figures(df)
    print(f"\nProcessed data saved to: {PROCESSED_FILE}")
    print(f"Figures saved to: {FIG_DIR}")


if __name__ == "__main__":
    run()
