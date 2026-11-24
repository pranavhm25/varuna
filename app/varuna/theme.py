"""
app/varuna/theme.py
===================
Design tokens, theme CSS and Plotly chart theming.

Two independently designed themes share one token contract:
  light  -- an archival scientific publication on warm paper
  dark   -- a night-shift meteorological control room
"""

from __future__ import annotations

from string import Template

# The landing page's type system: Geist for everything, Geist Mono for labels.
# The display face is aliased onto the serif token so the existing component CSS
# inherits it without every rule being rewritten.
SANS = '"Geist", "Segoe UI Variable Text", "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif'
SERIF = SANS
MONO = '"Geist Mono", "Cascadia Mono", "SFMono-Regular", Consolas, "Liberation Mono", monospace'

PALETTES = {
    "light": {
        "bg": "#F2EEE4",
        "bg_alt": "#E9E3D5",
        "surface": "#FAF8F1",
        "surface_2": "#E6E0D2",
        "ink": "#12232A",
        "ink_soft": "#33474E",
        "muted": "#55656B",
        "line": "#D8D1C0",
        "line_strong": "#9E947F",
        "rain": "#2A6584",
        "rain_deep": "#1B4A61",
        "teal": "#2C6B62",
        "green": "#4A754F",
        "amber": "#9A742F",
        "terra": "#A04E38",
        "grid": "#E1DAC9",
        "heat_zero": "#EDE7D8",
        "tint_terra": "rgba(160, 78, 56, 0.075)",
        "tint_rain": "rgba(42, 101, 132, 0.075)",
        "tint_amber": "rgba(154, 116, 47, 0.10)",
        "tint_ink": "rgba(18, 35, 42, 0.045)",
        "tint_green": "rgba(74, 117, 79, 0.08)",
        "band_terra": "rgba(160, 78, 56, 0.16)",
        "band_green": "rgba(74, 117, 79, 0.16)",
        "band_rain": "rgba(42, 101, 132, 0.16)",
        "shadow": "rgba(18, 35, 42, 0.10)",
        "mode_label": "Daylight",
    },
    "dark": {
        "bg": "#000000",
        "bg_alt": "#0A0A0A",
        "surface": "#101010",
        "surface_2": "#181818",
        "ink": "#FFFFFF",
        "ink_soft": "#C4C4C4",
        "muted": "#9B9B9B",
        "line": "#212121",
        "line_strong": "#313131",
        "rain": "#8FB4CE",
        "rain_deep": "#C2DAE8",
        "teal": "#86AFA8",
        "green": "#93B69A",
        "amber": "#D2A75F",
        "terra": "#D79A7B",
        "grid": "#161616",
        "heat_zero": "#0E0E0E",
        "tint_terra": "rgba(215, 154, 123, 0.11)",
        "tint_rain": "rgba(143, 180, 206, 0.10)",
        "tint_amber": "rgba(210, 167, 95, 0.11)",
        "tint_ink": "rgba(255, 255, 255, 0.05)",
        "tint_green": "rgba(147, 182, 154, 0.10)",
        "band_terra": "rgba(215, 154, 123, 0.20)",
        "band_green": "rgba(147, 182, 154, 0.20)",
        "band_rain": "rgba(143, 180, 206, 0.20)",
        "shadow": "rgba(0, 0, 0, 0.55)",
        "mode_label": "Night watch",
    },
}


def palette(theme: str) -> dict:
    p = dict(PALETTES.get(theme, PALETTES["dark"]))
    p["name"] = theme
    p["is_dark"] = theme == "dark"
    return p


CSS = Template(
    """
@font-face {
  font-family: "Geist";
  src: url("app/static/fonts/geist.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Geist Mono";
  src: url("app/static/fonts/geist-mono.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}

:root {
  --v-bg: $bg;
  --v-bg-alt: $bg_alt;
  --v-surface: $surface;
  --v-surface-2: $surface_2;
  --v-ink: $ink;
  --v-ink-soft: $ink_soft;
  --v-muted: $muted;
  --v-line: $line;
  --v-line-strong: $line_strong;
  --v-rain: $rain;
  --v-rain-deep: $rain_deep;
  --v-teal: $teal;
  --v-green: $green;
  --v-amber: $amber;
  --v-terra: $terra;
  --v-grid: $grid;
  --v-tint-ink: $tint_ink;
  --v-tint-rain: $tint_rain;
  --v-tint-terra: $tint_terra;
  --v-tint-amber: $tint_amber;
  --v-tint-green: $tint_green;
  --v-band-terra: $band_terra;
  --v-band-green: $band_green;
  --v-band-rain: $band_rain;
  --v-serif: $serif;
  --v-sans: $sans;
  --v-mono: $mono;
}

/* ---------------------------------------------------------------- shell -- */
html, body, .stApp, [data-testid="stAppViewContainer"] {
  background-color: var(--v-bg) !important;
}
.stApp { color: var(--v-ink); font-family: var(--v-sans); }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stDecoration"], [data-testid="stAppDeployButton"], #MainMenu { display: none !important; }
footer { visibility: hidden; }
[data-testid="stMainBlockContainer"] {
  padding: 3rem 3.4rem 3.6rem 3.4rem;
  max-width: 1380px;
}
[data-testid="stSidebar"] {
  background: var(--v-bg-alt) !important;
  border-right: 1px solid var(--v-line);
}
[data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"] { background: transparent !important; }
[data-testid="stSidebarUserContent"] { padding: 1.5rem 1.15rem 2rem 1.15rem; }
[data-testid="stSidebarCollapseButton"] button { color: var(--v-muted) !important; }
[data-testid="stSidebarHeader"] { padding-bottom: 0.4rem; }

/* --------------------------------------------------------- base text ---- */
[data-testid="stMarkdownContainer"] p {
  color: var(--v-ink-soft);
  font-size: 0.925rem;
  line-height: 1.66;
}
[data-testid="stMarkdownContainer"] strong { color: var(--v-ink); font-weight: 600; }
[data-testid="stMarkdownContainer"] a { color: var(--v-rain); text-decoration: none; }
[data-testid="stMarkdownContainer"] code {
  font-family: var(--v-mono);
  font-size: 0.78rem;
  background: var(--v-tint-ink);
  color: var(--v-ink);
  padding: 0.08rem 0.3rem;
  border-radius: 8px;
}
[data-testid="stWidgetLabel"] p {
  font-family: var(--v-mono) !important;
  font-size: 0.63rem !important;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--v-muted) !important;
}
[data-testid="stCaptionContainer"] p, .stCaption p {
  font-family: var(--v-mono) !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.04em;
  color: var(--v-muted) !important;
  line-height: 1.5;
}
[data-testid="stSpinner"] p { color: var(--v-muted); font-family: var(--v-mono); font-size: 0.72rem; }
[data-testid="stSpinner"] svg { color: var(--v-rain); }

/* ------------------------------------------------------------ widgets --- */
/* React Aria widget DOM (Streamlit 1.5x+) */
[data-testid="stSelectbox"] [role="group"] {
  background-color: var(--v-surface) !important;
  border: 1px solid var(--v-line-strong) !important;
  border-radius: 2px !important;
}
[data-testid="stSelectbox"] [role="group"]:hover { border-color: var(--v-rain) !important; }
[data-testid="stSelectbox"] [role="group"]:focus-within { border-color: var(--v-rain) !important; }
[data-testid="stSelectbox"] [role="combobox"] {
  color: var(--v-ink) !important;
  background-color: transparent !important;
  font-family: var(--v-sans);
}
[data-testid="stSelectbox"] [role="combobox"]::placeholder { color: var(--v-muted) !important; }
[data-testid="stSelectbox"] button { background-color: transparent !important; color: var(--v-muted) !important; }
[data-testid="stSelectbox"] svg { color: var(--v-muted) !important; }
[role="listbox"] {
  background-color: var(--v-surface) !important;
  border: 1px solid var(--v-line-strong) !important;
  border-radius: 2px !important;
}
[role="option"] {
  color: var(--v-ink-soft) !important;
  background-color: transparent !important;
  font-family: var(--v-sans);
}
[role="option"]:hover, [role="option"][aria-selected="true"] {
  background-color: var(--v-surface-2) !important;
  color: var(--v-ink) !important;
}
[data-testid="stTextInput"] div:has(> input) {
  background-color: var(--v-surface) !important;
  border: 1px solid var(--v-line-strong) !important;
  border-radius: 2px !important;
}
[data-testid="stTextInput"] div:has(> input):focus-within { border-color: var(--v-rain) !important; }
[data-testid="stTextInput"] input { color: var(--v-ink) !important; background: transparent !important; }
[data-testid="stTextInput"] input::placeholder { color: var(--v-muted) !important; }
[data-testid="stCheckbox"] label > div:first-of-type {
  background-color: var(--v-surface) !important;
  border: 1px solid var(--v-line-strong) !important;
  border-radius: 2px !important;
}
[data-testid="stCheckbox"] label[data-selected="true"] > div:first-of-type {
  border-color: var(--v-rain) !important;
  box-shadow: inset 0 0 0 1px var(--v-rain) !important;
}
[data-testid="stCheckbox"] label[data-selected="true"] > div:first-of-type polyline {
  stroke: var(--v-rain) !important;
}
[data-testid="stCheckbox"] label[data-focused="true"] > div:first-of-type {
  outline: 2px solid var(--v-rain);
  outline-offset: 2px;
}
[data-testid="stCheckbox"] p { color: var(--v-ink-soft) !important; }

/* Legacy BaseWeb widget DOM */
[data-baseweb="select"] > div {
  background-color: var(--v-surface) !important;
  border-color: var(--v-line-strong) !important;
  border-radius: 2px !important;
  color: var(--v-ink) !important;
  font-family: var(--v-sans);
  font-size: 0.86rem;
  min-height: 38px;
}
[data-baseweb="select"] > div:hover { border-color: var(--v-rain) !important; }
[data-baseweb="select"] input, [data-baseweb="select"] div { color: var(--v-ink); }
[data-baseweb="select"] svg { color: var(--v-muted); fill: var(--v-muted); }
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul {
  background-color: var(--v-surface) !important;
  border: 1px solid var(--v-line-strong);
}
[data-baseweb="menu"] li {
  color: var(--v-ink-soft) !important;
  background-color: transparent !important;
  font-family: var(--v-sans);
  font-size: 0.85rem;
}
[data-baseweb="menu"] li:hover, [data-baseweb="menu"] li[aria-selected="true"] {
  background-color: var(--v-surface-2) !important;
  color: var(--v-ink) !important;
}
[data-baseweb="input"] {
  background-color: var(--v-surface) !important;
  border-color: var(--v-line-strong) !important;
  border-radius: 2px !important;
}
[data-baseweb="base-input"] { background-color: transparent !important; }
.stApp input { color: var(--v-ink) !important; font-family: var(--v-sans); }
.stApp input::placeholder { color: var(--v-muted) !important; }
[data-testid="stTextInput"] label p { color: var(--v-muted); }

[data-testid="stSlider"] [role="slider"] {
  background-color: var(--v-rain) !important;
  border-color: var(--v-rain) !important;
}
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] {
  background-color: var(--v-rain) !important;
  border-radius: 2px !important;
}
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] p {
  color: var(--v-bg) !important;
  font-family: var(--v-mono) !important;
  font-size: 0.68rem !important;
}
[data-testid="stSlider"] [data-testid="stSliderTickBarMin"],
[data-testid="stSlider"] [data-testid="stSliderTickBarMax"] {
  color: var(--v-muted) !important;
  font-family: var(--v-mono);
  font-size: 0.68rem;
}
[data-testid="stSlider"] [data-testid="stTickBar"] { color: var(--v-muted); }

.stButton button, .stDownloadButton button {
  font-family: var(--v-sans);
  font-size: 0.84rem;
  font-weight: 500;
  border-radius: 8px;
  box-shadow: none !important;
  border: 1px solid var(--v-line-strong);
  background: transparent;
  color: var(--v-ink-soft);
  min-height: 2.1rem;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}
.stButton button:hover, .stDownloadButton button:hover {
  border-color: var(--v-rain);
  color: var(--v-ink);
  background: var(--v-surface-2);
}
.stButton button[data-testid="stBaseButton-primary"] {
  background: var(--v-ink) !important;
  color: var(--v-bg) !important;
  border-color: var(--v-ink) !important;
}
.stButton button[data-testid="stBaseButton-primary"]:hover { background: var(--v-ink-soft) !important; border-color: var(--v-ink-soft) !important; }
.stButton button p { font-size: 0.84rem; }
.stButton button[data-testid="stBaseButton-primary"] p { color: var(--v-bg) !important; }

/* --------------------------------------------------------------- nav ---- */
.st-key-varuna-nav div[data-testid="stVerticalBlock"] { gap: 0.1rem !important; }
.st-key-varuna-nav .stButton button {
  width: 100%;
  justify-content: flex-start;
  border: 1px solid transparent;
  background: transparent;
  color: var(--v-ink-soft);
  padding: 0.44rem 0.55rem;
  font-size: 0.845rem;
  letter-spacing: 0.005em;
  text-align: left;
}
.st-key-varuna-nav .stButton button p { font-size: 0.845rem; }
.st-key-varuna-nav .stButton button:hover {
  background: var(--v-surface);
  border-color: var(--v-line);
  color: var(--v-ink);
}
.st-key-varuna-nav .stButton button[data-testid="stBaseButton-primary"] {
  background: var(--v-ink) !important;
  color: var(--v-bg) !important;
  border-color: var(--v-ink) !important;
}
.st-key-varuna-nav .stButton button[data-testid="stBaseButton-primary"] p { color: var(--v-bg) !important; }
.st-key-varuna-theme div[data-testid="stVerticalBlock"] { gap: 0.25rem !important; }
.st-key-varuna-theme .stButton button { padding: 0.28rem 0.5rem; font-size: 0.7rem; min-height: 1.9rem; }
.st-key-varuna-theme .stButton button p { font-size: 0.7rem; }

[data-testid="stExpander"] details {
  border: 1px solid var(--v-line) !important;
  border-radius: 2px !important;
  background: var(--v-surface) !important;
}
[data-testid="stExpander"] summary { padding: 0.5rem 0.8rem; }
[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] p,
[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] span {
  font-family: var(--v-mono);
  font-size: 0.66rem;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: var(--v-muted) !important;
}
[data-testid="stExpander"] summary svg { color: var(--v-muted); fill: var(--v-muted); }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] { padding: 0.2rem 0.9rem 0.7rem 0.9rem; }

[data-testid="stVerticalBlockBorderWrapper"] {
  border-color: var(--v-line) !important;
  border-radius: 2px !important;
  background: var(--v-surface);
}

.v-topbar {
  display: flex; flex-wrap: wrap; gap: 0.4rem 1.4rem; justify-content: space-between;
  font-family: var(--v-mono); font-size: 0.58rem; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--v-muted); margin-bottom: 1.5rem;
}

/* ---------------------------------------------------------- page head --- */
.v-page { border-bottom: 1px solid var(--v-line-strong); padding-bottom: 1.5rem; margin-bottom: 1.6rem; animation: v-rise 0.3s ease both; }
.v-page__grid { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr); gap: 2rem; align-items: end; }
.v-kicker { font-family: var(--v-mono); font-size: 0.66rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--v-muted); }
.v-page h1 {
  font-family: var(--v-sans);
  font-weight: 600;
  font-size: clamp(2.05rem, 3.4vw, 3.15rem);
  line-height: 1.02;
  letter-spacing: -0.03em;
  margin: 0.55rem 0 0.6rem 0;
  color: var(--v-ink);
}
.v-lede { max-width: 64ch; margin: 0; color: var(--v-ink-soft); font-size: 0.96rem; line-height: 1.6; }
.v-meta { margin: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem 1.4rem; }
.v-meta div { min-width: 0; }
.v-meta dt { font-family: var(--v-mono); font-size: 0.6rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--v-muted); }
.v-meta dd { margin: 0.16rem 0 0 0; font-size: 0.84rem; color: var(--v-ink); line-height: 1.35; }

/* ------------------------------------------------------------ section --- */
.v-section { display: flex; align-items: baseline; gap: 0.75rem; margin: 2.4rem 0 0.9rem 0; border-top: 1px solid var(--v-line); padding-top: 0.75rem; }
.v-section__no { font-family: var(--v-mono); font-size: 0.62rem; letter-spacing: 0.1em; color: var(--v-muted); border: 1px solid var(--v-line-strong); padding: 0.1rem 0.32rem; }
.v-section h2 { font-family: var(--v-sans); font-size: 1.24rem; font-weight: 600; letter-spacing: -0.02em; margin: 0; color: var(--v-ink); line-height: 1.2; }
.v-section__note { margin-left: auto; font-family: var(--v-mono); font-size: 0.62rem; letter-spacing: 0.08em; color: var(--v-muted); text-align: right; }
.v-sub { font-family: var(--v-mono); font-size: 0.63rem; letter-spacing: 0.13em; text-transform: uppercase; color: var(--v-muted); margin: 1.1rem 0 0.35rem 0; }

/* -------------------------------------------------------------- stats --- */
.v-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(148px, 1fr)); border-top: 1px solid var(--v-line-strong); border-bottom: 1px solid var(--v-line); margin: 0.4rem 0 0.2rem 0; }
.v-stat { padding: 0.9rem 1rem 0.95rem 0; border-right: 1px solid var(--v-line); }
.v-stat:last-child { border-right: 0; }
.v-stat__label { font-family: var(--v-mono); font-size: 0.6rem; letter-spacing: 0.13em; text-transform: uppercase; color: var(--v-muted); }
.v-stat__value { font-family: var(--v-mono); font-size: 1.62rem; line-height: 1.15; letter-spacing: -0.03em; margin-top: 0.35rem; color: var(--v-ink); font-variant-numeric: tabular-nums; }
.v-stat__unit { font-family: var(--v-mono); font-size: 0.7rem; color: var(--v-muted); margin-left: 0.15rem; letter-spacing: 0; }
.v-stat__note { font-size: 0.73rem; color: var(--v-muted); margin-top: 0.3rem; line-height: 1.4; }

/* -------------------------------------------------------------- meter --- */
.v-meter { margin: 0.5rem 0 0.2rem 0; }
.v-meter__head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.55rem; gap: 1rem; flex-wrap: wrap; }
.v-meter__reading { font-family: var(--v-mono); font-size: 1.05rem; letter-spacing: -0.01em; }
.v-meter__track { position: relative; height: 26px; border: 1px solid var(--v-line-strong); background: var(--v-surface); overflow: visible; }
.v-meter__band { position: absolute; top: 0; bottom: 0; opacity: 0.9; }
.v-meter__band--deficit { background: var(--v-band-terra); }
.v-meter__band--stable { background: var(--v-band-green); }
.v-meter__band--excess { background: var(--v-band-rain); }
.v-meter__zero { position: absolute; top: -4px; bottom: -4px; width: 1px; background: var(--v-line-strong); }
.v-meter__marker { position: absolute; top: -7px; bottom: -7px; width: 2px; background: var(--v-ink); transition: left 0.35s ease; }
.v-meter__marker::after { content: ""; position: absolute; left: -4px; top: -4px; width: 10px; height: 10px; background: var(--v-ink); border-radius: 50%; }
.v-meter__value { position: absolute; top: -1.55rem; left: 50%; transform: translateX(-50%); font-family: var(--v-mono); font-size: 0.7rem; white-space: nowrap; color: var(--v-ink); background: var(--v-bg); padding: 0 0.25rem; }
.v-meter__axis { position: relative; height: 1.05rem; margin-top: 0.4rem; font-family: var(--v-mono); font-size: 0.62rem; color: var(--v-muted); }
.v-meter__tick { position: absolute; top: 0; transform: translateX(-50%); white-space: nowrap; }
.v-meter__tick--first { transform: translateX(0); }
.v-meter__tick--last { transform: translateX(-100%); }
.v-meter__legend { display: flex; flex-wrap: wrap; gap: 1.2rem; margin-top: 0.65rem; font-family: var(--v-mono); font-size: 0.63rem; color: var(--v-muted); }
.v-meter__legend i { display: inline-block; width: 0.55rem; height: 0.55rem; margin-right: 0.35rem; vertical-align: -1px; }

/* --------------------------------------------------------- probability -- */
.v-probs { display: grid; gap: 0.65rem; margin-top: 0.3rem; }
.v-prob__head { display: flex; justify-content: space-between; font-family: var(--v-mono); font-size: 0.68rem; letter-spacing: 0.05em; color: var(--v-ink-soft); }
.v-prob__head b { font-weight: 600; color: var(--v-ink); }
.v-prob__track { height: 7px; background: var(--v-tint-ink); margin-top: 0.25rem; }
.v-prob__fill { height: 100%; transition: width 0.4s ease; }

/* ------------------------------------------------------------- chips ---- */
.v-chip { display: inline-flex; align-items: center; gap: 0.35rem; font-family: var(--v-mono); font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 0.12rem 0.45rem; border: 1px solid currentColor; border-radius: 4px; white-space: nowrap; line-height: 1.5; }
.v-chip--terra { color: var(--v-terra); }
.v-chip--green { color: var(--v-green); }
.v-chip--rain { color: var(--v-rain); }
.v-chip--amber { color: var(--v-amber); }
.v-chip--neutral { color: var(--v-muted); }
.v-chip--solid { background: currentColor; }
.v-chip--solid span { color: var(--v-bg); }

/* ------------------------------------------------------------- tables --- */
.v-table-wrap { border-top: 1px solid var(--v-line-strong); border-bottom: 1px solid var(--v-line); overflow: auto; max-height: 520px; }
.v-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.v-table caption { caption-side: top; text-align: left; font-family: var(--v-mono); font-size: 0.63rem; letter-spacing: 0.08em; color: var(--v-muted); padding: 0 0 0.4rem 0; }
.v-table th { position: sticky; top: 0; z-index: 2; background: var(--v-bg); font-family: var(--v-mono); font-size: 0.6rem; letter-spacing: 0.11em; text-transform: uppercase; color: var(--v-muted); text-align: left; font-weight: 500; padding: 0.5rem 0.7rem; border-bottom: 1px solid var(--v-line-strong); }
.v-table td { padding: 0.46rem 0.55rem; border-bottom: 1px solid var(--v-line); color: var(--v-ink-soft); vertical-align: middle; }
.v-table tbody tr:hover td { background: var(--v-surface); }
.v-table tbody tr:last-child td { border-bottom: 0; }
.v-table .r { text-align: right; }
.v-table .c { text-align: center; }
.v-num { font-family: var(--v-mono); font-variant-numeric: tabular-nums; font-size: 0.78rem; color: var(--v-ink); }
.v-mono { font-family: var(--v-mono); font-size: 0.78rem; }
.v-dim { color: var(--v-muted); }
.v-rowkey { color: var(--v-ink); font-weight: 500; }
.v-table__scroll { font-family: var(--v-mono); font-size: 0.62rem; color: var(--v-muted); padding-top: 0.4rem; letter-spacing: 0.05em; }

/* ------------------------------------------------------------ callout --- */
.v-callout { display: grid; grid-template-columns: 3px 1fr; gap: 0.9rem; background: var(--v-surface); border: 1px solid var(--v-line); border-radius: 12px; padding: 0.9rem 1.05rem 0.9rem 0.9rem; margin: 1rem 0; }
.v-callout__bar { background: var(--v-muted); }
.v-callout--amber .v-callout__bar { background: var(--v-amber); }
.v-callout--terra .v-callout__bar { background: var(--v-terra); }
.v-callout--rain .v-callout__bar { background: var(--v-rain); }
.v-callout--green .v-callout__bar { background: var(--v-green); }
.v-callout__title { font-family: var(--v-mono); font-size: 0.63rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--v-ink); margin-bottom: 0.25rem; }
.v-callout p { margin: 0; font-size: 0.845rem; color: var(--v-ink-soft); line-height: 1.6; }
.v-callout p + p { margin-top: 0.45rem; }

/* -------------------------------------------------------------- empty --- */
.v-empty { border: 1px dashed var(--v-line-strong); padding: 1.4rem 1.1rem; color: var(--v-muted); font-family: var(--v-mono); font-size: 0.72rem; letter-spacing: 0.04em; }

/* ----------------------------------------------------------- findings --- */
.v-findings { display: grid; gap: 0; border-top: 1px solid var(--v-line-strong); }
.v-finding { display: grid; grid-template-columns: 2.2rem 1fr; gap: 0.8rem; padding: 0.85rem 0; border-bottom: 1px solid var(--v-line); }
.v-finding__no { font-family: var(--v-mono); font-size: 0.66rem; color: var(--v-muted); padding-top: 0.15rem; }
.v-finding h3 { font-family: var(--v-sans); font-size: 0.9rem; font-weight: 600; margin: 0 0 0.2rem 0; color: var(--v-ink); letter-spacing: 0; }
.v-finding p { margin: 0; font-size: 0.845rem; color: var(--v-ink-soft); line-height: 1.6; }

/* --------------------------------------------------------------- flow --- */
.v-flow { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: stretch; margin: 0.4rem 0 0.2rem 0; }
.v-flow__node { flex: 1 1 170px; border: 1px solid var(--v-line); border-radius: 12px; background: var(--v-surface); padding: 0.85rem 0.9rem; position: relative; min-width: 0; }
.v-flow__node--final { border-color: var(--v-rain); background: var(--v-tint-rain); }
.v-flow__label { font-family: var(--v-mono); font-size: 0.58rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--v-muted); }
.v-flow__value { font-family: var(--v-mono); font-size: 1.35rem; color: var(--v-ink); letter-spacing: -0.02em; margin-top: 0.25rem; }
.v-flow__desc { font-size: 0.75rem; color: var(--v-muted); line-height: 1.45; margin-top: 0.2rem; }
.v-flow__arrow { align-self: center; color: var(--v-line-strong); font-family: var(--v-mono); font-size: 0.9rem; padding: 0 0.15rem; }

/* -------------------------------------------------------------- tiles --- */
.v-tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); border-top: 1px solid var(--v-line-strong); border-left: 1px solid var(--v-line); margin-top: 0.5rem; }
.v-tile { border-right: 1px solid var(--v-line); border-bottom: 1px solid var(--v-line); border-radius: 12px; padding: 1.05rem 1.1rem 1.15rem 1.1rem; background: var(--v-surface); min-width: 0; }
.v-tile__head { display: flex; align-items: center; flex-wrap: wrap; gap: 0.35rem 0.5rem; margin-bottom: 0.55rem; }
.v-tile__head .v-chip { white-space: normal; }
.v-tile__head > span:last-child { margin-left: auto; }
.v-glyph { width: 15px; height: 15px; flex: 0 0 15px; }
.v-tile__cid { font-family: var(--v-mono); font-size: 0.6rem; letter-spacing: 0.12em; color: var(--v-muted); }
.v-tile__name { font-family: var(--v-serif); font-size: 1.02rem; line-height: 1.25; margin: 0.2rem 0 0.4rem 0; color: var(--v-ink); font-weight: 600; }
.v-tile__desc { font-size: 0.76rem; color: var(--v-muted); line-height: 1.5; min-height: 3.2em; }
.v-tile__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.55rem 0.8rem; margin-top: 0.7rem; padding-top: 0.7rem; border-top: 1px dashed var(--v-line); }
.v-tile__metric span { display: block; font-family: var(--v-mono); font-size: 0.57rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--v-muted); }
.v-tile__metric b { font-family: var(--v-mono); font-size: 0.85rem; font-weight: 500; color: var(--v-ink); }

/* ------------------------------------------------------------ dossier --- */
.v-dossier { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr); gap: 1.6rem; align-items: start; }
.v-crumb { font-family: var(--v-mono); font-size: 0.63rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--v-muted); }
.v-crumb b { color: var(--v-ink); font-weight: 500; }
.v-dossier h2 { font-family: var(--v-sans); font-size: clamp(1.7rem, 2.6vw, 2.35rem); font-weight: 600; letter-spacing: -0.028em; margin: 0.35rem 0 0.3rem 0; color: var(--v-ink); line-height: 1.05; }
.v-dossier__sub { font-size: 0.85rem; color: var(--v-muted); }
.v-verdict { border: 1px solid var(--v-line); border-radius: 12px; background: var(--v-surface); padding: 1rem 1.05rem; }
.v-verdict__label { font-family: var(--v-mono); font-size: 0.6rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--v-muted); }
.v-verdict__value { font-family: var(--v-serif); font-size: 1.5rem; font-weight: 600; line-height: 1.1; margin: 0.25rem 0 0.3rem 0; }
.v-verdict__meta { display: flex; justify-content: space-between; gap: 0.7rem; font-family: var(--v-mono); font-size: 0.66rem; color: var(--v-muted); }
.v-verdict__big { font-family: var(--v-mono); font-size: 2.1rem; letter-spacing: -0.03em; line-height: 1; }

/* ------------------------------------------------------------- lists ---- */
.v-deflist { border-top: 1px solid var(--v-line); margin: 0.4rem 0 0 0; }
.v-deflist div { display: flex; justify-content: space-between; gap: 1rem; padding: 0.4rem 0; border-bottom: 1px solid var(--v-line); font-size: 0.8rem; }
.v-deflist dt { color: var(--v-muted); }
.v-deflist dd { margin: 0; font-family: var(--v-mono); font-size: 0.76rem; color: var(--v-ink); text-align: right; }

/* -------------------------------------------------------------- brand --- */
.v-brand { padding-bottom: 1.1rem; border-bottom: 1px solid var(--v-line); margin-bottom: 0.9rem; }
.v-brand__row { display: flex; align-items: center; gap: 0.55rem; }
.v-brand__name { font-family: var(--v-sans); font-size: 1.28rem; letter-spacing: 0.24em; font-weight: 600; color: var(--v-ink); line-height: 1; }
.v-brand__meta { font-family: var(--v-mono); font-size: 0.55rem; letter-spacing: 0.13em; text-transform: uppercase; color: var(--v-muted); margin-top: 0.42rem; line-height: 1.6; }
.v-side-label { font-family: var(--v-mono); font-size: 0.58rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--v-muted); margin: 1.35rem 0 0.45rem 0; display: flex; justify-content: space-between; border-top: 1px solid var(--v-line); padding-top: 0.7rem; }
.v-side-note { font-family: var(--v-mono); font-size: 0.6rem; color: var(--v-muted); line-height: 1.7; letter-spacing: 0.02em; margin-top: 0.9rem; border-top: 1px solid var(--v-line); padding-top: 0.7rem; }
.v-glance { border: 1px solid var(--v-line); border-radius: 12px; background: var(--v-surface); padding: 0.75rem 0.85rem; margin-top: 0.9rem; }
.v-glance__name { font-family: var(--v-serif); font-size: 1rem; color: var(--v-ink); line-height: 1.2; }
.v-glance__row { display: flex; justify-content: space-between; font-family: var(--v-mono); font-size: 0.65rem; color: var(--v-muted); margin-top: 0.3rem; gap: 0.5rem; }
.v-glance__row b { color: var(--v-ink); font-weight: 500; }
.v-glance__foot { font-size: 0.7rem; color: var(--v-muted); margin-top: 0.5rem; padding-top: 0.45rem; border-top: 1px dashed var(--v-line); line-height: 1.45; }

/* ------------------------------------------------------------- footer --- */
.v-foot { border-top: 1px solid var(--v-line-strong); margin-top: 3rem; padding-top: 0.9rem; display: flex; flex-wrap: wrap; gap: 0.6rem 1.6rem; justify-content: space-between; font-family: var(--v-mono); font-size: 0.61rem; letter-spacing: 0.05em; color: var(--v-muted); }
.v-foot b { color: var(--v-ink-soft); font-weight: 500; letter-spacing: 0.14em; }

/* -------------------------------------------------------------- cover --- */
.v-cover { padding-bottom: 0.4rem; margin-bottom: 0.6rem; animation: v-rise 0.35s ease both; }
.v-cover__grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.04fr); gap: 3.2rem; align-items: center; }
.v-cover__kicker { display: flex; align-items: center; gap: 0.5rem; font-family: var(--v-mono); font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--v-muted); }
.v-cover__dot { width: 5px; height: 5px; border-radius: 50%; background: var(--v-rain); display: inline-block; }
.v-cover h1 { font-family: var(--v-sans); font-weight: 600; font-size: clamp(2.2rem, 4.2vw, 3.85rem); line-height: 1.02; letter-spacing: -0.035em; margin: 1.05rem 0 1.1rem 0; color: var(--v-ink); max-width: 16ch; }
.v-cover__lead { max-width: 48ch; margin: 0 0 1.6rem 0; color: var(--v-ink-soft); font-size: 0.98rem; line-height: 1.62; }
.v-cover__counts { display: flex; flex-wrap: wrap; gap: 0.55rem 1.5rem; font-family: var(--v-mono); font-size: 0.62rem; letter-spacing: 0.06em; color: var(--v-muted); }
.v-cover__counts b { color: var(--v-ink); font-weight: 500; }
.v-field { border: 1px solid var(--v-line); border-radius: 12px; background: var(--v-surface); padding: 1.15rem 1.15rem 0.95rem 1.15rem; }
.v-field svg { display: block; width: 100%; height: auto; }
.v-field__caption { margin-top: 0.9rem; font-size: 0.74rem; line-height: 1.55; color: var(--v-muted); }
.v-field__caption b { color: var(--v-ink-soft); font-weight: 500; }
.st-key-cover-actions { margin-top: 0.9rem; }
.st-key-cover-actions .stButton button { min-height: 2.5rem; padding: 0 1.05rem; }
.st-key-cover-actions .stButton button[data-testid="stBaseButton-primary"] { font-weight: 500; }

/* --------------------------------------------------------- responsive --- */
@media (max-width: 1024px) {
  [data-testid="stMainBlockContainer"] { padding: 2rem 1.5rem 2.6rem 1.5rem; }
  .v-page__grid { grid-template-columns: 1fr; gap: 1.2rem; }
  .v-cover__grid { grid-template-columns: 1fr; gap: 1.8rem; }
  .v-dossier { grid-template-columns: 1fr; gap: 1rem; }
  [data-testid="stMain"] [data-testid="stHorizontalBlock"] {
    flex-direction: column !important;
    align-items: stretch !important;
  }
  [data-testid="stMain"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: 100% !important;
    flex: 1 1 auto !important;
    min-width: 0 !important;
  }
}
@media (max-width: 720px) {
  [data-testid="stMainBlockContainer"] { padding: 3.1rem 1rem 2.2rem 1rem; }
  .v-page h1 { font-size: 1.95rem; }
  .v-lede { font-size: 0.9rem; }
  .v-meta { grid-template-columns: 1fr 1fr; gap: 0.6rem 1rem; }
  .v-section { flex-wrap: wrap; }
  .v-section__note { margin-left: 0; width: 100%; text-align: left; }
  .v-stat { padding-right: 0.6rem; }
  .v-stat__value { font-size: 1.35rem; }
  .v-tiles { grid-template-columns: 1fr; }
  .v-flow__node { flex-basis: 100%; }
  .v-flow__arrow { display: none; }
  .v-dossier h2 { font-size: 1.6rem; }
  .v-table { font-size: 0.78rem; }
  .v-table th, .v-table td { padding: 0.42rem 0.5rem; }
}

@keyframes v-rise {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }
}
"""
)


def css_for(theme: str) -> str:
    p = palette(theme)
    return CSS.substitute(
        serif=SERIF,
        sans=SANS,
        mono=MONO,
        **{k: v for k, v in p.items() if k not in ("name", "is_dark", "mode_label")},
    )


# ------------------------------------------------------------------ charts --
def style_figure(fig, p, height=320, legend=True, x_grid=False, y_grid=True, margin=None):
    """Apply the Varuna chart grammar to a Plotly figure."""
    margin = margin or dict(l=8, r=10, t=58 if legend else 12, b=6)
    fig.update_layout(
        height=height,
        margin=margin,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=MONO, size=10, color=p["muted"]),
        hoverlabel=dict(
            bgcolor=p["surface"],
            bordercolor=p["line_strong"],
            font=dict(family=MONO, size=11, color=p["ink"]),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(family=MONO, size=9.5, color=p["muted"]),
            bgcolor="rgba(0,0,0,0)",
            itemsizing="constant",
        ),
        showlegend=legend,
        hovermode="closest",
        transition=dict(duration=0),
        modebar=dict(bgcolor="rgba(0,0,0,0)", color=p["muted"], activecolor=p["ink"]),
    )
    fig.update_xaxes(
        showgrid=x_grid,
        gridcolor=p["grid"],
        gridwidth=1,
        zeroline=False,
        linecolor=p["line"],
        linewidth=1,
        ticks="outside",
        ticklen=3,
        tickcolor=p["line"],
        tickfont=dict(family=MONO, size=9.5, color=p["muted"]),
        title_font=dict(family=MONO, size=9.5, color=p["muted"]),
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=y_grid,
        gridcolor=p["grid"],
        gridwidth=1,
        zeroline=False,
        linecolor=p["line"],
        linewidth=0,
        ticks="outside",
        ticklen=3,
        tickcolor=p["line"],
        tickfont=dict(family=MONO, size=9.5, color=p["muted"]),
        title_font=dict(family=MONO, size=9.5, color=p["muted"]),
        automargin=True,
    )
    return fig
