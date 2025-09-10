import pandas as pd
import gspread
import plotly.express as px
import taipy as tp
from taipy import Config
from taipy.gui import Gui
import taipy.gui.builder as tgb

# Google Sheet containing the cardiac dataset
# Place your own Google Sheet link here
# Example: "https://docs.google.com/spreadsheets/d/<YOUR-SHEET-ID>/edit?usp=sharing"
SHEET_URL = "https://docs.google.com/spreadsheets/d/<YOUR-SHEET-ID>/edit?usp=sharing"


# Connect to Google Sheets API using service account credentials
client = gspread.service_account(filename="config/credentials.json")

# Load the first worksheet into a Pandas DataFrame
df_raw = pd.DataFrame(client.open_by_url(SHEET_URL).get_worksheet(0).get_all_records())

# Convert 'sex' column to numeric (0 = Female, 1 = Male) and create label column
df_raw["sex"] = pd.to_numeric(df_raw["sex"], errors="coerce").fillna(0).astype(int)
df_raw["sex_label"] = df_raw["sex"].map({0: "Female", 1: "Male"})


# -----------------------------
# Function: Compute average age
# -----------------------------
def compute_avg_age(filtered_df: pd.DataFrame, gender_filter: str) -> float:
    """
    Compute average age from the dataset based on gender filter.
    gender_filter can be 'All', 'Male', or 'Female'.
    """
    data = (
        filtered_df
        if gender_filter == "All"
        else filtered_df[filtered_df["sex_label"] == gender_filter]
    )
    return round(data["age"].mean(), 1) if not data.empty else 0


# -----------------------------
# Configure Taipy Data Nodes
# -----------------------------
filtered_df_cfg = Config.configure_data_node("filtered_df")
gender_filter_cfg = Config.configure_data_node("gender_filter")
avg_age_cfg = Config.configure_data_node("avg_age")

# Configure Taipy Task
task_cfg = Config.configure_task(
    "compute_avg_age", compute_avg_age, [filtered_df_cfg, gender_filter_cfg], avg_age_cfg
)

# Configure Taipy Scenario
scenario_cfg = Config.configure_scenario("cardiac_scenario", [task_cfg])

# Export configuration to TOML file
Config.export("config.toml")


# -----------------------------
# GUI Initial States
# -----------------------------
gender_lov = ["All", "Male", "Female"]  # Gender options
gender_selected = "All"                 # Default gender filter
filtered_df = df_raw.copy()             # Default dataset view
pie_fig = px.pie()                      # Placeholder for pie chart
box_fig = px.box()                      # Placeholder for box plot
avg_age = 0                             # Default avg age


# -----------------------------
# Dashboard Update Function
# -----------------------------
def update_dash(state):
    """
    Update dashboard figures and statistics based on selected gender filter.
    """
    subset = (
        df_raw if state.gender_selected == "All"
        else df_raw[df_raw["sex_label"] == state.gender_selected]
    )
    state.filtered_df = subset
    state.avg_age = round(subset["age"].mean(), 1) if not subset.empty else 0

    # Pie chart: count of 'target' by gender
    state.pie_fig = px.pie(
        subset.groupby("sex_label")["target"].count().reset_index(name="count"),
        names="sex_label", values="count",
        title=f"Target Count -- {state.gender_selected}"
    )

    # Box plot: cholesterol by gender
    state.box_fig = px.box(subset, x="sex_label", y="chol", title="Cholesterol by Gender")


# -----------------------------
# Save Scenario Function
# -----------------------------
def save_scenario(state):
    """
    Save the current scenario state into Taipy scenario object.
    """
    state.scenario.filtered_df.write(state.filtered_df)
    state.scenario.gender_filter.write(state.gender_selected)
    state.refresh("scenario")
    tp.gui.notify(state, "s", "Scenario saved -- submit to compute!")


# -----------------------------
# GUI Layout (Taipy Builder)
# -----------------------------
with tgb.Page() as page:
    tgb.text("# Cardiac Arrest Dashboard")

    # Gender selector
    tgb.selector(value="{gender_selected}", lov="{gender_lov}",
                 label="Select Gender:", on_change=update_dash)

    # Charts
    with tgb.layout(columns="1 1", gap="20px"):
        tgb.chart(figure="{pie_fig}")
        tgb.chart(figure="{box_fig}")

    # Statistics
    tgb.text("### Average Age (Live): {avg_age}")
    tgb.table(data="{filtered_df}", pagination=True)

    tgb.text("---")
    tgb.text("## Scenario Management")

    # Scenario management controls
    tgb.scenario_selector("{scenario}")
    tgb.selector(label="Scenario Gender:", lov="{gender_lov}",
                 value="{gender_selected}", on_change=save_scenario)
    tgb.scenario("{scenario}")
    tgb.scenario_dag("{scenario}")

    # Scenario computed result
    tgb.text("**Avg Age (Scenario):**")
    tgb.data_node("{scenario.avg_age}")
    tgb.table(data="{filtered_df}", pagination=True)


# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    # Start Taipy Orchestrator
    tp.Orchestrator().run()

    # Create a default scenario and initialize with full dataset
    scenario = tp.create_scenario(scenario_cfg)
    scenario.filtered_df.write(df_raw)
    scenario.gender_filter.write("All")

    # Run GUI
    Gui(page).run(title="Cardiac Arrest Dashboard", dark_mode=True)
