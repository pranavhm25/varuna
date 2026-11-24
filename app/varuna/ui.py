"""
app/varuna/ui.py
================
Shared HTML components for the Varuna workspace. All dynamic values pass
through `esc()`; only structure and class names are interpolated raw.
"""

from __future__ import annotations

import html
from typing import Iterable, Sequence

import streamlit as st

from .config import ZONE_LABELS, ZONE_SHORT, ZONE_TONES

GLYPHS = {
    "circle": '<circle cx="8" cy="8" r="5.4" fill="none" stroke="currentColor" stroke-width="1.6"/>'
    '<circle cx="8" cy="8" r="1.5" fill="currentColor"/>',
    "diamond": '<path d="M8 1.9 L14.1 8 L8 14.1 L1.9 8 Z" fill="none" stroke="currentColor" stroke-width="1.5"/>',
    "square": '<rect x="2.6" y="2.6" width="10.8" height="10.8" fill="none" stroke="currentColor" stroke-width="1.5"/>',
    "triangle": '<path d="M8 2.2 L14.2 13.4 L1.8 13.4 Z" fill="none" stroke="currentColor" stroke-width="1.5"/>',
}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def num(value, digits: int = 1) -> str:
    try:
        return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError):
        return "\u2014"


def signed(value, digits: int = 1, suffix: str = "") -> str:
    try:
        return f"{float(value):+,.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return "\u2014"


def tone_color(p: dict, tone: str) -> str:
    return p.get(tone, p["ink"])


def chip(label: str, tone: str = "neutral") -> str:
    return f'<span class="v-chip v-chip--{esc(tone)}">{esc(label)}</span>'


def zone_chip(zone: str, text: str | None = None) -> str:
    return chip(text or ZONE_LABELS.get(zone, zone), ZONE_TONES.get(zone, "neutral"))


def glyph(cid: int, p: dict, shape: str | None = None, size: int = 15) -> str:
    from .config import CLUSTERS

    meta = CLUSTERS.get(int(cid), CLUSTERS[2])
    body = GLYPHS[shape or meta["glyph"]]
    return (
        f'<svg class="v-glyph" width="{size}" height="{size}" viewBox="0 0 16 16" '
        f'aria-hidden="true" style="color:{tone_color(p, meta["tone"])}">{body}</svg>'
    )


def page_header(kicker: str, title: str, lede: str, meta: Sequence[tuple[str, str]] = ()) -> str:
    meta_html = "".join(
        f"<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>" for label, value in meta
    )
    meta_block = f'<dl class="v-meta">{meta_html}</dl>' if meta_html else ""
    return f"""
    <header class="v-page">
      <div class="v-page__grid">
        <div>
          <div class="v-kicker">{esc(kicker)}</div>
          <h1>{esc(title)}</h1>
          <p class="v-lede">{esc(lede)}</p>
        </div>
        {meta_block}
      </div>
    </header>
    """


def section(no: str, title: str, note: str = "") -> str:
    note_html = f'<div class="v-section__note">{esc(note)}</div>' if note else ""
    return f"""
    <div class="v-section">
      <span class="v-section__no">{esc(no)}</span>
      <h2>{esc(title)}</h2>
      {note_html}
    </div>
    """


def sub_label(text: str) -> str:
    return f'<div class="v-sub">{esc(text)}</div>'


def stat_strip(items: Iterable[dict]) -> str:
    cells = []
    for item in items:
        color = item.get("color")
        style = f' style="color:{color}"' if color else ""
        unit = (
            f'<span class="v-stat__unit">{esc(item["unit"])}</span>' if item.get("unit") else ""
        )
        note = f'<div class="v-stat__note">{esc(item["note"])}</div>' if item.get("note") else ""
        cells.append(
            f'<div class="v-stat"><div class="v-stat__label">{esc(item["label"])}</div>'
            f'<div class="v-stat__value"{style}>{esc(item["value"])}{unit}</div>{note}</div>'
        )
    return f'<div class="v-stats">{"".join(cells)}</div>'


def callout(tone: str, title: str, body_html: str) -> str:
    return f"""
    <div class="v-callout v-callout--{esc(tone)}">
      <div class="v-callout__bar"></div>
      <div>
        <div class="v-callout__title">{esc(title)}</div>
        {body_html}
      </div>
    </div>
    """


def paragraph(text: str) -> str:
    return f"<p>{text}</p>"


def empty_state(message: str) -> str:
    return f'<div class="v-empty">{esc(message)}</div>'


def findings(items: Sequence[dict | tuple[str, str]]) -> str:
    rows = []
    for i, item in enumerate(items, 1):
        if isinstance(item, dict):
            title, body = item["title"], item["body"]
        else:
            title, body = item
        rows.append(
            f'<div class="v-finding"><div class="v-finding__no">{i:02d}</div>'
            f"<div><h3>{esc(title)}</h3><p>{esc(body)}</p></div></div>"
        )
    return f'<div class="v-findings">{"".join(rows)}</div>'


def flow(stages: Sequence[tuple[str, str, str, str]]) -> str:
    """stages: (label, description, value, unit); the last node is emphasised."""
    parts = []
    for i, (label, desc, value, unit) in enumerate(stages):
        final = " v-flow__node--final" if i == len(stages) - 1 else ""
        parts.append(
            f'<div class="v-flow__node{final}">'
            f'<div class="v-flow__label">{esc(label)}</div>'
            f'<div class="v-flow__value">{esc(value)} <span style="font-size:.68rem;color:var(--v-muted)">{esc(unit)}</span></div>'
            f'<div class="v-flow__desc">{esc(desc)}</div></div>'
        )
        if i < len(stages) - 1:
            parts.append('<div class="v-flow__arrow" aria-hidden="true">\u2192</div>')
    return f'<div class="v-flow">{"".join(parts)}</div>'


def deflist(items: Sequence[tuple[str, str]]) -> str:
    rows = "".join(
        f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in items
    )
    return f'<dl class="v-deflist">{rows}</dl>'


def meter(departure: float, p: dict, zone: str) -> str:
    lo, hi = -60.0, 100.0

    def pos(value: float) -> float:
        clamped = min(max(value, lo), hi)
        return (clamped - lo) / (hi - lo) * 100.0

    marker = pos(departure)
    ticks = [(-60.0, "\u221260"), (-20.0, "\u221220"), (0.0, "0"), (40.0, "+40"), (100.0, "+100")]
    tick_html = []
    for i, (value, label) in enumerate(ticks):
        anchor = "first" if i == 0 else ("last" if i == len(ticks) - 1 else "mid")
        tick_html.append(
            f'<span class="v-meter__tick v-meter__tick--{anchor}" style="left:{pos(value):.1f}%">'
            f"{label}%</span>"
        )
    return f"""
    <div class="v-meter">
      <div class="v-meter__head">
        <div class="v-meter__reading">{signed(departure, 1, "%")} departure
          &nbsp;{zone_chip(zone)}</div>
        <div class="v-stat__label">KSNDMC reference thresholds</div>
      </div>
      <div class="v-meter__track" role="img"
           aria-label="Rainfall departure {signed(departure, 1, ' percent')} on a scale from minus 60 to plus 100 percent">
        <span class="v-meter__band v-meter__band--deficit" style="left:0%;width:{pos(-20):.1f}%"></span>
        <span class="v-meter__band v-meter__band--stable" style="left:{pos(-20):.1f}%;width:{pos(40) - pos(-20):.1f}%"></span>
        <span class="v-meter__band v-meter__band--excess" style="left:{pos(40):.1f}%;width:{100 - pos(40):.1f}%"></span>
        <span class="v-meter__zero" style="left:{pos(0):.1f}%"></span>
        <span class="v-meter__marker" style="left:{marker:.1f}%">
          <span class="v-meter__value">{signed(departure, 1, "%")}</span>
        </span>
      </div>
      <div class="v-meter__axis">{"".join(tick_html)}</div>
      <div class="v-meter__legend">
        <span><i style="background:var(--v-terra);opacity:.75"></i>Deficit \u2264 \u221220%</span>
        <span><i style="background:var(--v-green);opacity:.75"></i>Stable \u221220% to +40%</span>
        <span><i style="background:var(--v-rain);opacity:.75"></i>Excess \u2265 +40%</span>
        <span style="margin-left:auto">Departure = (actual \u2212 normal) / normal \u00d7 100</span>
      </div>
    </div>
    """


def probability_bars(probabilities: dict, p: dict) -> str:
    rows = []
    for zone in ("drought_prone", "stable", "flood_prone"):
        value = float(probabilities.get(zone, 0.0))
        color = tone_color(p, ZONE_TONES[zone])
        rows.append(
            f'<div class="v-prob"><div class="v-prob__head">'
            f"<span>{esc(ZONE_LABELS[zone])}</span><b>{value * 100:.0f}%</b></div>"
            f'<div class="v-prob__track" role="img" aria-label="{esc(ZONE_LABELS[zone])} probability {value * 100:.0f} percent">'
            f'<div class="v-prob__fill" style="width:{value * 100:.1f}%;background:{color}"></div>'
            f"</div></div>"
        )
    return f'<div class="v-probs">{"".join(rows)}</div>'


def table(
    columns: Sequence[dict],
    rows: Sequence[dict],
    caption: str | None = None,
    empty: str = "No records match the current filters.",
    foot: str | None = None,
) -> str:
    """Render a semantic table.

    columns: [{label, key, align: 'l'|'r'|'c', cls}]
    rows:    [{key: value}] where value may be a str or {"raw": html}
    """
    if not rows:
        return empty_state(empty)

    head = "".join(
        f'<th class="{"r" if c.get("align") == "r" else ("c" if c.get("align") == "c" else "")}">'
        f'{esc(c["label"])}</th>'
        for c in columns
    )
    body_rows = []
    for row in rows:
        cells = []
        for col in columns:
            value = row.get(col["key"], "")
            cls = col.get("cls", "")
            if col.get("align") == "r":
                cls = (cls + " r").strip()
            elif col.get("align") == "c":
                cls = (cls + " c").strip()
            if isinstance(value, dict) and "raw" in value:
                cell = value["raw"]
                cls = (cls + " " + value.get("cls", "")).strip()
            else:
                cell = esc(value)
            cells.append(f'<td class="{cls}">{cell}</td>')
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    caption_html = f"<caption>{esc(caption)}</caption>" if caption else ""
    foot_html = f'<div class="v-table__scroll">{esc(foot)}</div>' if foot else ""
    return (
        f'<div class="v-table-wrap"><table class="v-table">{caption_html}'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table></div>{foot_html}"
    )


def cluster_tiles(cluster_stats: dict, p: dict) -> str:
    tiles = []
    for cid in sorted(cluster_stats):
        stats = cluster_stats[cid]
        from .config import CLUSTERS

        meta = CLUSTERS[cid]
        color = tone_color(p, meta["tone"])
        tiles.append(
            f'<div class="v-tile">'
            f'<div class="v-tile__head">{glyph(cid, p)}'
            f'<span class="v-tile__cid">CLUSTER {cid}</span></div>'
            f'<h3 class="v-tile__name" style="color:{color}">{esc(meta["name"])}</h3>'
            f'<div class="v-tile__desc">{esc(meta["desc"])}</div>'
            f'<div class="v-tile__grid">'
            f'<div class="v-tile__metric"><span>Hoblis</span><b>{stats["n"]:,}</b></div>'
            f'<div class="v-tile__metric"><span>Share</span><b>{stats["share"]:.1f}%</b></div>'
            f'<div class="v-tile__metric"><span>Mean normal</span><b>{num(stats["normal"], 0)} mm</b></div>'
            f'<div class="v-tile__metric"><span>Mean departure</span><b>{signed(stats["departure"], 1, "%")}</b></div>'
            f'<div class="v-tile__metric"><span>Deficit years</span><b>{stats["deficit"]:.2f} / 5</b></div>'
            f'<div class="v-tile__metric"><span>Volatility</span><b>{num(stats["std"], 1)} pp</b></div>'
            f"</div>"
            f'<div style="margin-top:.55rem;font-family:var(--v-mono);font-size:.6rem;color:var(--v-muted);letter-spacing:.06em">'
            f'{stats["suspect"]} flagged normals in cluster</div>'
            f"</div>"
        )
    return f'<div class="v-tiles">{"".join(tiles)}</div>'


def footer(theme: str) -> str:
    return f"""
    <div class="v-foot">
      <div><b>VARUNA</b> \u00b7 Karnataka Rainfall Intelligence</div>
      <div>KSNDMC via OpenCity Karnataka \u00b7 ODC-BY / NDSAP \u00b7 850 stations \u00b7 2020\u20132025</div>
      <div>{esc("Night watch" if theme == "dark" else "Daylight")} theme \u00b7 academic ML project</div>
    </div>
    """


def render(html_block: str) -> None:
    st.markdown(html_block, unsafe_allow_html=True, anchors=False)
