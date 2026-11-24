"""
app/app.py
==========
VARUNA -- Karnataka Rainfall Intelligence.

Streamlit entry point for the redesigned workspace. The application shell owns
navigation, the global station selector, theming and error states; the five
analytical modules live in `app/varuna/modules/`.

The machine-learning pipeline is untouched: this interface reads the existing
artifacts in data/, models/ and reports/ and calls the existing inference
helper in src/predict_risk.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
for path in (str(ROOT_DIR), str(APP_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

from varuna import config, theme, ui  # noqa: E402
from varuna.data import DataUnavailable, VarunaData, load_data  # noqa: E402
from varuna.modules import districts, hobli, models, overview, quality, zones  # noqa: E402

st.set_page_config(
    page_title="VARUNA \u00b7 Karnataka Rainfall Intelligence",
    page_icon="\U0001f327",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "About": (
            "VARUNA \u2014 hobli-level rainfall deviation and drought-risk analytics for "
            "Karnataka. Data: KSNDMC via OpenCity (ODC-BY)."
        )
    },
)

MODULES = [overview.PAGE, hobli.PAGE, zones.PAGE, districts.PAGE, quality.PAGE, models.PAGE]
RENDERERS = {
    "overview": overview.render,
    "hobli": hobli.render,
    "zones": zones.render,
    "districts": districts.render,
    "quality": quality.render,
    "models": models.render,
}


# ------------------------------------------------------------------- theme --
def resolve_theme() -> str:
    """Resolve the theme once per session and keep it stable across reruns.

    Streamlit's configured base theme is light; the app's own token layer owns the
    rest. The session is seeded on the first run so navigation never flips it.
    """
    saved = st.session_state.get("varuna_theme")
    if saved not in ("light", "dark"):
        requested = st.query_params.get("theme")
        saved = requested if requested in ("light", "dark") else "dark"
        st.session_state["varuna_theme"] = saved
    return saved


def switch_theme(target: str) -> None:
    st.session_state["varuna_theme"] = target
    try:
        st.query_params["theme"] = target
    except Exception:
        pass
    st.rerun()


theme_name = resolve_theme()
p = theme.palette(theme_name)

st.markdown(f"<style>{theme.css_for(theme_name)}</style>", unsafe_allow_html=True)


# -------------------------------------------------------------------- nav ---
def module_state() -> str:
    slug = st.session_state.get("varuna_module", "overview")
    return slug if slug in RENDERERS else "overview"


def set_module(slug: str) -> None:
    st.session_state["varuna_module"] = slug
    st.rerun()


def brand_block() -> str:
    return f"""
    <div class="v-brand">
      <div class="v-brand__row" style="color:{p['ink']}">
        <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
          <rect x="0.75" y="0.75" width="22.5" height="22.5" fill="none"
                stroke="currentColor" stroke-opacity=".28"/>
          <path d="M6 17V11.5 M10 17V7 M14 17V13.2 M18 17V9.4"
                stroke="currentColor" stroke-width="1.6" stroke-linecap="square"/>
          <path d="M4.2 19.6H19.8" stroke="currentColor" stroke-width="1.6"/>
        </svg>
        <span class="v-brand__name">VARUNA</span>
      </div>
      <div class="v-brand__meta">Karnataka rainfall intelligence<br/>Hobli deviation &amp; drought risk</div>
    </div>
    """


def station_glance(data: VarunaData, sel: dict) -> str:
    hist = data.station_history(sel["district"], sel["taluk"], sel["hobli"])
    if hist.empty:
        return ""
    latest = hist.iloc[-1]
    zone = "drought_prone" if latest["departure_pct"] <= config.DROUGHT_THRESHOLD else (
        "flood_prone" if latest["departure_pct"] >= config.EXCESS_THRESHOLD else "stable"
    )
    color = p[config.ZONE_TONES[zone]]
    cluster = data.station_cluster(sel["district"], sel["taluk"], sel["hobli"])
    regime = cluster["cluster_name"] if cluster is not None else "\u2014"
    flagged = (sel["district"], sel["taluk"], sel["hobli"]) in data.suspect_keys
    flag = (
        '<span class="v-chip v-chip--amber" style="margin-top:.45rem;font-size:.54rem">flagged normal</span>'
        if flagged
        else ""
    )
    return f"""
    <div class="v-glance">
      <div class="v-glance__name">{ui.esc(sel['hobli'])}</div>
      <div class="v-glance__row"><span>Latest season</span><b>{int(latest['year'])}</b></div>
      <div class="v-glance__row"><span>Departure</span><b style="color:{color}">{latest['departure_pct']:+.1f}%</b></div>
      <div class="v-glance__row"><span>Observed</span><b>{latest['actual_mm']:,.1f} mm</b></div>
      <div class="v-glance__row"><span>Normal</span><b>{latest['normal_mm']:,.1f} mm</b></div>
      <div class="v-glance__foot">{ui.esc(regime)}</div>
      {flag}
    </div>
    """


# ---------------------------------------------------------------- loading ---
try:
    with st.spinner("Loading Varuna datasets"):
        data = load_data()
except DataUnavailable as exc:
    st.markdown(
        ui.page_header(
            "VARUNA \u00b7 system state",
            "Pipeline artifacts unavailable",
            "The interface is running, but the analysis cannot start without the prepared datasets.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        ui.callout("terra", "Missing inputs", ui.paragraph(ui.esc(exc))),
        unsafe_allow_html=True,
    )
    st.markdown(
        ui.paragraph(
            "Run <code>python src/clean_data.py</code>, then <code>python src/features.py</code>, "
            "<code>python src/train_models.py</code> and <code>python src/export_cluster_labels.py</code> "
            "to regenerate the artifacts."
        ),
        unsafe_allow_html=True,
    )
    st.stop()
except Exception as exc:  # unreadable artifact
    st.markdown(
        ui.page_header(
            "VARUNA \u00b7 system state",
            "Dataset read failed",
            "A required file exists but could not be read as expected.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        ui.callout("terra", "Read error", ui.paragraph(ui.esc(exc))),
        unsafe_allow_html=True,
    )
    st.stop()


# ----------------------------------------------------------------- sidebar --
with st.sidebar:
    st.markdown(brand_block(), unsafe_allow_html=True)

    with st.container(key="varuna-nav"):
        for page in MODULES:
            active = module_state() == page["slug"]
            clicked = st.button(
                f"{page['index']}\u2003{page['label']}",
                key=f"nav-{page['slug']}",
                type="primary" if active else "secondary",
                width="stretch",
            )
            if clicked and not active:
                set_module(page["slug"])

    st.markdown('<div class="v-side-label"><span>Station selector</span><span>Global</span></div>', unsafe_allow_html=True)
    district_options = sorted(data.clean["district"].unique())
    district = st.selectbox("District", district_options, index=0)
    taluk_options = sorted(
        data.clean[data.clean["district"] == district]["taluk"].unique()
    )
    taluk = st.selectbox("Taluk", taluk_options, index=0)
    hobli_options = sorted(
        data.clean[
            (data.clean["district"] == district) & (data.clean["taluk"] == taluk)
        ]["hobli"].unique()
    )
    hobli_name = st.selectbox("Hobli", hobli_options, index=0)

    selection = {"district": district, "taluk": taluk, "hobli": hobli_name}
    st.markdown(station_glance(data, selection), unsafe_allow_html=True)

    st.markdown('<div class="v-side-label"><span>Appearance</span><span>Theme</span></div>', unsafe_allow_html=True)
    with st.container(key="varuna-theme"):
        day_col, night_col = st.columns(2, gap="small")
        with day_col:
            if st.button(
                "Daylight",
                key="theme-light",
                type="primary" if theme_name == "light" else "secondary",
                width="stretch",
            ) and theme_name != "light":
                switch_theme("light")
        with night_col:
            if st.button(
                "Night watch",
                key="theme-dark",
                type="primary" if theme_name == "dark" else "secondary",
                width="stretch",
            ) and theme_name != "dark":
                switch_theme("dark")

    st.markdown(
        f"""
        <div class="v-side-note">
          PANEL<br/>
          2020 &middot; 2021 &middot; 2022 &middot; 2024 &middot; 2025<br/>
          2023 has no hobli-level KSNDMC publication.<br/><br/>
          {config.CLEANING_TOTALS['clean']:,} clean station-years &middot; {config.NORMALIZATION_FACTS['canonical']} canonical stations<br/>
          31 districts &middot; ODC-BY
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------- page --
slug = module_state()
page = next(m for m in MODULES if m["slug"] == slug)
position = "00" if slug == "overview" else f"{page['index']} / 05"

st.markdown(
    f"""
    <div class="v-topbar">
      <span>VARUNA &middot; meteorological intelligence</span>
      <span>{ui.esc(position)} &middot; {ui.esc(page['label'])}</span>
      <span>{'Night watch' if theme_name == 'dark' else 'Daylight'} reading</span>
    </div>
    """,
    unsafe_allow_html=True,
)

RENDERERS[slug](data, selection, p)

st.markdown(ui.footer(theme_name), unsafe_allow_html=True)
