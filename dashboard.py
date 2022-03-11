import streamlit as st
import pandas as pd
import json
import numpy as np
import plotly.express as px
from db_communication import DatabaseCommunicator
st.set_page_config(layout="wide")


# - Load data -
# New approach
logs_db_communicator = DatabaseCommunicator()
entries_in_db = logs_db_communicator.retrieve_information()

data = list(entries_in_db)
for dat in data:
    del dat["_id"]
    # dat["timestamp"] = str(dat["timestamp"])

# Old approach
# f = open('data_in_db.json')
# data = json.load(f)

df = pd.json_normalize(data)
df['index'] = range(0, len(df))


full = pd.DataFrame()
for main_idx, entry in enumerate(df['entries']):
    new = pd.DataFrame()
    for idx, each_class in enumerate(entry):
        new.at[idx, 'classname'] = each_class['classname']
        new.at[idx, 'confidence'] = each_class['confidence']
        new.at[idx, 'accepted'] = each_class['accepted']
        new.at[idx, 'weight'] = each_class['weight']
        new.at[idx, 'index'] = main_idx
    full = full.append(new)


all_db = pd.merge(full, df, how='left', on='index')

for idx in all_db['index']:
    all_db.loc[all_db['index'] == idx, 'precision'] = sum(all_db[all_db['index'] == idx]['accepted'])*100/len(all_db[all_db['index'] == idx]['accepted'])

all_db = all_db[(0 < all_db["insulin_factor"]) & (all_db["insulin_factor"] < 0.5)]  # Sort out some insulin factor outliers

# - Calculate key values -
n_values = 10
last_10 = all_db.nlargest(n_values, "timestamp")
precision_avg = np.mean(last_10["precision"])
resp_time_avg = np.round(np.mean(all_db.nlargest(n_values, "timestamp")["response_time"]), 3)

nr_samples = 3
last_samples = pd.DataFrame(all_db.nlargest(nr_samples, "timestamp"))
last_samples = last_samples.drop(columns=["entries"])

medium_avg_latency = np.mean(all_db.loc[all_db["model_used"] == "medium", "response_time"])
small_avg_latency = np.mean(all_db.loc[all_db["model_used"] == "small", "response_time"])
nano_avg_latency = np.mean(all_db.loc[all_db["model_used"] == "nano", "response_time"])


# - Web app -
st.title("ImageToInsulin Dashboard")
page_option = st.radio('', ("Developer's View", "Business' View"), index=1)

if page_option == "Developer's View":
    # Display the last sample
    st.markdown("Last " + str(nr_samples) + " samples:")
    st.dataframe(last_samples)

    plot1_1, plot1_2 = st.columns((1, 1))
    plot1_3, plot1_4 = st.columns((1, 1))

    # Row 1 of plots
    fig = px.line(all_db, x='timestamp', y="precision", color='model_used', title='Time series of Precision per upload')
    plot1_1.plotly_chart(fig, use_container_width=True)

    fig = px.line(all_db, x='timestamp', y="response_time", color='model_used', title='Time series of Response time')
    plot1_2.plotly_chart(fig, use_container_width=True)

    # Row 2
    fig = px.scatter(all_db, x='classname', y='confidence', color='model_used', title='Scatter plot of Classname vs Confidence')
    plot1_3.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(all_db, x="classname", title='Histogram of Classes')
    fig = fig.update_layout()
    plot1_4.plotly_chart(fig, use_container_width=True)

    # Latency of different models
    # st.markdown("Average latency medium model: " + str(np.round(medium_avg_latency, 3)) + " s")
    # st.markdown("Average latency small model: " + str(np.round(small_avg_latency, 3)) + " s")
    # st.markdown("Average latency nano model: " + str(np.round(nano_avg_latency, 3)) + " s")


if page_option == "Business' View":
    # Display the quick info
    st.subheader("Quick info:")
    st.markdown("Avg precision last 10 samples: " + str(precision_avg) + " %")
    st.markdown("Avg response time last 10 samples: " + str(resp_time_avg) + " s")

    plot2_1, plot2_2 = st.columns((1, 1))
    plot2_3, plot2_4 = st.columns((1, 1))
    plot2_5, plot2_6 = st.columns((1, 1))

    # Row 1 of plots
    fig = px.line(all_db, x='timestamp', y="precision", title='Time series of Precision per upload')
    plot2_1.plotly_chart(fig, use_container_width=True)

    fig = px.line(all_db, x='timestamp', y="response_time", title='Time series of Response time')
    plot2_2.plotly_chart(fig, use_container_width=True)

    # Row 2 of plots
    fig = px.histogram(all_db, x="insulin_factor", title='Histogram of Insulin factor')
    fig = fig.update_layout()
    plot2_3.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(all_db, x="weight", title='Histogram of Weights of food')
    fig = fig.update_layout()
    plot2_4.plotly_chart(fig, use_container_width=True)

    # Row 3 of plots
    fig = px.histogram(all_db, x="classname", title='Histogram of Classes')
    fig = fig.update_layout()
    plot2_5.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(all_db, x="insulin_amount", title='Histogram of Insulin Dosage')
    fig = fig.update_layout()
    plot2_6.plotly_chart(fig, use_container_width=True)

    st.subheader("10 samples with highest insulin amount:")
    st.dataframe(all_db.nlargest(10, "insulin_amount"))







