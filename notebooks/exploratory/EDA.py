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
import re

from pathlib import Path


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

# %%
input_path = Path('../../data/export.xml')
with open(input_path, 'r') as xml_file:
    input_data = xmltodict.parse(xml_file.read())

# %%
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

# %% [markdown]
# I like working with `duckdb` because it's fast and easy to use. I'll use it in the cli in addition to pandas in the notebook.
#
# Let's now create a `duckdb` database and load the data into it.
#
# Note: the workout data needed to be flattened because it included nested data.

# %%
# Define the path to the DuckDB database
db_path = '../../data/health_data.duckdb'

# Connect to the DuckDB database (it will be created if it doesn't exist)
con = duckdb.connect(db_path)

# Dump the dataframes into the DuckDB database
con.execute("CREATE TABLE IF NOT EXISTS records AS SELECT * FROM records_df")
con.execute("CREATE TABLE IF NOT EXISTS workouts AS SELECT * FROM workout_df_flat")
con.execute("CREATE TABLE IF NOT EXISTS activities AS SELECT * FROM activity_df")

# Close the connection
con.close()

# %% [markdown]
# # EDA

# %% [markdown]
# ## Records

# %%
records_df.info()
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

# %% [markdown]
# ### Data Cleaning

# %%
