import streamlit as st
import sys
import os
import pandas as pd
import altair as alt
import plotly.express as px
from datetime import datetime
import warnings
import re
import glob

# supress warnings from printing on app
warnings.filterwarnings('ignore')

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cwd, 'utils'))
import llm_rag as lm
from infection_scraper import FluDataHandler

st.set_page_config(layout="wide")

# Add an official-looking image to the app
banner = os.path.join(cwd,'data', 'assets', 'header_image_chat2.jpg')
inf_data = os.path.join(cwd, 'data', 'tmp')
ref_data = os.path.join(cwd, 'data', 'ref')
pop_data = os.path.join(cwd, 'data', 'ref', 'state_populations.csv')
images   = os.path.join(cwd, 'data', 'assets')
cfg_dir  = os.path.join(cwd, 'cfg')
 
# Sidebar for navigation
st.sidebar.image(os.path.join(images,'ds_portfolio_logo_v2.png'))
st.sidebar.title("Navigation")
option = st.sidebar.radio("Select a tab:", ("About",
                                            "Infection Cases & Rates",
                                            "COVID-19 LLM News Analyst",
                                            #"Hospitalization Burden Forecasts"
                                            ))


# Prepare the model (loading data, creating embeddings, setting up retriever and chain)
# retrieval_qa_chain = prepare_model()

# Home tab
# Map & Forecasts tab
if option == "Infection Cases & Rates":
    

    st.title('COVID Map & Forecasts')
    
    st.write("Infection counts by state from the CDC. Rates are calculated relative to latest cencus population counts by state.")

    # Refresh data on command to avoid expense on pipelines
    if st.button('Refresh Data'):
        # Rerun data scraper
        ih = FluDataHandler(cfg_dir, inf_data, ref_data)
        inf_file = ih.update_infection_data()
        df =  pd.read_csv(inf_file) # Load or refresh your data here
        st.session_state['data'] = df #Save to session state which will persist
        
    else:
        if 'data' not in st.session_state:
            # find the most recent records
            avail_data = glob.glob(r'fluview_data*', root_dir = inf_data)
            data_dates = [re.search(r'\d{4}-\d{2}-\d{2}', x).group() for x in avail_data]
            max_date = max(data_dates)
            ind = data_dates.index(max_date)
            most_recent = avail_data[ind]

            # Load
            df =  pd.read_csv(os.path.join(inf_data, most_recent))
            st.session_state['data'] =  df

    # Load COVID-19 data
    if os.path.exists(inf_data):
        #df = pd.read_csv(inf_data)
        df = st.session_state['data']
        population_df = pd.read_csv(pop_data)
        df = df.merge(population_df, left_on='region', right_on='state_abbreviation', how='left')
        df['infection_rate'] = (df['num_ili'].astype(float) / df['Pop.2023'].astype(float)) * 100000  # Infection rate per 100,000 people

        # Convert epiweek to a start date of the week
        df['year'] = df['epiweek'].astype(str).str[:4].astype(int)
        df['week'] = df['epiweek'].astype(str).str[4:].astype(int)
        df['date'] = df.apply(lambda x: datetime.strptime(f"{x['year']}-W{x['week']}-1", "%Y-W%W-%w"), axis=1)
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')

        # Define the color range for consistency
        num_ili_max = df['num_ili'].max()
        infection_rate_max = df['infection_rate'].max()

        # Display the animated choropleth maps of COVID-19 infections over time side by side
        st.write("### Animated COVID-19 Infections and Infection Rate by Region Over Time")
        # Define a radio button for selecting the data type
        data_type = st.radio(
            "Select Data Type",
            ('COVID-19 Infection Rates', 'COVID-19 Cases')
        )
        col1, col2, col3 = st.columns([1, 3, 1])
        if data_type == 'COVID-19 Infection Rates':
            with col2:
                fig = px.choropleth(df, locations='region', locationmode='USA-states', color='infection_rate',
                                    color_continuous_scale='Blues', scope='usa',
                                    animation_frame='date',
                                    range_color=(0, infection_rate_max),
                                    labels={'infection_rate': 'Infection Rate per 100,000'},
                                    title='COVID-19 Infection Rate by State Over Time')
                
        else:
            with col2:
                fig = px.choropleth(df, locations='region', locationmode='USA-states', color='num_ili',
                                    color_continuous_scale='Reds', scope='usa',
                                    animation_frame='date',
                                    range_color=(0, num_ili_max),
                                    labels={'num_ili': 'COVID-19 Cases'},
                                    title='COVID-19 Infections by Region Over Time')
        fig.update_layout(title_text="title", margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=700)        
        st.plotly_chart(fig, use_container_width=True)


        # Display the stacked line plot of COVID-19 infections over time by region
        st.write("### COVID-19 Infections Over Time by Region")
        df_r = df[~df['region_name'].isnull()]
        fig_line = px.area(df_r, x='date', y='num_ili', color='region_name',
                           #title='COVID-19 Infections Over Time by State',
                           labels={'num_ili': 'COVID-19 Cases', 'epiweek': 'Epiweek', 'region': 'Region'})
        st.plotly_chart(fig_line)
        
    else:
        st.error("Data file not found. Please upload the COVID-19 data.")


# COVID-19 Analysis tab
elif option == "COVID-19 LLM News Analyst":

    llm = lm.LLMRag()
    llm.prep_retrieval()

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # Set up the Streamlit app title
        st.title('AI COVID News Explorer')
        st.image(banner, caption='Stay up-to-date on the latest, with the AI COVID assistant', use_container_width=True)

        # Refresh data on command to avoid expense on pipelines
        if st.button('Refresh Data'):
            llm.update_vectordb()

        # Add a text input for user queries
        user_query = st.text_input('Enter your questions about recent COVID-19 trends:')

        # Add a button to run the query
        if st.button('Run Query'):
            if user_query:
                # Run the query using the prepared model
                result = llm.run_query(user_query)

                # Display the answer
                st.write("### Answer:")
                st.write(result['result'])

                # Display the source documents
                st.write("### Source Documents:")
                for doc in result['source_documents']:
                    st.write(doc)
            else:
                st.warning('Please enter a query to get results.')
        
        # Footer text
        st.write("Questions are answered by ChatGPT's gpt-3.5-turbo model with access to international news reports on COVID hospitalizations. Source documents provided are raw text from news stories matched as the highest similarity through semantic search.")


# About tab
elif option == "About":

    # Top Logo Banner
    st.write('# AI COVID + Flu Analyst')
    st.image(os.path.join(images, 'logo_banner.png'), width=800)

    # Overview
    #st.write('## Overview')
    over_doc = os.path.join(cwd, 'desc', 'overview.md')
    with open(over_doc, 'r', encoding='utf-8') as f:
        over_cont = f.read()
    with st.expander('Overview'):
        st.markdown(over_cont)

    # Description & Quick Start
    quick_start = os.path.join(cwd,'desc', 'quick_start.md')
    with open(quick_start, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    with st.expander('Quick Start Guide'):  
        st.markdown(readme_content)

    # LLM & RAG description
    #st.write("-------------------")
    #st.write("## Interactive News Analyst \n ### (LLM Retrieval-Augmented Generation)")
    llm_desc = os.path.join(cwd, 'desc', 'llm_rag_desc.md')
    with open(llm_desc, 'r', encoding='utf-8') as f:
        llm_desc_cont = f.read()
    with st.expander('LLM Retrieval-Augmented Generation'): 
        st.markdown(llm_desc_cont)
        st.image(os.path.join(images, 'LLM_diagram.png'))
    
    # Data Engineering
    #st.write("-------------------")
    #st.write("## Data Engineering")
    #st.image(os.path.join(images, 'LLM_diagram.png'))
    de_desc = os.path.join(cwd, 'desc', 'data_engineering.md')
    with open(de_desc, 'r', encoding='utf-8') as f:
        de_desc_cont = f.read()
    with st.expander('Data Engineering'):
        st.markdown(de_desc_cont)

    # Forecasting
    #st.write("-------------------")
    #st.write("## Forecasting")
    #st.image(os.path.join(images, 'LLM_diagram.png'))
    pred_desc = os.path.join(cwd, 'desc', 'pred_forecast_desc.md')
    with open(pred_desc, 'r', encoding='utf-8') as f:
        pred_desc_cont = f.read()
    with st.expander('Forecasting'):
        st.markdown(pred_desc_cont)