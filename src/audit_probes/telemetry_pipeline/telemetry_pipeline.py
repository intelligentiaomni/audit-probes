"""Telemetry cleaning, anomaly flagging, and plotting helpers."""

from __future__ import annotations

import json
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - optional dependency
    plt = None

try:
    import pandas as pd
except ImportError:  # pragma: no cover - optional dependency
    pd = None


INTERPOLATION_ASSUMPTION = (
    "Missing altitude values are linearly interpolated after sorting by time. "
    "This is suitable for lightweight exploratory analysis, not mission-critical reconstruction."
)


def load_telemetry(path: str | Path):
    _require_pandas()
    file_path = Path(path)

    if file_path.suffix.lower() == ".csv":
        return pd.read_csv(file_path)

    if file_path.suffix.lower() == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        records = payload.get("records", payload) if isinstance(payload, dict) else payload
        return pd.DataFrame(records)

    raise ValueError(f"Unsupported telemetry format: {file_path.suffix}")


def clean_telemetry(df, time_column: str = "time", altitude_column: str = "altitude"):
    _require_pandas()
    cleaned = df.copy()
    cleaned[altitude_column] = pd.to_numeric(cleaned[altitude_column], errors="coerce")
    cleaned["altitude_interpolated"] = cleaned[altitude_column].isna()

    cleaned = cleaned.dropna(subset=[time_column])
    cleaned = cleaned.sort_values(by=time_column).reset_index(drop=True)
    cleaned[altitude_column] = cleaned[altitude_column].interpolate(
        method="linear", limit_direction="both"
    )
    cleaned = cleaned.dropna(subset=[altitude_column])
    cleaned = cleaned[cleaned[altitude_column] > 0].reset_index(drop=True)
    cleaned.attrs["interpolation_assumption"] = INTERPOLATION_ASSUMPTION
    return cleaned


def flag_anomalies(
    df,
    altitude_column: str = "altitude",
    jump_threshold: float = 1500.0,
):
    _require_pandas()
    flagged = df.copy()
    flagged["altitude_delta"] = flagged[altitude_column].diff().fillna(0.0)
    flagged["anomaly_flag"] = flagged["altitude_delta"].abs() > jump_threshold
    flagged["anomaly_reason"] = flagged["anomaly_flag"].map(
        lambda is_flagged: "altitude jump exceeds threshold" if is_flagged else ""
    )
    return flagged


def build_dashboard_frame(path: str | Path):
    frame = load_telemetry(path)
    frame = clean_telemetry(frame)
    return flag_anomalies(frame)


def plot_altitude_profile(
    df,
    time_column: str = "time",
    altitude_column: str = "altitude",
    output_path: str | Path | None = None,
    show: bool = False,
):
    if plt is None:  # pragma: no cover - depends on optional dependency
        raise RuntimeError("matplotlib is required for plotting")

    figure, axis = plt.subplots(figsize=(9, 4.5))
    axis.plot(df[time_column], df[altitude_column], linewidth=2, color="#0b6e4f")
    axis.set_title("Telemetry Altitude Profile")
    axis.set_xlabel("Time")
    axis.set_ylabel("Altitude")
    axis.grid(alpha=0.25)

    flagged = df[df.get("anomaly_flag", False)]
    if not flagged.empty:
        axis.scatter(
            flagged[time_column],
            flagged[altitude_column],
            color="#b02e0c",
            label="Anomaly",
            zorder=3,
        )
        axis.legend()

    if output_path is not None:
        figure.tight_layout()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(output_path, dpi=150)

    if show:
        plt.show()
    else:
        plt.close(figure)


def _require_pandas() -> None:
    if pd is None:  # pragma: no cover - depends on optional dependency
        raise RuntimeError("pandas is required for telemetry processing")
