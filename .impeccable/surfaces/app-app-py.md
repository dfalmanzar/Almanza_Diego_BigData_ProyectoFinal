---
version: 1
slug: "app-app-py"
primary_target: "app/app.py"
related_targets: ["app/componentes"]
---

# Dashboard Streamlit · Violencia armada

Scope: the whole Streamlit app (app/app.py and its HTML components). Visitor mode: Operate (public visitors explore data; sections required by the course guide: Resumen, Datos, Visualizaciones, Modelo, Insights y reporte). Code-led build.

User steer on the chosen card: the map must be detailed enough that each country reads on its own (it need not be ASCII); a different typeface from the sketch; a highly visual page with attractive animation that never feels flat. Pinned: black, white and red only (with grey and red variants); equal-area world map opening the page, countries coloured by deaths per 1,000 km² (UCDP), hotspots marked, year selector.

## Direction contract

THESIS: Every view is a grid specimen: the map, the figures and the charts are assembled on one visible construction grid, and the data is the proof. It refuses the stock dark dashboard of sidebar filters and rounded KPI cards.

OWN-WORLD: Ink-black ground with fine grid hairlines; white ink; a closed six-step grey ramp and a four-step red ramp, nothing else. Chakra Petch (chamfered, grid-built) for display figures and headings, Barlow (DIN-lineage grotesk) for interface text, Martian Mono (grid-built) for data. One red diagonal stroke is the only rebellion (active section, primary action, the selected period). Rules are 1 px, radius is zero, empty areas carry an offset-dot texture.

STORY: The visitor sees at once where in the world organised violence is densest per square kilometre, scrubs the years, opens a country, then crosses to the Colombia half to see how homicide changed, what the model can and cannot tell, and downloads the report.

FIRST VIEWPORT: Top bar: wordmark left, five sections right, active one underlined by the red diagonal. Below, a row of three monumental figures on the grid, the middle one on a red plane. Then the Equal Earth world map at full width, about 60 % of the viewport, every country drawn with its border and filled with a cell texture whose density and red follow its intensity; hotspots pulse. Under the map, the year rule is the period selector; the primary action (explore the data) sits at its right.

FORM: Wim Crouwel gridded type specimen (catalog challenger crouwel-grid-specimen, chosen by the user over assigned candidate 3, Informe de situación). seed: df50fd36f0c3f105. Signature interaction: the map assembles cell by cell on load, light countries first and the reddest last; moving the year rule rebuilds intensities with a cell flip; figures count up digit by digit; hotspots pulse; sections reveal as their grid lines draw in.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
