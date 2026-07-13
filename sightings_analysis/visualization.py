from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Mapping

from .context import AnalysisContext


def _bar_chart(
    path: Path,
    *,
    title: str,
    subtitle: str,
    footer: str,
    labels: list[str],
    values: list[int],
    description: str,
) -> Path:
    width = 1000
    height = 560
    margin_left = 90
    margin_right = 40
    margin_top = 110
    margin_bottom = 90
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    maximum = max(values) if values else 1
    bar_gap = max(5, int(chart_width / max(len(values), 1) * 0.16))
    bar_width = max(
        8,
        (chart_width - bar_gap * (len(values) + 1)) / max(len(values), 1),
    )

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(description)}</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{margin_left}" y="48" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#16202a">{escape(title)}</text>',
        f'<text x="{margin_left}" y="78" font-family="Arial, sans-serif" font-size="16" fill="#536171">{escape(subtitle)}</text>',
        f'<line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{margin_left + chart_width}" y2="{margin_top + chart_height}" stroke="#98a2ad"/>',
    ]

    for index, (label, value) in enumerate(zip(labels, values, strict=True)):
        x = margin_left + bar_gap + index * (bar_width + bar_gap)
        bar_height = 0 if maximum == 0 else chart_height * value / maximum
        y = margin_top + chart_height - bar_height
        elements.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" rx="3" fill="#356a86"/>'
        )
        elements.append(
            f'<text x="{x + bar_width / 2:.2f}" y="{max(y - 8, margin_top + 12):.2f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#16202a">{value}</text>'
        )
        elements.append(
            f'<text x="{x + bar_width / 2:.2f}" y="{margin_top + chart_height + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#374151">{escape(label)}</text>'
        )

    elements.append(
        f'<text x="{margin_left}" y="{height - 24}" font-family="Arial, sans-serif" font-size="13" fill="#6b7280">{escape(footer)}</text>'
    )
    elements.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(elements) + "\n", encoding="utf-8")
    return path


def _horizontal_bar_chart(
    path: Path,
    *,
    title: str,
    subtitle: str,
    footer: str,
    labels: list[str],
    values: list[int],
    description: str,
) -> Path:
    width = 1000
    row_height = 34
    height = max(500, 150 + row_height * len(labels))
    margin_left = 180
    margin_right = 80
    margin_top = 110
    margin_bottom = 60
    chart_width = width - margin_left - margin_right
    maximum = max(values) if values else 1

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(description)}</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="70" y="48" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#16202a">{escape(title)}</text>',
        f'<text x="70" y="78" font-family="Arial, sans-serif" font-size="16" fill="#536171">{escape(subtitle)}</text>',
    ]
    for index, (label, value) in enumerate(zip(labels, values, strict=True)):
        y = margin_top + index * row_height
        length = 0 if maximum == 0 else chart_width * value / maximum
        elements.extend(
            [
                f'<text x="{margin_left - 14}" y="{y + 20}" text-anchor="end" font-family="Arial, sans-serif" font-size="13" fill="#374151">{escape(label)}</text>',
                f'<rect x="{margin_left}" y="{y + 5}" width="{length:.2f}" height="22" rx="3" fill="#356a86"/>',
                f'<text x="{min(margin_left + length + 8, width - 50):.2f}" y="{y + 21}" font-family="Arial, sans-serif" font-size="12" fill="#16202a">{value}</text>',
            ]
        )
    elements.append(
        f'<text x="70" y="{height - 22}" font-family="Arial, sans-serif" font-size="13" fill="#6b7280">{escape(footer)}</text>'
    )
    elements.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(elements) + "\n", encoding="utf-8")
    return path


def _sample_flow_chart(
    path: Path,
    *,
    input_rows: int,
    delay_rows: int,
    flagged_rows: int,
    context: AnalysisContext,
) -> Path:
    width, height = 1000, 400
    boxes = [
        (70, "Input", input_rows, f"All {context.short_label} reports"),
        (370, "General analysis", input_rows, "Rows retained"),
        (
            670,
            "Delay analysis",
            delay_rows,
            f"{flagged_rows} calendar-order flags excluded",
        ),
    ]
    items = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Reported sightings sample flow</title>',
        '<desc id="desc">A flow diagram showing that all records are retained for general analysis while calendar-order warnings are excluded only from reporting-delay statistics.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="70" y="55" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#16202a">Reported Sightings Sample Flow</text>',
        f'<text x="70" y="84" font-family="Arial, sans-serif" font-size="16" fill="#536171">{escape(context.dataset_label)} • every material sample change is disclosed</text>',
    ]
    for index, (x, title, count, note) in enumerate(boxes):
        items.extend(
            [
                f'<rect x="{x}" y="145" width="240" height="135" rx="12" fill="#eef4f7" stroke="#356a86" stroke-width="2"/>',
                f'<text x="{x + 120}" y="185" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#16202a">{escape(title)}</text>',
                f'<text x="{x + 120}" y="225" text-anchor="middle" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#356a86">{count:,}</text>',
                f'<text x="{x + 120}" y="255" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#536171">{escape(note)}</text>',
            ]
        )
        if index < len(boxes) - 1:
            items.extend(
                [
                    f'<line x1="{x + 240}" y1="212" x2="{x + 295}" y2="212" stroke="#64748b" stroke-width="3"/>',
                    f'<polygon points="{x + 295},212 {x + 282},204 {x + 282},220" fill="#64748b"/>',
                ]
            )
    items.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(items) + "\n", encoding="utf-8")
    return path


def _top_with_other(values: Mapping[str, int], limit: int = 12) -> tuple[list[str], list[int]]:
    items = list(values.items())
    visible = items[:limit]
    remaining = sum(value for _, value in items[limit:])
    if remaining:
        visible.append(("Other", remaining))
    return [name for name, _ in visible], [int(value) for _, value in visible]


def write_figures(
    figures_dir: Path,
    analysis: Mapping[str, object],
    context: AnalysisContext,
) -> dict[str, Path]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    rows = int(analysis["input_rows"])
    coverage = analysis["date_coverage"]
    by_year = analysis["by_year"]
    by_month = analysis["by_month"]
    by_time = analysis["by_time_of_day"]
    by_state = analysis["by_state"]
    by_shape = analysis["by_shape"]
    delay = analysis["reporting_delay"]
    state_labels, state_values = _top_with_other(by_state)
    shape_labels = list(by_shape.keys())
    shape_values = [int(value) for value in by_shape.values()]
    footer = f"{context.dataset_label} • descriptive counts only"

    return {
        "reports_by_year": _bar_chart(
            figures_dir / "reports-by-year.svg",
            title="Reported Sightings by Year",
            subtitle=f"{context.dataset_label} • n={rows:,} • {coverage['start']} to {coverage['end']}",
            footer=footer,
            labels=list(by_year.keys()),
            values=[int(value) for value in by_year.values()],
            description=f"Bar chart of reported sighting counts by year for the {context.short_label}.",
        ),
        "reports_by_month": _bar_chart(
            figures_dir / "reports-by-month.svg",
            title="Reported Sightings by Calendar Month",
            subtitle=f"{context.dataset_label} • n={rows:,} • aggregated across the covered years",
            footer=footer,
            labels=list(by_month.keys()),
            values=[int(value) for value in by_month.values()],
            description=f"Bar chart of reported sighting counts by calendar month for the {context.short_label}.",
        ),
        "reports_by_time": _bar_chart(
            figures_dir / "reports-by-time-of-day.svg",
            title="Reported Sightings by Time of Day",
            subtitle=f"{context.dataset_label} • n={rows:,} • local clock categories",
            footer=footer,
            labels=list(by_time.keys()),
            values=[int(value) for value in by_time.values()],
            description=f"Bar chart of reported sighting counts by morning, afternoon, evening, and night for the {context.short_label}.",
        ),
        "reports_by_state": _horizontal_bar_chart(
            figures_dir / "reports-by-state.svg",
            title="Reported Sightings by State",
            subtitle=f"{context.dataset_label} • n={rows:,} • top states plus Other",
            footer=footer,
            labels=state_labels,
            values=state_values,
            description=f"Horizontal bar chart of reported sighting counts by U.S. state for the {context.short_label}.",
        ),
        "reports_by_shape": _horizontal_bar_chart(
            figures_dir / "reports-by-shape.svg",
            title="Reported Sightings by Shape",
            subtitle=f"{context.dataset_label} • n={rows:,} • standardized categories",
            footer=footer,
            labels=shape_labels,
            values=shape_values,
            description=f"Horizontal bar chart of reported sighting counts by standardized shape category for the {context.short_label}.",
        ),
        "sample_flow": _sample_flow_chart(
            figures_dir / "sample-flow.svg",
            input_rows=rows,
            delay_rows=int(delay["valid_rows"]),
            flagged_rows=int(delay["excluded_negative_calendar_rows"]),
            context=context,
        ),
    }
