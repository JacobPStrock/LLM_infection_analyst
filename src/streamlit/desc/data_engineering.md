This section provides an overview of the data engineering techniques employed in the system to fetch and process real-time news stories from NewsAPI and epidemiological data from the CDC via the Delphi Epidata API.

### News Data Retrieval
The system dynamically retrieves current news stories from NewsAPI, which are then processed to serve as the foundation for generating insights:

- **API Integration :** News stories are fetched in real-time using NewsAPI, ensuring the content is current and relevant.
- **Data Handling :** Stories are parsed and necessary attributes like headlines, content, and publication dates are extracted and stored for further processing.

### COVID Data Acquisition
We obtain real-time epidemiological data directly from the CDC through the Delphi Epidata API. This process is detailed in the following steps:

- **API Usage :** The system makes requests to the Delphi Epidata API to fetch the latest available data on flu and COVID-like illness surveillance.
- **Date Range Handling :** Data for specific epidemiological weeks (epiweeks) is requested, with the system calculating the range based on the current date to ensure the most recent data is retrieved.
- **Data Transformation :** Retrieved data is transformed into a structured format, making it suitable for analysis and integration into the system's data pipeline.


### Data Storage and Access
Data fetched from both NewsAPI and the CDC is stored locally to facilitate quick access and processing:

- **Temporary Storage :** News articles and COVID data are initially stored in a temporary directory, which is periodically cleaned to ensure data freshness and relevance.
- **Reference Data Management :** Static reference data, such as state population statistics, is stored separately and utilized to enrich the COVID data with demographic insights.

### On-Demand Data Refresh
To manage computational resources efficiently and avoid unnecessary data fetches, the system employs an on-demand data refresh strategy:

- **Streamlit Interface :** Users can trigger data updates directly from the Streamlit interface via a 'Refresh Data' button. This ensures that the dashboard displays the most current information without the need for continuous background processing.
- **Session State Management :** Upon refreshing, the new data is loaded and saved to Streamlit’s session state. This approach ensures that the updated state is retained across app refreshes and during the user session, enhancing the user experience by providing continuity and speed in data interaction.

### Automated Data Processing
Once new data is fetched, it is processed automatically to update the system's insights:

- **Data Preprocessing :** New data goes through a cleaning and preprocessing pipeline to match the system's requirements for analysis.
- **Information Retrieval Setup :** For the RAG system, news data is embedded using machine learning models and stored in a vector database for quick retrieval based on semantic similarity to user queries.

### Conclusion
Our data engineering practices are designed to ensure that the system remains responsive and current, providing users with reliable and up-to-date information. The integration of on-demand refresh capabilities with robust data processing pipelines allows for efficient resource usage while maintaining high data quality and system performance.