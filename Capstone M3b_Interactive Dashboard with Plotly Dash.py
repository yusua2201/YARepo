import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import os

url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
spacex_df = pd.read_csv(url)
# print(spacex_df.head())
print(spacex_df.shape)

# Task 1: Add a Launch Site Drop-Down Input Component
app = dash.Dash(__name__)

# Extract unique launch sites from spacex_df
launch_sites = spacex_df["Launch Site"].unique()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in launch_sites
]

min_payload = spacex_df["Payload Mass (kg)"].min()
max_payload = spacex_df["Payload Mass (kg)"].max()
# Define app layout
app.layout = html.Div([
    html.H2("SpaceX Launch Records Dashboard"),
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    # Payload Range Slider
    html.Div([
        html.P("Select Payload Range (Kg):"),
        dcc.RangeSlider(
            id='payload-slider',
            min=0, max=10000, step=1000,
            marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
            value=[min_payload, max_payload]
        )
    ], style={'width': '70%', 'margin': 'auto'}),
    
    # Pie Chart Output
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    # Scatter Plot Output
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback function to update Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_pie_chart(entered_site, payload_range):
    # Filter data based on payload range
    filtered_df = spacex_df[(spacex_df["Payload Mass (kg)"] >= payload_range[0]) &
                            (spacex_df["Payload Mass (kg)"] <= payload_range[1])]

    if entered_site == 'ALL':
        # Filter only successful launches
        successful_df = filtered_df[filtered_df["class"] == 1]
        success_counts = successful_df.groupby("Launch Site").size().reset_index(name="count")

        # Compute percentage contribution
        success_counts["percentage"] = (success_counts["count"] / success_counts["count"].sum()) * 100

        fig = px.pie(
            success_counts,
            values="percentage",
            names="Launch Site",
            title="Percentage Contribution of Each Site to Total Successful Launches"
        )
    else:
        # Filter for selected site
        site_filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
        site_success_count = site_filtered_df.groupby("class").size().reset_index(name="count")

        fig = px.pie(
            site_success_count,
            values="count",
            names="class",
            title=f"Success & Failure Counts for {entered_site}"
        )
    return fig

# Callback function to update Scatter Plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]  # Two inputs
)
def get_scatter_chart(entered_site, payload_range):
    # Filter data based on payload range
    filtered_df = spacex_df[(spacex_df["Payload Mass (kg)"] >= payload_range[0]) &
                            (spacex_df["Payload Mass (kg)"] <= payload_range[1])]

    if entered_site == 'ALL':
        # Render scatter plot for all sites
        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title="Payload vs. Launch Outcome for All Sites",
            hover_data=["Launch Site"]
        )
    else:
        # Filter for selected site
        site_filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]

        fig = px.scatter(
            site_filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title=f"Payload vs. Launch Outcome for {entered_site}",
            hover_data=["Booster Version"]
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)   
