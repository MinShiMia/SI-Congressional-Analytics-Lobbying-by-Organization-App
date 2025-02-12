import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
import io
import requests


# Set the page layout to 'wide'
st.set_page_config(layout="wide")


# Load the data from GitHub
# ssl._create_default_https_context = ssl._create_unverified_context  # Disable SSL verification
frequency_by_org_path = "https://raw.githubusercontent.com/MinShiMia/SI-Congressional-Analytics-Lobbying-by-Organization-App/main/lda_quarterly_frequency_by_client_organization_over_time_top_100.csv"
total_expenses_by_org_path = "https://raw.githubusercontent.com/MinShiMia/SI-Congressional-Analytics-Lobbying-by-Organization-App/main/lda_quarterly_total_lobbying_expenses_by_client_organization_over_time_top_100.csv"
avg_expenses_by_org_path = "https://raw.githubusercontent.com/MinShiMia/SI-Congressional-Analytics-Lobbying-by-Organization-App/main/lda_quarterly_avg_lobbying_expenses_by_client_organization_over_time_top_100.csv"


response1 = requests.get(frequency_by_org_path)
response1.raise_for_status()  # Raise an error for bad status codes (e.g., 404, 403)
csv_data1 = response1.content.decode('utf-8')
frequency_by_org = pd.read_csv(io.StringIO(csv_data1))

response2 = requests.get(total_expenses_by_org_path)
response2.raise_for_status()  # Raise an error for bad status codes (e.g., 404, 403)
csv_data2 = response2.content.decode('utf-8')
total_expenses_by_org = pd.read_csv(io.StringIO(csv_data2))

response3 = requests.get(avg_expenses_by_org_path)
response3.raise_for_status()  # Raise an error for bad status codes (e.g., 404, 403)
csv_data3 = response3.content.decode('utf-8')
avg_expenses_by_org = pd.read_csv(io.StringIO(csv_data3))




# Sidebar for filters
st.sidebar.header("Filters")

# Year Slider (min and max year in the dataset)
min_year = int(frequency_by_org['Year'].min())
max_year = int(frequency_by_org['Year'].max())
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Quarter Filter (ordered numerically)
quarter_filter = st.sidebar.multiselect(
    "Select Quarter",
    options=sorted(frequency_by_org['Quarter'].unique()),  # Sort quarters numerically
    default=sorted(frequency_by_org['Quarter'].unique())
)

# Organization Filter (sorted alphabetically)
organization_filter = st.sidebar.multiselect(
    "Select Organization",
    options=sorted(frequency_by_org['client_name'].unique()),  # Sort organization names alphabetically
    default=sorted(frequency_by_org['client_name'].unique())
)


# Main Content - Organization
st.header("Organization Data")

# Top-N Organization Slider
top_n = st.sidebar.slider(
    "Select Top-N Organizations by Frequency",
    min_value=10,
    max_value=100,
    value=50,
    step=10
)

# Function to filter and sort data
def filter_and_sort_frequency_data(df, year_range, quarter_filter, org_filter, top_n):
    df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    if quarter_filter:
        df = df[df['Quarter'].isin(quarter_filter)]
    if org_filter:
        df = df[df['client_name'].isin(org_filter)]
    df = df.groupby('client_name').agg({'LDA_frequency': 'sum'}).reset_index()
    df = df.sort_values(by='LDA_frequency', ascending=False).head(top_n)
    return df


# Function to filter and sort data
def filter_and_sort_total_expenses_data(df, year_range, quarter_filter, org_filter, top_n):
    df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    if quarter_filter:
        df = df[df['Quarter'].isin(quarter_filter)]
    if org_filter:
        df = df[df['client_name'].isin(org_filter)]
    df = df.groupby('client_name').agg({'LDA_lobbying_expenses': 'sum'}).reset_index()
    df = df.sort_values(by='LDA_lobbying_expenses', ascending=False).head(top_n)
    return df


# # Function to filter and sort data
# def filter_and_sort_avg_expenses_data(df, year_range, quarter_filter, org_filter, top_n):
#     df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
#     if quarter_filter:
#         df = df[df['Quarter'].isin(quarter_filter)]
#     if org_filter:
#         df = df[df['client_name'].isin(org_filter)]
#     df = df.groupby('client_name').agg({'LDA_lobbying_expenses': 'avg'}).reset_index()
#     df = df.sort_values(by='LDA_lobbying_expenses', ascending=False).head(top_n)
#     return df


# Filter and sort the frequency data
filtered_frequency = filter_and_sort_frequency_data(frequency_by_org, year_range, quarter_filter, organization_filter, top_n)

# Filter and sort the frequency data
filtered_total_expenses = filter_and_sort_total_expenses_data(total_expenses_by_org, year_range, quarter_filter, organization_filter, top_n)

# # Filter and sort the frequency data
# filtered_avg_expenses = filter_and_sort_avg_expenses_data(avg_expenses_by_org, year_range, quarter_filter, organization_filter, top_n)

## Plot Frequency by Organization using plotly
st.subheader(f"Frequency of Activities by Top {top_n} Organizations")

# Create interactive bar plot
fig = px.bar(
    filtered_frequency,
    x='client_name',
    y='LDA_frequency',
    title=f'Top {top_n} Organizations by Frequency',
    labels={'client_name': 'Organization', 'LDA_frequency': 'LDA Frequency'},
    color='LDA_frequency',
    color_continuous_scale='teal',
    height=800
)

# Customize the layout for better readability
fig.update_layout(
    xaxis_tickangle=-45,
    xaxis_title='Organization',
    yaxis_title='LDA Frequency',
    margin=dict(l=40, r=40, t=40, b=80),
    hovermode='x'
)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Display Filtered Data
st.subheader("Filtered Frequency Data")
st.dataframe(filtered_frequency)


# Plot Total Lobbying Expenses by Organization using plotly
st.subheader(f"Total Lobbying Expenses by Top {top_n} Organizations")

# Create an interactive bar plot
fig = px.bar(
    filtered_total_expenses,
    x='client_name',
    y='LDA_lobbying_expenses',
    color='LDA_lobbying_expenses',
    color_continuous_scale='sunset',
    title=f'Top {top_n} Organizations by Total Lobbying Expenses',
    labels={'client_name': 'Organization', 'LDA_lobbying_expenses': 'Total Expenses (in Millions)'},
    height=600
)

# Customize the layout for better readability
fig.update_layout(
    xaxis_tickangle=-45,
    xaxis_title='Organization',
    yaxis_title='Total Lobbying Expenses (in Millions)',
    margin=dict(l=40, r=40, t=40, b=80),
    hovermode='x'
)

# Display the interactive plot in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Display Filtered Data
st.subheader("Filtered Total Lobbying Expenses Data")
st.dataframe(filtered_total_expenses)


#
# # Plot Total Lobbying Expenses by Organization
# st.subheader(f"Average Lobbying Expenses by Top {top_n} Organizations")
# plt.figure(figsize=(10, 6))
# plt.bar(filtered_avg_expenses['client_name'], filtered_avg_expenses['LDA_lobbying_expenses'], color='skyblue')
# plt.xticks(rotation=45, ha='right')
# plt.xlabel('Organization')
# plt.ylabel('LDA_lobbying_expenses')
# plt.title(f'Top {top_n} Organizations by Average Lobbying Expenses')
# st.pyplot(plt)
#
# # Display Filtered Data
# st.subheader("Filtered Average Lobbying Expenses Data")
# st.dataframe(filtered_avg_expenses)
#

# Footer
st.write("Data source: S3 Bucket")