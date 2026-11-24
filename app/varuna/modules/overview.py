"""
app/varuna/modules/overview.py
==============================
The cover screen: the landing page's design language inside the workspace.

The departure field is drawn from the cleaned panel itself (mean departure per
district and observed season), the same numbers the landing page plots. Nothing
here recomputes a model or invents a value.
"""

from __future__ import annotations

import streamlit as st

from .. import config, ui

PAGE = {"slug": "overview", "index": "00", "label": "Overview"}

W, H = 760.0, 470.0
PAD_L, PAD_R, PAD_T, PAD_B = 8.0, 8.0, 12.0, 26.0


def _go(slug: str) -> None:
    st.session_state["varuna_module"] = slug
    st.rerun()


def _field(data, p: dict) -> tuple[str, dict]:
    """Layered ridge field: one polyline per district across the observed seasons."""
    pivot = data.district_pivot
    years = [int(year) for year in pivot.columns]
    rows = sorted(
        ((str(district), pivot.loc[district]) for district in pivot.index),
        key=lambda item: float(item[1].mean()),
    )

    peak = {"district": "", "year": 0, "value": float("-inf")}
    low = {"district": "", "year": 0, "value": float("inf")}
    for district, series in rows:
        for year in years:
            value = series.get(year)
            if value != value:  # NaN
                continue
            value = float(value)
            if value > peak["value"]:
                peak = {"district": district, "year": year, "value": value}
            if value < low["value"]:
                low = {"district": district, "year": year, "value": value}

    step = (W - PAD_L - PAD_R) / max(len(years) - 1, 1)
    row_gap = (H - PAD_T - PAD_B) / max(len(rows), 1)
    rise = row_gap / 34.0

    def x_at(index: int) -> float:
        return PAD_L + index * step

    def y_at(baseline: float, value: float) -> float:
        clamped = min(max(value, -60.0), 130.0)
        return baseline - clamped * rise

    strokes = []
    for i, (district, series) in enumerate(rows):
        baseline = PAD_T + (i + 0.85) * row_gap
        points = []
        for j, year in enumerate(years):
            value = series.get(year)
            if value != value:
                continue
            points.append(f"{x_at(j):.1f} {y_at(baseline, float(value)):.1f}")
        if len(points) < 2:
            continue
        opacity = 0.3 + 0.6 * (i / max(len(rows) - 1, 1))
        strokes.append(
            f'<polyline points="{" ".join(points)}" stroke="{p["rain"]}" '
            f'stroke-opacity="{opacity:.2f}">'
            f"<title>{ui.esc(district)} \u00b7 mean {series.mean():+.1f}%</title>"
            "</polyline>"
        )

    def marker(record: dict, color: str) -> str:
        if not record["district"]:
            return ""
        index = years.index(record["year"])
        baseline = PAD_T + (rows.index(next(r for r in rows if r[0] == record["district"])) + 0.85) * row_gap
        return (
            f'<circle cx="{x_at(index):.1f}" cy="{y_at(baseline, record["value"]):.1f}" '
            f'r="2.6" fill="{color}">'
            f'<title>{ui.esc(record["district"])} {record["year"]} \u00b7 {record["value"]:+.1f}%</title>'
            "</circle>"
        )

    axis = "".join(
        f'<text x="{x_at(j):.1f}" y="{H - 6:.1f}" fill="{p["muted"]}" font-size="9" '
        f'font-family="Geist Mono, monospace" letter-spacing="1.2" '
        f'text-anchor="{"start" if j == 0 else ("end" if j == len(years) - 1 else "middle")}">'
        f"{year}</text>"
        for j, year in enumerate(years)
    )

    svg = (
        f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" '
        f'aria-label="Mean rainfall departure by district and season, {len(rows)} districts across '
        f'{len(years)} observed seasons">'
        f'<g fill="none" stroke-width="1.15" stroke-linejoin="round" stroke-linecap="round">'
        f'{"".join(strokes)}</g>'
        f"{marker(peak, p['rain'])}{marker(low, p['terra'])}"
        f"{axis}"
        "</svg>"
    )
    return svg, {"peak": peak, "low": low, "districts": len(rows), "years": years}


def _caption(extremes: dict) -> str:
    peak, low = extremes["peak"], extremes["low"]
    return (
        '<div class="v-field__caption">'
        f"Mean departure by district and season, from the cleaned station panel. "
        f"Peak <b>{ui.esc(peak['district'].title())} {peak['year']}</b> at "
        f"<b>{peak['value']:+.1f}%</b>, low <b>{ui.esc(low['district'].title())} {low['year']}</b> at "
        f"<b>{low['value']:+.1f}%</b>. Hover a ridge for its district mean."
        "</div>"
    )


def render(data, selection, p: dict) -> None:
    svg, extremes = _field(data, p)
    stations = int(data.clean.groupby("year").size().max())
    seasons = int(len(data.clean))
    flagged = int(len(data.suspect))
    regimes = int(data.clusters["cluster_id"].nunique())

    left, right = st.columns([1, 1.04], gap="large")

    with left:
        st.markdown(
            f"""
            <div class="v-cover">
              <div class="v-cover__kicker"><span class="v-cover__dot"></span>Karnataka &middot; hobli monsoon intelligence</div>
              <h1>See the dry hobli the district average hides.</h1>
              <p class="v-cover__lead">
                Varuna reads five observed monsoon seasons across the Karnataka hobli network.
                Pick a station to read its departure, its climatological regime and the classifier
                verdict, with the data caveats still attached.
              </p>
              <div class="v-cover__counts">
                <span><b>{stations:,}</b> stations each season</span>
                <span><b>{seasons:,}</b> clean station seasons</span>
                <span><b>{flagged:,}</b> flagged baseline normals</span>
                <span><b>{regimes}</b> climatological regimes</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.container(key="cover-actions"):
            open_col, district_col = st.columns(2, gap="small")
            with open_col:
                if st.button("Open the workspace", type="primary", width="stretch"):
                    _go("hobli")
            with district_col:
                if st.button("District intelligence", width="stretch"):
                    _go("districts")

    with right:
        st.markdown(
            f'<div class="v-field">{svg}{_caption(extremes)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        ui.section(
            "01",
            "One station at a time",
            f"{config.OBSERVED_YEARS[0]}\u2013{config.OBSERVED_YEARS[-1]} \u00b7 {config.MISSING_YEAR} not published",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        ui.paragraph(
            f"The workspace holds {stations:,} station records per season across {extremes['districts']} districts. "
            "Every reading is a published station record or a stored model artifact, and every "
            "suspect baseline normal is flagged where it appears rather than smoothed away."
        ),
        unsafe_allow_html=True,
    )
