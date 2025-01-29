Below is a quick start if you would like to fork this repo and modify this app for your own data project. You'll need to setup your own OpenAI account and API keys to use this project. Current rates for APIs and model usage is quite reasonable for a personal project, and you can easily set limits to not worry about going over budget.

### Prerequisites
1. Install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
2. Create an account on the [OpenAI Developer Platform](https://platform.openai.com/docs/overview).
3. Create a free account on with [News API](https://newsapi.ai/?gad_source=1&gclid=Cj0KCQiA19e8BhCVARIsALpFMgH7jiIjf0qrdXkKebGhGd6SpmdOzmC7EBg5sW-Y9k7jxrHhIP1fioYaAn-hEALw_wcB)

### Setup
1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/yourproject.git
    cd yourproject
    ```

2. **Update the API Keys**:
   - Add your OpenAI API Key to _oai\_template.yaml_ & rename to _oai.yaml_
   - Add your News API Key to _newsapi\_template.yaml_ & rename to _newsapi.yaml_

3. **Setup the Python Virtual Environment**:
   - From the terminal run : 
   ```sh
   venv/Scripts/Activate
   ```

4. **Run the Streamlit App**:
   - From the terminal run : 
  ```sh
  streamlit run ./src/streamlit/app.py
  ```

### Access the Streamlit App
   - Once the container is up, open your browser and go to [http://localhost:8182](http://localhost:8182)
