import streamlit as st


def render_metric_card(label, value, sub=None):
    """
    Renders a single glassmorphism metric card.

    Parameters
    ----------
    label : str
        The small uppercase label shown above the value.
    value : str
        The large primary value displayed on the card.
    sub : str, optional
        A small secondary line shown below the value.
    """
    sub_html = f'<div class="metric-card-sub">{sub}</div>' if sub else ""

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-label">{label}</div>
            <div class="metric-card-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(metrics):
    """
    Renders a horizontal row of metric cards.

    Parameters
    ----------
    metrics : list of dict
        Each dict must contain 'label' and 'value'.
        Optionally may contain 'sub'.

    Example
    -------
    render_metric_row([
        {"label": "Total Students", "value": "1,200", "sub": "Enrolled"},
        {"label": "Total Courses", "value": "34"},
    ])
    """
    columns = st.columns(len(metrics))
    for col, metric in zip(columns, metrics):
        with col:
            render_metric_card(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                sub=metric.get("sub", None),
            )


def render_page_header(title, subtitle=None):
    """
    Renders a styled page header with an optional subtitle.

    Parameters
    ----------
    title : str
        The main page title.
    subtitle : str, optional
        A secondary description shown below the title.
    """
    subtitle_html = (
        f'<div class="page-subtitle">{subtitle}</div>' if subtitle else ""
    )

    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-title">{title}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(title):
    """
    Renders a styled section title inside a page.

    Parameters
    ----------
    title : str
        The section heading text.
    """
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )


def render_badge(text, variant="blue"):
    """
    Renders a small styled badge tag.

    Parameters
    ----------
    text : str
        The text to display inside the badge.
    variant : str
        One of 'blue', 'green', 'red', 'yellow'.
    """
    st.markdown(
        f'<span class="badge badge-{variant}">{text}</span>',
        unsafe_allow_html=True,
    )