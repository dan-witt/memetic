#!/usr/bin/env python3
"""Weather-report figure: (A) rolling claim-Vendi/W over the community's own timeline against the
frozen anchor levels; (B) daily author inflow; (C) daily raw-zstd novelty vs the human band floor;
(D) daily venue share against the lemmy.world platform founding — the matched human comparator,
frozen, from results/lemmy_baseline. Panel D exists because the anchors' 0.085-0.221 band cannot
show what a human PLATFORM does: the square oscillates around lemmy's level, not far above it.
Usage: weather_figure.py <issue dir, e.g. results/weather/2026-08-11>"""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(sys.argv[1] if len(sys.argv) > 1 else "results/weather/2026-08-11")
d = json.load(open(R / "results.json"))

SURFACE = "#fcfcfb"; INK = "#0b0b0b"; MUTED = "#898781"; GRID = "#e1e0d9"; BASE = "#c3c2b7"
C_MAIN = "#2a78d6"; C_ANCHOR = "#898781"; C_BAR = "#c3c2b7"

_alloc = (d.get("allocation_trend") or {}).get("venue_share_per_day_qwen_binary")
# Issue #8 adopted a corrected parse and publishes both series; when both are present the panel
# draws both, because the whole point of the correction is that it moves BOTH sides of the
# comparison and the reader should see the shortfall as it stands under either currency.
_alloc_c = (d.get("allocation_trend") or {}).get("venue_share_per_day_corrected_parse")
_lem = ((d.get("allocation_trend") or {}).get("lemmy_reference") or {}).get("platform_qwen")
_lem_c = ((d.get("allocation_trend") or {}).get("lemmy_comparator_corrected") or {}
          ).get("platform_qwen_corrected")
_axes = 4 if _alloc else 3
fig, axs = plt.subplots(1, _axes, figsize=(12.5 if _axes == 3 else 16.0, 4.0), dpi=200,
                        gridspec_kw={"width_ratios": [1.6, 1, 1] + ([1.25] if _axes == 4 else [])})
ax1, ax2, ax3 = axs[0], axs[1], axs[2]
ax4 = axs[3] if _axes == 4 else None
fig.set_facecolor(SURFACE)
for ax in axs:
    ax.set_facecolor(SURFACE); ax.grid(True, color=GRID, linewidth=.7, axis="y")
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("bottom", "left"): ax.spines[sp].set_color(BASE)
    ax.tick_params(colors=MUTED, labelsize=8.5)

ts = d["idea_time_series"]
xs = range(len(ts["vendi_over_W"]))
ax1.plot(xs, ts["vendi_over_W"], color=C_MAIN, lw=1.8)
lv = ts["anchor_levels"]
tight = {k: v for k, v in lv.items() if k in ("lisp", "smalltalk", "scheme")}
ax1.axhspan(min(tight.values()), max(tight.values()), color=BASE, alpha=.35, lw=0)
ax1.text(0, max(tight.values()) + 0.0012, "lisp · smalltalk · scheme", color=MUTED, fontsize=7.5, va="bottom")
for name in ("forth", "sci", "hn"):
    ax1.axhline(lv[name], color=C_ANCHOR, lw=.8, ls=(0, (3, 3)), alpha=.7)
    ax1.text(1, lv[name] + 0.0012, name, color=MUTED, fontsize=7.5, va="bottom")
ticks = [i for i in xs if i % max(1, len(ts["vendi_over_W"]) // 6) == 0]
ax1.set_xticks(ticks); ax1.set_xticklabels([ts["t_utc"][i][:5] for i in ticks], fontsize=8)
ax1.set_ylabel("claim-Vendi / W (120-item windows)", color=MUTED, fontsize=8.5)
ax1.set_title("A · Idea diversity along the timeline, vs frozen anchors", loc="left", color=INK, fontsize=10)

inf = d["structure"]["inflows"]
days = list(inf)
ax2.bar(range(len(days)), [inf[k]["new_authors"] for k in days], color=C_BAR, width=.65)
ax2.set_xticks(range(len(days))); ax2.set_xticklabels(days, fontsize=8, rotation=45)
ax2.set_ylabel("new authors / day", color=MUTED, fontsize=8.5)
ax2.set_title("B · Author inflow", loc="left", color=INK, fontsize=10)

z = d["register_trend_zstd_raw"]
zd = list(z["per_day"])
ax3.plot(range(len(zd)), [z["per_day"][k] for k in zd], color=C_MAIN, lw=1.8, marker="o", ms=4)
ax3.axhline(z["band_floor"], color=C_ANCHOR, lw=1.0, ls=(0, (3, 3)))
ax3.text(len(zd) - 1, z["band_floor"], " human band floor", color=MUTED, fontsize=7.5, va="bottom", ha="right")
ax3.set_xticks(range(len(zd))); ax3.set_xticklabels(zd, fontsize=8, rotation=45)
ax3.set_ylabel("raw zstd novelty (lower = more recycling)", color=MUTED, fontsize=8.5)
ax3.set_ylim(min(z["per_day"].values()) - 0.02, z["band_floor"] + 0.02)
ax3.set_title("C · Register (surface style)", loc="left", color=INK, fontsize=10)

if ax4 is not None:
    ad = list(_alloc)
    ax4.plot(range(len(ad)), [_alloc[k] for k in ad], color=C_MAIN, lw=1.8, marker="o", ms=4,
             label="strict parse (series currency)" if _alloc_c else None)
    if _alloc_c:
        ax4.plot(range(len(ad)), [_alloc_c.get(k) for k in ad], color=C_MAIN, lw=1.2, alpha=.55,
                 ls=(0, (4, 2)), marker="o", ms=2.5, label="corrected parse")
    if _lem:
        ax4.axhline(_lem, color="#c2410c", lw=1.2, ls="--")
        ax4.text(len(ad) - 1, _lem + 0.004, "lemmy.world platform", ha="right", va="bottom",
                 color="#c2410c", fontsize=8)
    if _lem_c and _lem and abs(_lem_c - _lem) > 1e-9:
        ax4.axhline(_lem_c, color="#c2410c", lw=0.9, ls=(0, (2, 2)), alpha=.55)
    if _alloc_c:
        ax4.legend(loc="upper right", fontsize=7, frameon=False, labelcolor=MUTED)
    band = (d.get("allocation_trend") or {}).get("band_through_issue_4")
    if band:
        ax4.axhspan(band[0], band[1], color=BASE, alpha=.25, lw=0)
        ax4.text(0, band[0] - 0.006, "prior band", ha="left", va="top", color=MUTED, fontsize=8)
    ax4.set_xticks(range(len(ad))); ax4.set_xticklabels(ad, fontsize=8, rotation=45)
    ax4.set_ylabel("venue share / day (Qwen binary)", color=MUTED, fontsize=8.5)
    ax4.set_title("D · Allocation vs a human platform", loc="left", color=INK, fontsize=10)

fig.suptitle("1f916 weather · " + d["issue"].split(" (")[0], x=0.01, ha="left", color=INK,
             fontsize=11.5, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.93))
for ext in ("png", "svg"):
    fig.savefig(R / f"figure.{ext}", facecolor=SURFACE, bbox_inches="tight")
print("saved", R / "figure.png")
