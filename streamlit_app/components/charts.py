import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# SHARED CHART CONFIGURATION
# ============================================================

TRANSPARENT = "rgba(0,0,0,0)"

CHART_FONT = dict(
    family="Inter, sans-serif",
    color="rgba(255, 255, 255, 0.8)",
)

CHART_LAYOUT = dict(
    paper_bgcolor=TRANSPARENT,
    plot_bgcolor=TRANSPARENT,
    font=CHART_FONT,
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        bgcolor="rgba(255, 255, 255, 0.05)",
        bordercolor="rgba(255, 255, 255, 0.1)",
        borderwidth=1,
        font=dict(color="rgba(255, 255, 255, 0.8)", size=12),
    ),
    xaxis=dict(
        gridcolor="rgba(255, 255, 255, 0.06)",
        zerolinecolor="rgba(255, 255, 255, 0.06)",
        tickfont=dict(color="rgba(255, 255, 255, 0.6)", size=11),
        title_font=dict(color="rgba(255, 255, 255, 0.6)", size=12),
    ),
    yaxis=dict(
        gridcolor="rgba(255, 255, 255, 0.06)",
        zerolinecolor="rgba(255, 255, 255, 0.06)",
        tickfont=dict(color="rgba(255, 255, 255, 0.6)", size=11),
        title_font=dict(color="rgba(255, 255, 255, 0.6)", size=12),
    ),
)

BLUE_GRADIENT_SCALE = [
    [0.0, "#0072ff"],
    [1.0, "#00c6ff"],
]

BLUE_SEQUENCE = [
    "#4f8ef7",
    "#00c6ff",
    "#0072ff",
    "#38bdf8",
    "#7dd3fc",
    "#93c5fd",
    "#60a5fa",
]


def _apply_layout(fig, title=None):
    """
    Applies the shared glassmorphism layout to any Plotly figure.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
    title : str, optional
    """
    layout = dict(CHART_LAYOUT)
    if title:
        layout["title"] = dict(
            text=title,
            font=dict(
                family="Inter, sans-serif",
                color="#ffffff",
                size=15,
            ),
            x=0,
            xanchor="left",
            pad=dict(l=4),
        )
    fig.update_layout(**layout)
    return fig


# ============================================================
# ENROLLMENT CHARTS
# ============================================================

def enrollment_bar_chart(df):
    """
    Horizontal bar chart showing total enrollments per course.

    Parameters
    ----------
    df : pd.DataFrame
        Expected columns: course_name, total_enrollments
    """
    fig = px.bar(
        df,
        x="total_enrollments",
        y="course_name",
        orientation="h",
        color="total_enrollments",
        color_continuous_scale=BLUE_GRADIENT_SCALE,
        labels={
            "total_enrollments": "Total Enrollments",
            "course_name": "Course",
        },
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Enrollments: %{x}<extra></extra>",
    )
    fig.update_coloraxes(showscale=False)
    fig = _apply_layout(fig, title="Enrollments Per Course")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# GRADE CHARTS
# ============================================================

def grade_distribution_histogram(df):
    """
    Histogram of final score distribution across all students.

    Parameters
    ----------
    df : pd.DataFrame
        Expected columns: final_score
    """
    fig = px.histogram(
        df,
        x="final_score",
        nbins=20,
        color_discrete_sequence=["#4f8ef7"],
        labels={"final_score": "Final Score"},
    )
    fig.update_traces(
        marker_line_color="rgba(255,255,255,0.1)",
        marker_line_width=1,
        hovertemplate="Score Range: %{x}<br>Count: %{y}<extra></extra>",
    )
    fig = _apply_layout(fig, title="Final Score Distribution")
    st.plotly_chart(fig, use_container_width=True)


def average_grades_bar_chart(df):
    """
    Grouped bar chart comparing average assignment, exam,
    and final scores per course.

    Parameters
    ----------
    df : pd.DataFrame
        Expected columns: course_name, avg_assignment,
                          avg_exam, avg_final
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Assignment",
        x=df["course_name"],
        y=df["avg_assignment"],
        marker_color="#4f8ef7",
        hovertemplate="<b>%{x}</b><br>Assignment: %{y}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        name="Exam",
        x=df["course_name"],
        y=df["avg_exam"],
        marker_color="#00c6ff",
        hovertemplate="<b>%{x}</b><br>Exam: %{y}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        name="Final",
        x=df["course_name"],
        y=df["avg_final"],
        marker_color="#0072ff",
        hovertemplate="<b>%{x}</b><br>Final: %{y}<extra></extra>",
    ))

    fig.update_layout(barmode="group", bargap=0.2, bargroupgap=0.05)
    fig = _apply_layout(fig, title="Average Grades Per Course")
    st.plotly_chart(fig, use_container_width=True)


def grade_scatter_chart(df):
    """
    Scatter plot of assignment grade vs exam grade,
    coloured by final score.

    Parameters
    ----------
    df : pd.DataFrame
        Expected columns: assignment_grade, exam_grade,
                          final_score, name, surname, course_name
    """
    df = df.copy()
    df["student"] = df["name"] + " " + df["surname"]

    fig = px.scatter(
        df,
        x="assignment_grade",
        y="exam_grade",
        color="final_score",
        color_continuous_scale=BLUE_GRADIENT_SCALE,
        hover_data={"student": True, "course_name": True, "student": False},
        labels={
            "assignment_grade": "Assignment Grade",
            "exam_grade": "Exam Grade",
            "final_score": "Final Score",
        },
        custom_data=["student", "course_name", "final_score"],
    )
    fig.update_traces(
        marker=dict(size=8, opacity=0.8, line=dict(width=0)),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Course: %{customdata[1]}<br>"
            "Assignment: %{x}<br>"
            "Exam: %{y}<br>"
            "Final: %{customdata[2]}<extra></extra>"
        ),
    )
    fig = _apply_layout(fig, title="Assignment vs Exam Grades")
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# ATTENDANCE CHARTS
# ============================================================

def attendance_distribution_histogram(df):
    """
    Histogram of attendance percentage distribution.

    Parameters
    ----------
    df : pd.DataFrame
        Expected columns: attendance_percentage
    """
    fig = px.histogram(
        df,
        x="attendance_percentage",
        nbins=20,
        color_discrete_sequence=["#00c6ff"],
        labels={"attendance_percentage": "Attendance Percentage"},
    )
    fig.update_traces(
        marker_line_color="rgba(255,255,255,0.1)",
        marker_line_width=1,
        hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
    )
    fig = _apply_layout(fig, title="Attendance Distribution")
    st.plotly_chart(fig, use_container_width=True)


def average_attendance_bar_chart(df):
    """
    Horizontal bar chart of average attendance per course.

    Parameters
    ----------
    df : pd.DataFrame
        Expected columns: course_name, avg_attendance
    """
    fig = px.bar(
        df,
        x="avg_attendance",
        y="course_name",
        orientation="h",
        color="avg_attendance",
        color_continuous_scale=BLUE_GRADIENT_SCALE,
        labels={
            "avg_attendance": "Average Attendance (%)",
            "course_name": "Course",
        },
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Avg Attendance: %{x}%<extra></extra>",
    )
    fig.update_coloraxes(showscale=False)
    fig = _apply_layout(fig, title="Average Attendance Per Course")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# STUDENT CHARTS
# ============================================================

def gender_donut_chart(df):
    """
    Donut chart showing gender distribution of students.

    Parameters
    ----------
    df : pd.DataFrame
        Expected columns: gender, total
    """
    fig = px.pie(
        df,
        names="gender",
        values="total",
        hole=0.6,
        color_discrete_sequence=BLUE_SEQUENCE,
    )
    fig.update_traces(
        textfont=dict(color="#ffffff", size=12),
        marker=dict(line=dict(color="rgba(255,255,255,0.05)", width=2)),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    )
    fig = _apply_layout(fig, title="Gender Distribution")
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# OVERVIEW CHARTS
# ============================================================

def overview_grades_gauge(average_score):
    """
    Gauge chart showing the overall average final score.

    Parameters
    ----------
    average_score : float
        The average final score across all students.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=average_score,
        number=dict(
            font=dict(color="#ffffff", family="Inter, sans-serif", size=36),
            suffix="",
        ),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickcolor="rgba(255,255,255,0.4)",
                tickfont=dict(color="rgba(255,255,255,0.6)", size=11),
            ),
            bar=dict(color="#4f8ef7"),
            bgcolor=TRANSPARENT,
            borderwidth=0,
            steps=[
                dict(range=[0, 50], color="rgba(255,80,80,0.15)"),
                dict(range=[50, 75], color="rgba(255,200,0,0.15)"),
                dict(range=[75, 100], color="rgba(0,210,150,0.15)"),
            ],
            threshold=dict(
                line=dict(color="#00c6ff", width=2),
                thickness=0.75,
                value=average_score,
            ),
        ),
        title=dict(
            text="Average Final Score",
            font=dict(color="rgba(255,255,255,0.7)", size=13),
        ),
    ))
    fig = _apply_layout(fig)
    st.plotly_chart(fig, use_container_width=True)


def overview_attendance_gauge(average_attendance):
    """
    Gauge chart showing the overall average attendance percentage.

    Parameters
    ----------
    average_attendance : float
        The average attendance percentage across all students.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=average_attendance,
        number=dict(
            font=dict(color="#ffffff", family="Inter, sans-serif", size=36),
            suffix="%",
        ),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickcolor="rgba(255,255,255,0.4)",
                tickfont=dict(color="rgba(255,255,255,0.6)", size=11),
            ),
            bar=dict(color="#00c6ff"),
            bgcolor=TRANSPARENT,
            borderwidth=0,
            steps=[
                dict(range=[0, 50], color="rgba(255,80,80,0.15)"),
                dict(range=[50, 75], color="rgba(255,200,0,0.15)"),
                dict(range=[75, 100], color="rgba(0,210,150,0.15)"),
            ],
            threshold=dict(
                line=dict(color="#4f8ef7", width=2),
                thickness=0.75,
                value=average_attendance,
            ),
        ),
        title=dict(
            text="Average Attendance",
            font=dict(color="rgba(255,255,255,0.7)", size=13),
        ),
    ))
    fig = _apply_layout(fig)
    st.plotly_chart(fig, use_container_width=True)