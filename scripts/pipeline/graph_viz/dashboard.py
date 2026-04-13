from pathlib import Path
from typing import Any

from .io_utils import short_diagram_name

TEMPLATE_PATH = Path(__file__).with_name("dashboard_template.html")


def _read_template(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _render_link(label: str, href: str | None, cls: str = "") -> str:
    if not href:
        return f'<span class="action disabled {cls}">{label}</span>'
    return f'<a class="action {cls}" href="{href}" target="_blank" rel="noopener">{label}</a>'


def _build_card_html(row: dict[str, Any]) -> str:
    diagram_id = str(row.get("diagram_id", ""))
    short_name = short_diagram_name(diagram_id)
    suspicious = int(row.get("n_suspicious_terminal_matches", 0))
    implicit_supply = int(row.get("n_implicit_supply_nets", 0))

    suspicious_badge = (
        f'<span class="badge badge-warn">{suspicious} suspicious</span>'
        if suspicious > 0 else
        '<span class="badge badge-ok">clean</span>'
    )

    full_png_rel = f"full_png/{row['full_png']}" if row.get("full_png") else None
    full_html_rel = f"full_html/{row['full_html']}" if row.get("full_html") else None
    component_png_rel = f"component_net_png/{row['component_net_png']}" if row.get("component_net_png") else None
    component_html_rel = f"component_net_html/{row['component_net_html']}" if row.get("component_net_html") else None
    overlay_png_rel = f"overlay/{row['overlay_png']}" if row.get("overlay_png") else None
    graph_json_rel = f"downloads/graph_json/{row['graph_json']}" if row.get("graph_json") else None
    simplified_json_rel = (
        f"downloads/simplified_json/{row['simplified_json']}"
        if row.get("simplified_json") else None
    )

    preview_rel = component_png_rel or overlay_png_rel or full_png_rel
    preview_html = (
        f'<a class="preview-link" href="{preview_rel}" target="_blank" rel="noopener">'
        f'  <img class="preview" src="{preview_rel}" alt="Preview {short_name}" loading="lazy" />'
        f'</a>'
        if preview_rel else
        '<div class="preview preview-empty">No preview</div>'
    )

    return f'''<article class="diagram-card" data-name="{short_name.lower()} {diagram_id.lower()}" data-suspicious="{suspicious}">
  <div class="card-top">
    <div>
      <div class="card-title-row">
        <h2>{short_name}</h2>
        {suspicious_badge}
      </div>
      <p class="card-subtitle">{diagram_id}</p>
    </div>

      <div class="metrics-grid">
      <div class="metric"><span class="metric-value">{row.get('n_nodes_total', 0)}</span><span class="metric-label">nodes</span></div>
      <div class="metric"><span class="metric-value">{row.get('n_edges_total', 0)}</span><span class="metric-label">edges</span></div>
      <div class="metric"><span class="metric-value">{suspicious}</span><span class="metric-label">suspicious</span></div>
      <div class="metric"><span class="metric-value">{implicit_supply}</span><span class="metric-label">implicit nets</span></div>
    </div>
  </div>

  <div class="card-body">
    <div class="preview-wrap">
      {preview_html}
    </div>

    <div class="actions-wrap">
      <div class="action-group">
        <div class="group-title">Full graph</div>
        <div class="action-row">
          {_render_link('PNG', full_png_rel)}
          {_render_link('HTML', full_html_rel, 'primary')}
        </div>
      </div>

      <div class="action-group">
        <div class="group-title">Component → Net</div>
        <div class="action-row">
          {_render_link('PNG', component_png_rel)}
          {_render_link('HTML', component_html_rel, 'primary')}
        </div>
      </div>

      <div class="action-group">
        <div class="group-title">Overlay</div>
        <div class="action-row">
          {_render_link('PNG', overlay_png_rel)}
        </div>
      </div>

      <div class="action-group">
        <div class="group-title">Data</div>
        <div class="action-row">
          {_render_link('Graph JSON', graph_json_rel)}
          {_render_link('Simplified JSON', simplified_json_rel, 'primary')}
        </div>
      </div>
    </div>
  </div>
</article>
'''


def save_index_html(index_rows: list[dict[str, Any]], out_path: Path) -> None:
    rows_sorted = sorted(
        index_rows,
        key=lambda r: (
            -int(r.get("n_suspicious_terminal_matches", 0)),
            str(r.get("diagram_id", "")),
        ),
    )

    total_diagrams = len(rows_sorted)
    total_nodes = sum(int(r.get("n_nodes_total", 0)) for r in rows_sorted)
    total_edges = sum(int(r.get("n_edges_total", 0)) for r in rows_sorted)
    total_suspicious = sum(int(r.get("n_suspicious_terminal_matches", 0)) for r in rows_sorted)
    diagrams_with_suspicious = sum(
        1 for r in rows_sorted if int(r.get("n_suspicious_terminal_matches", 0)) > 0
    )

    cards_html = "\n".join(_build_card_html(row) for row in rows_sorted)

    html = _read_template(TEMPLATE_PATH)
    html = html.replace("{{TOTAL_DIAGRAMS}}", str(total_diagrams))
    html = html.replace("{{TOTAL_NODES}}", str(total_nodes))
    html = html.replace("{{TOTAL_EDGES}}", str(total_edges))
    html = html.replace("{{TOTAL_SUSPICIOUS}}", str(total_suspicious))
    html = html.replace("{{DIAGRAMS_WITH_SUSPICIOUS}}", str(diagrams_with_suspicious))
    html = html.replace("{{CARDS_HTML}}", cards_html)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
