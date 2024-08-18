"""
import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

# Function to load JSON data from GitHub
def load_json_from_github(url):
    response = requests.get(url)
    return response.json()

# URLs to your GitHub raw JSON files
ford_url = 'https://raw.githubusercontent.com/thebnbrkr/finance/main/Ford.json'
gm_url = 'https://raw.githubusercontent.com/thebnbrkr/finance/main/GM.json'

# Load the data
ford_data = load_json_from_github(ford_url)
gm_data = load_json_from_github(gm_url)

# Function to extract US GAAP values and descriptions
def extract_us_gaap_values(data):
    us_gaap_values = {}
    us_gaap_descriptions = {}
    
    if 'facts' in data:
        for key, value in data['facts'].get('us-gaap', {}).items():
            if 'units' in value:
                us_gaap_values[key] = value['units']
            if 'description' in value:  # Add description if available
                us_gaap_descriptions[key] = value['description']
    return us_gaap_values, us_gaap_descriptions

# Extract the US GAAP values and descriptions
ford_us_gaap, ford_us_gaap_desc = extract_us_gaap_values(ford_data)
gm_us_gaap, gm_us_gaap_desc = extract_us_gaap_values(gm_data)

# Find common US GAAP keys
common_us_gaap_keys = set(ford_us_gaap.keys()).intersection(set(gm_us_gaap.keys()))

# Function to align data based on dates
def align_dates(ford_data, gm_data):
    ford_df = pd.DataFrame(ford_data)
    gm_df = pd.DataFrame(gm_data)
    
    ford_df['end'] = pd.to_datetime(ford_df['end'])
    gm_df['end'] = pd.to_datetime(gm_df['end'])
    
    merged_df = pd.merge(ford_df, gm_df, on='end', suffixes=('_ford', '_gm'), how='inner')
    return merged_df

# Select key US GAAP metrics to display
st.title("Ford vs GM US GAAP Metrics Comparison")
metrics = list(common_us_gaap_keys)
selected_metric = st.selectbox("Select a metric to compare", metrics)

# Show the description of the selected metric
if selected_metric:
    description = ford_us_gaap_desc.get(selected_metric, 'No description available')
    
    # Display the description
    st.subheader(f"Description: {description}")

    # Plot the selected metric
    ford_vals = ford_us_gaap[selected_metric].get('USD', [])
    gm_vals = gm_us_gaap[selected_metric].get('USD', [])
    
    if ford_vals and gm_vals:
        merged_data = align_dates(ford_vals, gm_vals)
        
        if not merged_data.empty:
            #st.write(f"Comparison of {selected_metric}")
            fig, ax = plt.subplots()
            ax.plot(merged_data['end'], merged_data['val_ford'], label='Ford')
            ax.plot(merged_data['end'], merged_data['val_gm'], label='GM')
            ax.set_xlabel('Date')
            ax.set_ylabel('Value (USD)')
            ax.legend()
            ax.set_title(f'Comparison of {selected_metric}')
            st.pyplot(fig)
"""

import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

# Function to load JSON data from GitHub
def load_json_from_github(url):
    response = requests.get(url)
    return response.json()

# URLs to your GitHub raw JSON files (add more companies as needed)
company_urls = {
    'Ford': 'https://raw.githubusercontent.com/thebnbrkr/finance/main/Ford.json',
    'GM': 'https://raw.githubusercontent.com/thebnbrkr/finance/main/GM.json',
    # Add additional companies here
    'Tesla': 'https://raw.githubusercontent.com/yourusername/finance/main/Tesla.json',
    'Lucid': 'https://raw.githubusercontent.com/yourusername/finance/main/Lucid.json',
}

# Function to extract US GAAP values and descriptions
def extract_us_gaap_values(data):
    us_gaap_values = {}
    us_gaap_descriptions = {}
    
    if 'facts' in data:
        for key, value in data['facts'].get('us-gaap', {}).items():
            if 'units' in value:
                us_gaap_values[key] = value['units']
            if 'description' in value:  # Add description if available
                us_gaap_descriptions[key] = value['description']
    return us_gaap_values, us_gaap_descriptions

# Function to load data for selected companies
def load_company_data(selected_companies):
    company_data = {}
    company_descriptions = {}
    for company in selected_companies:
        data = load_json_from_github(company_urls[company])
        us_gaap_values, us_gaap_descriptions = extract_us_gaap_values(data)
        company_data[company] = us_gaap_values
        company_descriptions[company] = us_gaap_descriptions
    return company_data, company_descriptions

# Function to align data based on dates
def align_dates(data_list):
    merged_df = pd.DataFrame()
    
    for company, data in data_list.items():
        df = pd.DataFrame(data)
        df['end'] = pd.to_datetime(df['end'])
        if merged_df.empty:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on='end', suffixes=(False, f'_{company}'), how='inner')
    
    return merged_df

# App title
st.title("Car Companies US GAAP Metrics Comparison")

# Select companies to compare (up to 4)
companies = list(company_urls.keys())
selected_companies = st.multiselect("Select up to 4 companies to compare", companies, default=companies[:2], max_selections=4)

if len(selected_companies) > 0:
    # Load data for the selected companies
    company_data, company_descriptions = load_company_data(selected_companies)

    # Find common US GAAP keys across all selected companies
    common_us_gaap_keys = set.intersection(*[set(data.keys()) for data in company_data.values()])
    
    if len(common_us_gaap_keys) > 0:
        # Select US GAAP metric to compare
        metrics = list(common_us_gaap_keys)
        selected_metric = st.selectbox("Select a metric to compare", metrics)
        
        # Show the description of the selected metric
        description = company_descriptions[selected_companies[0]].get(selected_metric, 'No description available')
        st.subheader(f"Description: {description}")
        
        # Prepare the data for plotting
        data_list = {}
        for company in selected_companies:
            if selected_metric in company_data[company]:
                data_list[company] = company_data[company][selected_metric].get('USD', [])
        
        # Align dates and plot the data
        merged_data = align_dates(data_list)
        
        if not merged_data.empty:
            st.write(f"Comparison of {selected_metric}")
            fig, ax = plt.subplots()
            for company in selected_companies:
                ax.plot(merged_data['end'], merged_data[f'val_{company}'], label=company)
            ax.set_xlabel('Date')
            ax.set_ylabel('Value (USD)')
            ax.legend()
            ax.set_title(f'Comparison of {selected_metric}')
            st.pyplot(fig)
    else:
        st.write("No common US GAAP metrics found across the selected companies.")
else:
    st.write("Please select at least one company.")
