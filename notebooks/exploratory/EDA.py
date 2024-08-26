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

from pathlib import Path

# %% [markdown]
# ## Data

# %%
input_path = Path('../../data/export.xml')
with open(input_path, 'r') as xml_file:
    input_data = xmltodict.parse(xml_file.read())

# %%
#Records list for general health data & imported as Pandas Data Frame
records_list = input_data['HealthData']['Record']
df_records = pd.DataFrame(records_list)

#Workout list for workout data
workouts_list = input_data['HealthData']['Workout']
df_workouts = pd.DataFrame(workouts_list)
df_workouts_flat = pd.json_normalize(df_workouts.to_dict(orient='records'))

#activity summary list for workout data
activity_list = input_data['HealthData']['ActivitySummary']
df_activities = pd.DataFrame(activity_list)

# %% [markdown]
# dumb the data into duckdb

# %%
# Define the path to the DuckDB database
db_path = '../../data/health_data.duckdb'

# Connect to the DuckDB database (it will be created if it doesn't exist)
con = duckdb.connect(db_path)

# Dump the dataframes into the DuckDB database
con.execute("CREATE TABLE IF NOT EXISTS records AS SELECT * FROM df_records")
con.execute("CREATE TABLE IF NOT EXISTS workouts AS SELECT * FROM df_workouts_flat")
con.execute("CREATE TABLE IF NOT EXISTS activities AS SELECT * FROM df_activities")

# Close the connection
con.close()

# %%
df_records.tail()

# %%
df_records['@type'].value_counts()

# %%
df_workouts.tail()

# %%
df_workouts.WorkoutStatistics.value_counts()

# %%
df_activities.tail()

# %%
# Convert date to datetime
df_activities['@dateComponents'] = pd.to_datetime(df_activities['@dateComponents'])
# Convert activeEnergyBurned to numeric
df_activities["@activeEnergyBurned"] = df_activities["@activeEnergyBurned"].apply(pd.to_numeric)

# %%
df_activities = df_activities.loc[(df_activities['@activeEnergyBurned'] != 0)]
plt.bar(df_activities['@dateComponents'], df_activities['@activeEnergyBurned'])
plt.xlabel('Date')
plt.ylabel('Active Energy Burned')
plt.title('Active Energy Burned by Date')

plt.show()

# %%
# create a figure and axis
fig, ax = plt.subplots()

# plot the data
ax.plot(df_activities['@dateComponents'], df_activities['@activeEnergyBurned'])

# set the x-axis label
ax.set_xlabel('Date')

# set the y-axis label
ax.set_ylabel('Energy Burned')

# set the title
ax.set_title('Energy Burned Every Day Since 2022')

# rotate the x-axis labels
plt.xticks(rotation=45)

# show the plot
plt.show()

# %%
df_workouts['@workoutActivityType'].unique()

# %%
import re

# %%
# remove HKWorkoutActivityType from workoutActivityType
df_workouts['@workoutActivityType'] = df_workouts['@workoutActivityType'].str.replace('HKWorkoutActivityType', '')

# %%
# create a figure and axis
fig, ax = plt.subplots()
# convert duration to numeric
df_workouts["@duration"] = df_workouts["@duration"].apply(pd.to_numeric)
# plot the data
ax.bar(df_workouts['@workoutActivityType'], df_workouts['@duration'])

# set the x-axis label
ax.set_xlabel('Activity Type')

# set the y-axis label
ax.set_ylabel('Duration (mins)')

# set the title
ax.set_title('Duration of Activities Since 2022')

# rotate the x-axis labels
plt.xticks(rotation=90)

# show the plot
plt.show()
