"""
Module 01 -- Hobli Intelligence
===============================
A single-station meteorological dossier: history, departure against the
KSNDMC thresholds, model assessment and forward outlook.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .. import charts, config, ui
from ..data import zone_of, adjusted_zone_of

PAGE = {
    "slug": "hobli",
    "index": "01",
    "label": "Hobli Intelligence",
    "title": "Hobli Intelligence",
    "kicker": "Module 01 \u00b7 Station dossier",
    "lede": (
        "A complete reading of one hobli station: how its monsoon has behaved across "
        "the observed panel, where it sits against the KSNDMC departure thresholds, "
        "what the classifier concludes, and what the forward projection implies."
    ),
}


def _narrative(hist: pd.DataFrame, latest: pd.Series, zone: str) -> str:
    first_year = int(hist["year"].min())
    mean_dep = hist["departure_pct"].mean()
    deficit_years = int((hist["departure_pct"] <= config.DROUGHT_THRESHOLD).sum())
    excess_years = int((hist["departure_pct"] >= config.HISTORIC_EXCESS_THRESHOLD).sum())
    direction = "below" if latest["departure_pct"] < 0 else "above"
    return (
        f"In {int(latest['year'])}, {latest['hobli']} recorded {latest['actual_mm']:,.1f} mm against a "
        f"normal of {latest['normal_mm']:,.1f} mm \u2014 {abs(latest['departure_pct']):.1f}% {direction} normal, "
        f"placing it in the {config.ZONE_LABELS[zone].lower()} band. Across the observed panel since "
        f"{first_year}, its mean departure is {mean_dep:+.1f}% with {deficit_years} deficit "
        f"{'year' if deficit_years == 1 else 'years'} (\u2264 \u221220%) and {excess_years} excess "
        f"{'year' if excess_years == 1 else 'years'} (\u2265 +20%)."
    )


def _forecast_block(year: int, row: pd.Series, shift: int, p: dict) -> str:
    norm = float(row["normal_mm"])
    dep = float(row["predicted_departure_pct"]) + shift
    margin = float(row["uncertainty_margin_pct"])
    actual = max(0.0, norm * (1 + dep / 100))
    low = max(0.0, norm * (1 + (dep - margin) / 100))
    high = max(0.0, norm * (1 + (dep + margin) / 100))
    zone = zone_of(dep)
    color = p[config.ZONE_TONES[zone]]
    simulated = (
        f'<span class="v-chip v-chip--amber">Simulated {shift:+d}%</span>' if shift else ""
    )
    return f"""
    <div class="v-verdict" style="border-left:2px solid {color}">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:.6rem">
        <div class="v-verdict__label">{year} projection</div>
        <div>{simulated} {ui.zone_chip(zone)}</div>
      </div>
      <div class="v-verdict__big" style="color:{color};margin-top:.6rem">{actual:,.0f}<span style="font-size:.72rem;color:var(--v-muted);letter-spacing:0"> mm</span></div>
      <div class="v-deflist" style="margin-top:.55rem">
        <div><dt>Normal</dt><dd>{norm:,.0f} mm</dd></div>
        <div><dt>Departure</dt><dd>{dep:+.1f}%</dd></div>
        <div><dt>Uncertainty range</dt><dd>{low:,.0f}\u2013{high:,.0f} mm</dd></div>
        <div><dt>Model margin</dt><dd>\u00b1{margin:.1f}%</dd></div>
      </div>
      <div style="margin-top:.6rem">
        {ui.probability_bars({z: row.get(f"prob_{z}", 0.0) for z in config.ZONE_ORDER}, p)}
      </div>
    </div>
    """


def render(data, sel: dict, p: dict) -> None:
    district, taluk, hobli = sel["district"], sel["taluk"], sel["hobli"]
    hist = data.station_history(district, taluk, hobli)
    cluster = data.station_cluster(district, taluk, hobli)

    if hist.empty:
        ui.render(ui.page_header(PAGE["kicker"], hobli, "No observed records exist for this station."))
        ui.render(ui.empty_state("No clean rainfall records were found for this station."))
        return

    latest = hist.iloc[-1]
    year = int(latest["year"])
    dep = float(latest["departure_pct"])
    suspect_key = (district, taluk, hobli)
    suspect = data.suspect_keys
    is_suspect = suspect_key in suspect
    median_normal = float(data.clean["normal_mm"].median())
    zone, zone_overridden = adjusted_zone_of(
        dep, float(latest["normal_mm"]), float(latest["actual_mm"]),
        is_suspect, median_normal,
    )
    zone_tone = config.ZONE_TONES[zone]
    cluster_name = cluster["cluster_name"] if cluster is not None else "\u2014"
    cluster_id = int(cluster["cluster_id"]) if cluster is not None else 2

    ui.render(
        ui.page_header(
            PAGE["kicker"],
            hobli,
            _narrative(hist, latest, zone),
            meta=[
                ("District", district),
                ("Taluk", taluk),
                ("Observed years", f"{len(hist)} of 6 panel years"),
                ("Climatological regime", cluster_name),
            ],
        )
    )

    # ---------------------------------------------------------- identity --
    ui.render(
        f"""
        <div class="v-dossier">
          <div>
            <div class="v-crumb">{ui.esc(district)} <span style="color:var(--v-line-strong)">/</span>
              {ui.esc(taluk)} <span style="color:var(--v-line-strong)">/</span> <b>{ui.esc(hobli)}</b></div>
            <div style="display:flex;align-items:center;gap:.5rem;margin-top:.7rem">
              {ui.glyph(cluster_id, p)}<span class="v-kicker">Cluster {cluster_id} \u00b7 {ui.esc(config.CLUSTERS[cluster_id]["short"])}</span>
            </div>
            <h2>{ui.esc(hobli)} station record</h2>
            <div class="v-dossier__sub">Canonical station key \u00b7 {ui.esc(district)} / {ui.esc(taluk)} / {ui.esc(hobli)}
              \u00b7 {len(hist)} observed monsoon seasons</div>
          </div>
          <div class="v-verdict" style="border-top:2px solid {p[zone_tone]}">
            <div class="v-verdict__label">{year} monsoon departure</div>
            <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:1rem;margin-top:.35rem">
              <div class="v-verdict__big" style="color:{p[zone_tone]}">{dep:+.1f}%</div>
              {ui.zone_chip(zone)}
            </div>
            <div class="v-verdict__meta" style="margin-top:.7rem">
              <span>Normal {latest['normal_mm']:,.1f} mm</span>
              <span>Observed {latest['actual_mm']:,.1f} mm</span>
            </div>
          </div>
        </div>
        """
    )

    ui.render(
        ui.stat_strip(
            [
                {"label": "Normal baseline", "value": ui.num(latest["normal_mm"], 1), "unit": "mm", "note": "KSNDMC long-term normal"},
                {"label": f"{year} observed", "value": ui.num(latest["actual_mm"], 1), "unit": "mm", "note": f"{latest['actual_mm'] - latest['normal_mm']:+,.1f} mm vs normal"},
                {"label": "Panel mean departure", "value": ui.signed(hist["departure_pct"].mean(), 1, "%"), "note": "Five observed seasons"},
                {"label": "Departure volatility", "value": ui.num(hist["departure_pct"].std(ddof=0), 1), "unit": "pp", "note": "Standard deviation"},
                {"label": "Deficit years", "value": str(int((hist["departure_pct"] <= config.DROUGHT_THRESHOLD).sum())), "unit": f"of {len(hist)}", "note": "\u2264 \u221220% departure", "color": p["terra"]},
                {"label": "Excess years", "value": str(int((hist["departure_pct"] >= config.HISTORIC_EXCESS_THRESHOLD).sum())), "unit": f"of {len(hist)}", "note": "\u2265 +20% departure", "color": p["rain"]},
            ]
        )
    )

    if is_suspect:
        row = data.suspect[
            (data.suspect["district"] == district)
            & (data.suspect["taluk"] == taluk)
            & (data.suspect["hobli"] == hobli)
        ].iloc[0]
        override_note = (
            " Because this station receives objectively high rainfall "
            f"(<b>{latest['actual_mm']:,.1f} mm</b> in {year}), the drought label has been "
            "overridden to <b>Stable</b>."
            if zone_overridden
            else ""
        )
        ui.render(
            ui.callout(
                "amber",
                "Baseline normal flagged \u00b7 data-quality caveat",
                ui.paragraph(
                    f"This station is catalogued in <code>reports/suspect_normals.csv</code> with an unchanged "
                    f"normal of <b>{row['normal_mm']:,.1f} mm</b> and persistent "
                    f"<b>{ui.esc(row['direction'].replace('_', ' '))}</b> departures "
                    f"(mean {row['mean_departure_pct']:+.2f}%). Extreme departures here can measure an "
                    f"uncalibrated benchmark as much as the weather.{override_note}"
                ),
            )
        )

    # ------------------------------------------------- departure indicator --
    ui.render(ui.section("01", "Departure against reference thresholds", f"KSNDMC risk zones \u00b7 {year}"))
    ui.render(ui.meter(dep, p, zone))

    # ------------------------------------------------------------ history --
    ui.render(ui.section("02", "Observed rainfall history", f"{len(hist)} seasons \u00b7 2020\u20132025"))
    col_chart, col_register = st.columns([1.5, 1], gap="large")
    with col_chart:
        st.plotly_chart(
            charts.rainfall_history(hist, p),
            theme=None,
            config={"displayModeBar": False, "responsive": True},
            width="stretch",
        )
        st.caption("Bars are observed annual rainfall. The dashed line is the station's normal baseline. KSNDMC published no hobli-level table for 2023, so the axis keeps the gap visible rather than interpolating it.")
    with col_register:
        rows = []
        for _, r in hist.iterrows():
            rz, _ = adjusted_zone_of(
                r["departure_pct"], float(r["normal_mm"]),
                float(r["actual_mm"]), is_suspect, median_normal,
            )
            rows.append(
                {
                    "year": str(int(r["year"])),
                    "actual": ui.num(r["actual_mm"], 1),
                    "normal": ui.num(r["normal_mm"], 1),
                    "dep": ui.signed(r["departure_pct"], 1, "%"),
                    "zone": {"raw": ui.zone_chip(rz)},
                }
            )
        rows.insert(
            3,
            {
                "year": "2023",
                "actual": "\u2014",
                "normal": "\u2014",
                "dep": "\u2014",
                                    "zone": {"raw": ui.chip("absent", "neutral")},
            },
        )
        ui.render(
            ui.table(
                [
                    {"label": "Year", "key": "year", "cls": "v-num"},
                    {"label": "Observed", "key": "actual", "align": "r"},
                    {"label": "Normal", "key": "normal", "align": "r"},
                    {"label": "Departure", "key": "dep", "align": "r"},
                    {"label": "Zone", "key": "zone"},
                ],
                rows,
                caption="Annual observation register",
            )
        )

    # ------------------------------------------------------- model verdict --
    ui.render(ui.section("03", "Model risk assessment", "2025 hold-out \u00b7 Random Forest"))
    feature = data.station_features(district, taluk, hobli, 2025)
    left, right = st.columns([1, 1], gap="large")

    if feature is None:
        with left:
            ui.render(ui.empty_state("This station has no 2025 feature row, so hold-out inference is unavailable."))
    else:
        try:
            from src.predict_risk import predict_risk

            with st.spinner("Running hold-out inference"):
                result = predict_risk(feature)
        except Exception as exc:  # inference contract or artifact failure
            with left:
                ui.render(
                    ui.callout(
                        "terra",
                        "Inference unavailable",
                        ui.paragraph(
                            "The classifier could not be evaluated for this station: "
                            f"<code>{ui.esc(exc)}</code>. Check <code>models/best_classifier.joblib</code> "
                            "and <code>models/feature_columns.json</code>."
                        ),
                    )
                )
            result = None

        if result:
            predicted = result["risk_zone"]
            probs = result["probabilities"]
            agreement = predicted == zone
            with left:
                ui.render(
                    f"""
                    <div class="v-verdict" style="border-left:2px solid {p[config.ZONE_TONES[predicted]]}">
                      <div class="v-verdict__label">Classifier verdict \u00b7 2025</div>
                      <div class="v-verdict__value" style="color:{p[config.ZONE_TONES[predicted]]}">{ui.esc(config.ZONE_LABELS[predicted])}</div>
                      <div class="v-verdict__meta">
                        <span>{ui.esc(config.ZONE_LABELS[zone])} observed</span>
                        <span>{"model and record agree" if agreement else "model disagrees with the record"}</span>
                      </div>
                    </div>
                    """
                )
                ui.render(
                    ui.paragraph(
                        "This is genuine out-of-time evidence: 2025 was withheld from training. "
                        "The verdict is one model output from a class-imbalanced problem, not a "
                        "forecast of agronomic drought."
                    )
                )
                ui.render(
                    ui.callout(
                        "rain",
                        "How much weight to give this",
                        ui.paragraph(
                            "The selected Random Forest reaches 70.82% accuracy but only 6.06% drought "
                            "recall on the 2025 hold-out. In validation across unseen districts it "
                            "recovered 30.49% of drought events. Treat a \u201cstable\u201d verdict as a weak "
                            "signal and a \u201cdrought-prone\u201d verdict as a prompt to investigate."
                        ),
                    )
                )
            with right:
                ui.render(ui.sub_label("Calibrated class probabilities"))
                ui.render(ui.probability_bars(probs, p))
                ui.render(
                    ui.paragraph(
                        "Probabilities come from the serialized forest's class distribution. "
                        "They reflect confidence inside the training distribution and are not "
                        "calibrated frequentist odds."
                    )
                )

    # --------------------------------------------------------- spatial ctx --
    if feature is not None:
        taluk_year = data.clean[
            (data.clean["district"] == district)
            & (data.clean["taluk"] == taluk)
            & (data.clean["year"] == year)
        ]
        district_year = data.clean[
            (data.clean["district"] == district) & (data.clean["year"] == year)
        ]
        if len(taluk_year) and len(district_year):
            t_dep = float(taluk_year["departure_pct"].mean())
            d_dep = float(district_year["departure_pct"].mean())
            ui.render(ui.section("04", "Administrative context", f"{year} taluk and district means"))
            c_chart, c_meta = st.columns([1.5, 1], gap="large")
            with c_chart:
                st.plotly_chart(
                    charts.departure_context(dep, t_dep, d_dep, p),
                    theme=None,
                    config={"displayModeBar": False, "responsive": True},
                    width="stretch",
                )
            with c_meta:
                ui.render(ui.sub_label("Micro-climatic offset"))
                ui.render(
                    ui.deflist(
                        [
                            ("Station vs taluk", ui.signed(dep - t_dep, 2, " pp")),
                            ("Station vs district", ui.signed(dep - d_dep, 2, " pp")),
                            ("Taluk mean departure", ui.signed(t_dep, 2, "%")),
                            ("District mean departure", ui.signed(d_dep, 2, "%")),
                            ("Stations in taluk", f"{len(taluk_year)}"),
                        ]
                    )
                )
                ui.render(
                    ui.paragraph(
                        "A station far below its taluk mean during the same season is a "
                        "micro-climatic signal worth checking for a benchmark artifact before "
                        "it is read as local drought."
                    )
                )

    # ------------------------------------------------------------ outlook --
    future = data.station_future(district, taluk, hobli)
    if future.empty:
        return

    ui.render(ui.section("05", "Forward outlook", "Autoregressive projection \u00b7 2026\u20132027"))
    ui.render(
        ui.callout(
            "amber",
            "Read the projection as a scenario, not a forecast",
            ui.paragraph(
                "Monsoon rainfall is driven by ENSO, IOD and MJO teleconnections that a statistical "
                "regressor fed with rainfall history cannot resolve years ahead. The ranges below widen "
                "with lead time for that reason."
            ),
        )
    )
    shift = st.slider(
        "Simulated precipitation shift",
        min_value=-30,
        max_value=30,
        value=0,
        step=5,
        format="%+d%%",
        help="Perturbs both projected years by a fixed percentage to test how the station responds to a drier or wetter monsoon regime.",
    )
    f26, f27 = st.columns(2, gap="large")
    for column, target_year in ((f26, 2026), (f27, 2027)):
        row = future[future["year"] == target_year]
        if len(row):
            with column:
                ui.render(_forecast_block(target_year, row.iloc[0], shift, p))

    st.plotly_chart(
        charts.outlook_trajectory(hist, future, p),
        theme=None,
        config={"displayModeBar": False, "responsive": True},
        width="stretch",
    )
    st.caption("Observed history, station normal and the projected trajectory with its stated uncertainty band. Shading marks the unpublished 2023 season.")

    taluk_future = data.future[
        (data.future["district"] == district)
        & (data.future["taluk"] == taluk)
        & (data.future["year"] == 2026)
    ].sort_values("predicted_departure_pct")
    if len(taluk_future):
        ui.render(ui.sub_label(f"2026 projections across {taluk} taluk"))
        ui.render(
            ui.table(
                [
                    {"label": "Hobli", "key": "hobli"},
                    {"label": "Normal mm", "key": "normal", "align": "r"},
                    {"label": "Projected mm", "key": "projected", "align": "r"},
                    {"label": "Departure", "key": "dep", "align": "r"},
                    {"label": "Zone", "key": "zone"},
                ],
                [
                    {
                        "hobli": r["hobli"],
                        "normal": ui.num(r["normal_mm"], 0),
                        "projected": ui.num(r["predicted_actual_mm"], 0),
                        "dep": ui.signed(r["predicted_departure_pct"], 1, "%"),
                        "zone": {"raw": ui.zone_chip(r["risk_zone"])},
                    }
                    for _, r in taluk_future.iterrows()
                ],
                caption=f"{taluk} taluk \u00b7 ordered from driest projection to wettest",
            )
        )

    with st.expander("Methodology and caveats for this module"):
        ui.render(
            ui.paragraph(
                "Departures are fixed by the project's target contract: "
                f"drought-prone \u2264 {config.DROUGHT_THRESHOLD:.0f}%, stable between "
                f"{config.DROUGHT_THRESHOLD:.0f}% and +{config.EXCESS_THRESHOLD:.0f}%, flood-prone "
                f"\u2265 +{config.EXCESS_THRESHOLD:.0f}%. The classifier reads 13 ex-ante features "
                "computed only from years before the target year, so no future information leaks "
                "into the 2025 hold-out verdict. The 2026\u20132027 figures are the existing "
                "autoregressive projections in "
                "<code>data/features/future_projections_2026_2027.csv</code>. The simulator applies "
                "a user-chosen perturbation to those projections; it does not retrain or alter stored "
                "outputs."
            )
        )
