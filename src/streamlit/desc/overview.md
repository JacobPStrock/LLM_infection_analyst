This is a streamlit app that leverages millions of news sources, along with up-to-date CDC data, an LLM RAG architecture, and multiple forecasting methods to provide a monitoring dashboard for flu and COVID infections. The app includes 3 major components:

1. __Descriptive & Predictive Infection Dashboard__ : Latest infection data in the US from the CDC are combined with Census geo-spatial data to map infections by total number and rate. Infection numbers are forecasted with ARIMA models to provide insight on bulk numbers by state and region.

2. __Interactive AI News Analyst__ : Leverages a LLM RAG deployment provides users the opportunity to interactively ask questions on about the latest news on COVID and hospitalizations in the US and around the world.

3. __Forecasted Hospital Burden__ : The potential impact on each state's hospital systems is predicted by forecasting infections, hospitalization rates, and hospital capacity. Results are used to predict the burden of flu and COVID patients on the total capacity of hospital beds, and provide warning on capacity issues.
