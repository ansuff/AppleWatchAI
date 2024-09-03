# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Setup

# %%
import pandas as pd
import xmltodict
import xmltodict
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go
import re

from pathlib import Path

# %% [markdown]
# Define the globals

# %%
RAW_DATA_DIR = Path("../../data")
XML_FILE_NAME = "export.xml"
DUCKDB_DB_NAME = "health_data.duckdb"


# %% [markdown]
# ## Utils

# %%
def camel_to_snake(name):
    # Remove the '@' and convert camelCase to snake_case
    name = re.sub('@', '', name)  # Remove '@' symbol
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()  # Convert camelCase to snake_case
    return name


# %% [markdown]
# ## Data

# %% [markdown]
# I like working with `duckdb` because it's fast and easy to use. I'll use it in the cli in addition to pandas in the notebook.
#
# Let's now create a `duckdb` database and load the data into it if it does not exist.
#
# Note: the workout data needed to be flattened because it included nested data.

# %%
con = duckdb.connect(f"{RAW_DATA_DIR}/{DUCKDB_DB_NAME}")
# Check if the tables already exist
tables_exist = con.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('records', 'workouts', 'activities')").fetchone()[0] >= 3
if not tables_exist:
    input_path = Path('../../data/export.xml')
    with open(input_path, 'r') as xml_file:
        input_data = xmltodict.parse(xml_file.read())

    #Records list for general health data 
    records_list = input_data['HealthData']['Record']
    records_df = pd.DataFrame(records_list)

    #Workout list for workout data
    workouts_list = input_data['HealthData']['Workout']
    workout_df = pd.DataFrame(workouts_list)
    workout_df_flat = pd.json_normalize(workout_df.to_dict(orient='records'))

    #activity summary list for workout data
    activity_list = input_data['HealthData']['ActivitySummary']
    activity_df = pd.DataFrame(activity_list)
    
    # Dump the dataframes into the DuckDB database
    con.execute("CREATE TABLE IF NOT EXISTS records AS SELECT * FROM records_df")
    con.execute("CREATE TABLE IF NOT EXISTS workouts AS SELECT * FROM workout_df_flat")
    con.execute("CREATE TABLE IF NOT EXISTS activities AS SELECT * FROM activity_df")
else:
    records_df = con.query("SELECT * FROM records").to_df()
    workout_df_flat = con.query("SELECT * FROM workouts").to_df()
    activity_df = con.query("SELECT * FROM activities").to_df()
con.close()

# %% [markdown]
# # EDA

# %% [markdown]
# ## Records

# %%
records_df.info()

# %% [markdown]
# so records requires `~250 MB` in the memory, which is fine for now, I will eventually be using duckdb for the streamlined code.

# %%
display(records_df["@type"].value_counts()) 

# %% [markdown]
# Apple provides way more than what I initially wanted which is great! this will be a fun dataset to work with. However, many of these physical activities are not what I consistently do, so I'll filter them out.
#
# I have around `3 million` records to work with, which is a great amount as I tried to be accurate in my records the past few years (since I got my first Apple Watch).

# %% [markdown]
# Let's rename some of the columns

# %%
# Applying the camel_to_snake function to rename all columns
records_df.columns = [camel_to_snake(col) for col in records_df.columns]
# Display the renamed columns
print(records_df.columns)

# %%
# return recorded Active Energy Burned
records_df.loc[(records_df['type'].str.contains("ActiveEnergyBurned"))]

# %% [markdown]
# From just looking into the calories burned, some aggregations are needed to get more meaningful insights.
#
# We have three date columns: `start_date`, `end_date` and `creation_date`. No need to keep the `creation_date` column (when did I add the record to the database). I will calculate duration from `start_date` and `end_date`, and keep the `start_date` column only.

# %% [markdown]
# ### Data Cleaning

# %% [markdown]
# First we convert the date columns to datetime objects.
#
# Then we calculate the duration of each record.

# %%
date_columns = ['start_date', 'end_date']
for col in date_columns:
    records_df[col] = pd.to_datetime(records_df[col])
records_df['duration'] = records_df['end_date'] - records_df['start_date']

# %%
columns_to_drop = ['source_name', 'source_version', 'device', 'creation_date', 'source_version', 'metadata_entry','end_date']
records_df_selected = records_df.drop(columns=columns_to_drop)

# %%
records_df_selected.tail()

# %% [markdown]
# `heart_rate_variability_metadata_list` contains a dict, needs to flattened

# %%
pd.json_normalize(records_df_selected.to_dict(orient='records'))

# %% [markdown]
# The `heart_rate_variability_metadata_list` column includes instantaneous heart rate variability data, which is not of an interest of mine given the inclusion of heart rate averages in the dataset. I will drop this column. Although, will keep an eye on it for future analysis.

# %%
records_df_selected = records_df_selected.drop(columns="heart_rate_variability_metadata_list")

# %%
# transform 'startDate' into date format 
records_df_cleaned = records_df_selected.copy()
records_df_cleaned['Day'] = records_df_selected['start_date'].dt.strftime('%A')
records_df_cleaned['Date'] = records_df_selected['start_date'].dt.strftime('%Y-%m-%d')
records_df_cleaned['Month'] = records_df_selected['start_date'].dt.strftime('%B')
# value is numeric, NaN if fails
records_df_cleaned['value'] = pd.to_numeric(records_df_selected['value'], errors='coerce')
# some records do not measure anything, just count occurrences
# filling with 1.0 (= one time) makes it easier to aggregate
records_df_cleaned['value'] = records_df_cleaned['value'].fillna(1.0)

# shorter observation names
records_df_cleaned['type'] = records_df_cleaned['type'].str.replace('HKQuantityTypeIdentifier', '')
records_df_cleaned['type'] = records_df_cleaned['type'].str.replace('HKCategoryTypeIdentifier', '')

# reorder columns
records_df_cleaned = records_df_cleaned[['type', 'Date','Day', 'Month','value','unit', 'duration']]

# %%
records_df_cleaned.sample(5)

# %%
records_df_cleaned.loc[records_df_cleaned.duration==pd.Timedelta('0 days 00:00:00')]

# %% [markdown]
# So we have quite a lot of activity types that do not have a duration, they just measure speed, bmi, etc. I will see if I will be needing them later.

# %%
display(records_df_cleaned["type"].value_counts()) 

# %%
records_df_cleaned.loc[records_df_cleaned['type'].str.contains("SleepAnalysis")]

# %% [markdown]
# I only need some of these record types that Apple provides, so will select only relevant ones.....

# %%
# dictionary of DataFrames for filtered 'records_df'
records_df_dict = {}
# filter 'type' of 'records'
record_types = [
   'BodyMass',
   'ActiveEnergyBurned',
   'BasalEnergyBurned',
   'DistanceWalkingRunning',
   'StepCount',
   'AppleStandTime',
   'WalkingSpeed',
   'DistanceCycling',
   'HeartRateVariabilitySDNN',
   'RestingHeartRate',
   'WalkingHeartRateAverage',
   'VO2Max',
   'HeartRateRecoveryOneMinute',
   'PhysicalEffort',
   'SleepAnalysis'
   ]
# create new DataFrame for every interested data
for record_type in record_types:
   records_df_dict[record_type] = records_df_cleaned.loc[(records_df_cleaned['type'].str.contains(record_type))].rename(columns={"value":record_type}).sort_values(by='Date')

# %% [markdown]
# Now aggregating the daily values

# %%
# list of data 'type' that need to be summed daily
key_get_sum = [
    'BasalEnergyBurned', 
    'ActiveEnergyBurned',
    'DistanceWalkingRunning',
    'StepCount',
    'AppleStandTime',
    'DistanceCycling',
    'PhysicalEffort',
    ]
records_df_dict_daily = {}
for key in key_get_sum:
    records_df_dict_daily[key] = records_df_dict[key].groupby(records_df_dict[key]['Date']).agg({key: 'sum', 'Day': lambda x: x.mode().iat[0]}).reset_index()

# %% [markdown]
# Including also monthly aggregations

# %%
records_df_dict_monthly = {}
for key in key_get_sum:
    records_df_dict_monthly[key] = records_df_dict[key].groupby(records_df_dict[key]['Date'].str[:-3]).agg({key: 'sum', 'Month': lambda x: x.mode().iat[0]}).reset_index()

# %% [markdown]
# ### Ploting

# %%
fig = go.Figure()
fig.add_trace(go.Scatter(x=records_df_dict_daily['DistanceCycling']['Date'], y=records_df_dict_daily['DistanceCycling']['DistanceCycling'], mode='lines', name='Cycling'))
fig.add_trace(go.Scatter(x=records_df_dict_daily['ActiveEnergyBurned']['Date'], y=records_df_dict_daily['ActiveEnergyBurned']['ActiveEnergyBurned'], mode='lines', name='Energy', yaxis='y2'))

fig.update_layout(title='Daily Distance Cycling and Active Energy Burned', xaxis_title='Date', yaxis_title='Distance Cycling (m)', yaxis2=dict(overlaying='y', side='right'))
fig.show()

# %%
