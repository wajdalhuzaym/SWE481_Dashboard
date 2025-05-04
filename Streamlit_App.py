import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')  # Avoid warnings

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Software Security Dashboard", layout="wide")
# font
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Apply font to EVERYTHING properly */
    html, body, [class*="css"] * {
        font-family: 'Inter', sans-serif !important;
    }

    /* Make the sidebar title bigger */
    section[data-testid="stSidebar"] h1 {
        font-size: 1.8rem;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)


# -----------------------------
# LOAD DATA
# -----------------------------

@st.cache_data
def load_valid_ids():
    ids_df = pd.read_excel(r"Data\student_ids_list.xlsx")
    return ids_df.iloc[:, 0].astype(str).tolist()

@st.cache_data
def load_survey_data():
    df = pd.read_excel(r"Data/SWE481_Cleaned_Responses_Numeric_Final.xlsx")
    numeric_columns = [
        'Midterm_1',
        'Midterm_2',
        'Assignments',
        'Absences',
        'Lecture_Satisfaction',
        'Project_Satisfaction',
        'Confidence',
        'Tools_Used'
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

valid_ids = load_valid_ids()
df_survey = load_survey_data()

# -----------------------------
# LOGIN PAGE
# -----------------------------

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def login_page():
    st.title("🔐 Software Security Dashboard Login")
    st.write("Please enter your University ID to access the dashboard.")

    user_id_input = st.text_input("Student ID", max_chars=9)

    if st.button("Login"):
        if user_id_input in valid_ids:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id_input
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid University ID. Please try again.")

# -----------------------------
# HELPER FUNCTION
# -----------------------------
metric_descriptions = {
    "Average Midterm 1": "Most students scored full marks.",
    "Average Midterm 2": "Most scored 10-14, with many full marks.",
    "Average Assignments": "Nearly all earned full marks.",
    "Average Absences": "Most missed 1-3 classes; few missed 7+.",
    "Lecture Satisfaction": "Moderate satisfaction with lectures.",
    "Project Satisfaction": "High satisfaction with project work.",
    "Confidence": "Most students showed moderate to high understanding of security topics.",
    "Tools Used (%)": "About 90% used security tools."
}


# Label mappings for chart x-axis
midterm_labels = {4: "1-6", 7: "7-9", 13.5: "10-14", 0:"0"}
absence_labels = {2: "1-3", 1: "1-3", 4: "4-6", 7: "7+"}


def display_metric(col, title, data_series, color, chart_type):
    with col:
        with st.container(border=True):
            avg_value = data_series.mean()
            min_value = data_series.min()
            max_value = data_series.max()

            # 💡 Smart display labels
            if title in ["Average Midterm 1", "Average Midterm 2"]:
                display_value = f"{avg_value:.2f} / 15"
            elif title == "Average Assignments":
                display_value = f"{avg_value:.2f} / 5"
            elif title == "Average Absences":
                display_value = f"{round(avg_value)} days"
            elif title in ["Lecture Satisfaction", "Project Satisfaction", "Confidence"]:
                display_value = f"{avg_value:.2f} / 4 Rating"
            elif title == "Tools Used (%)":
                display_value = f"{avg_value*100:.0f}%"
            else:
                display_value = f"{avg_value:.2f}"

            st.metric(f"{title}", display_value, help=f"Min: {min_value}, Max: {max_value}")

            # Description below metric
            st.caption(metric_descriptions.get(title, ""))

            # Create mini chart inside metric box
            fig, ax = plt.subplots(figsize=(3, 1.8))
            full_series = data_series.dropna().sort_values()

            # Special handling for Absences chart: merge 1s into 2s (group 1-3)
            if "Absences" in title:
                full_series = full_series.replace(1, 2)

            counts = full_series.value_counts().sort_index()

            # Plot the chart
            if chart_type == "Bar":
                bars = ax.bar(counts.index, counts.values, color=color)
                ax.bar_label(bars, labels=[f"{int(val)}" for val in counts.values], label_type='edge', fontsize=8, padding=2)
            elif chart_type == "Area":
                ax.fill_between(counts.index, counts.values, color=color, alpha=0.6)
                ax.plot(counts.index, counts.values, color=color)
            elif chart_type == "Line":
                ax.plot(counts.index, counts.values, color=color, marker='o')

            # Set x-axis labels based on metric type
            if "Midterm" in title:
                labels = [midterm_labels.get(val, str(val)) for val in counts.index]
                ax.set_xticks(counts.index)
                ax.set_xticklabels(labels)
            elif "Absences" in title:
                labels = [absence_labels.get(val, str(val)) for val in counts.index]
                ax.set_xticks(counts.index)
                ax.set_xticklabels(labels)

            ax.set_xlabel("Value")
            ax.set_ylabel("Count")
            ax.set_title("")
            st.pyplot(fig)

# -----------------------------
# MAIN DASHBOARD
# -----------------------------

def main_dashboard():
    #st.title("Software Security Dashboard")
    st.write(f"👋 Welcome, **{st.session_state.user_id}**")
    st.sidebar.title("Software Security Dashboard")
    #st.sidebar.markdown("*Insights from 29 students' feedback*")

    # Sidebar settings
    st.sidebar.header("⚙️Dashboard Settings")
    metric_options = [
        "All",
        "Midterm_1",
        "Midterm_2",
        "Assignments",
        "Absences",
        "Lecture_Satisfaction",
        "Project_Satisfaction",
        "Confidence",
        "Tools_Used"
    ]
    chart_type = st.sidebar.selectbox("Select chart type", ["Bar", "Area", "Line"])
    selected_metric = st.sidebar.selectbox("Select metric", metric_options)

    metrics = [
        ("Average Midterm 1", df_survey['Midterm_1'], '#29b5e8'),
        ("Average Midterm 2", df_survey['Midterm_2'], '#FF9F36'),
        ("Average Assignments", df_survey['Assignments'], '#D45B90'),
        ("Average Absences", df_survey['Absences'], '#7D44CF'),
        ("Lecture Satisfaction", df_survey['Lecture_Satisfaction'], '#2E8B57'),
        ("Project Satisfaction", df_survey['Project_Satisfaction'], '#FF6347'),
        ("Confidence", df_survey['Confidence'], '#8A2BE2'),
        ("Tools Used (%)", df_survey['Tools_Used'], '#FFA500'),
    ]
    st.markdown("""
    ### What the Numbers Say ?
    """)

    if selected_metric == "All":
        cols = st.columns(4)
        for idx, (title, data_series, color) in enumerate(metrics[:4]):
            display_metric(cols[idx], title, data_series, color, chart_type)

        cols2 = st.columns(4)
        for idx, (title, data_series, color) in enumerate(metrics[4:]):
            display_metric(cols2[idx], title, data_series, color, chart_type)
    else:
        selected = None
        for title, data_series, color in metrics:
            if selected_metric in title or selected_metric in data_series.name:
                selected = (title, data_series, color)
                break

        if selected:
            cols = st.columns([1, 2, 1])
            display_metric(cols[1], selected[0], selected[1], selected[2], chart_type)


    with st.expander('🗂️ See Full Survey Data'):
        st.dataframe(df_survey)
        st.markdown(
            "🔗 [View the original survey here](https://docs.google.com/forms/d/e/1FAIpQLSejVdE7ksv8VMnNu4GdS3nY9YBnf30EhYPXqSJinurxEGN9-g/viewform?usp=sharing)",
            unsafe_allow_html=True
        )

# -----------------------------
# RUN APP
# -----------------------------

if not st.session_state.logged_in:
    login_page()
else:
    main_dashboard()
