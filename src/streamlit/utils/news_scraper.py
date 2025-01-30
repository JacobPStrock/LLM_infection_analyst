import os
import requests
import yaml
import json
import glob
import streamlit as st
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

cwd = os.path.dirname(os.path.abspath(__file__))
cfg_path = os.path.join(cwd,'..','..', '..', 'cfg', 'newsapi.yaml')
data_tmp = os.path.join(cwd, '..', 'data', 'tmp')

#with open(cfg_path, 'rb') as cfg_file:
#        api_key = yaml.full_load(cfg_file)['key']

class NewsScraper:
    def __init__(self, config_path: str, data_tmp: str):
        self.config_path = config_path
        self.data_tmp = data_tmp
        self.api_key = st.secrets['napi_key']
        #self.api_key = self._load_api_key()


    def _load_api_key(self) -> str:
        """Load the API key from the YAML configuration file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as cfg_file:
                return yaml.safe_load(cfg_file)['key']
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except KeyError:
            raise KeyError("The configuration file is missing the 'key' field.")
        

    def _load_api_key(self) -> str:
        """Load the API key from the YAML configuration file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as cfg_file:
                return yaml.safe_load(cfg_file)['key']
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except KeyError:
            raise KeyError("The configuration file is missing the 'key' field.")


    def get_covid_hospitalization_news(self, page: int = 1) -> Dict[str, str]:
        """Fetch articles about COVID hospitalization from the News API."""
        yesterday = datetime.now() - timedelta(days=1)
        last_week = yesterday - timedelta(days=7)

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "covid hospitalization",
            "from": last_week.strftime("%Y-%m-%d"),
            "to": yesterday.strftime("%Y-%m-%d"),
            "sortBy": "publishedAt",
            "apiKey": self.api_key,
            "pageSize": 100,
            "page": page,
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            return {article["title"]: article["url"] for article in articles if "title" in article and "url" in article}
        else:
            print(f"Failed to retrieve articles. Status code: {response.status_code}")
            return {}


    def scrape_article_with_bs4(self, url: str) -> Optional[str]:
        """Scrape the main content of a news article using BeautifulSoup."""
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = soup.find_all('p')
                return ' '.join(p.get_text() for p in paragraphs)
            else:
                print(f"Failed to retrieve article. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error occurred while scraping: {e}")
            return None


    def remove_old_files(self) -> None:
        """Remove old temporary files from the data directory."""
        old_files = glob.glob(os.path.join(self.data_tmp, "covid_hosp*"))
        for file in old_files:
            os.remove(file)


    def save_articles_to_json(self, articles: List[Dict[str, str]]) -> str:
        """Save articles to a JSON file."""
        document_name = f"covid_hospitalization_articles_{datetime.now().strftime('%Y-%m-%d')}.json"
        document_path = os.path.join(self.data_tmp, document_name)

        with open(document_path, 'w', encoding='utf-8') as file:
            json.dump(articles, file, ensure_ascii=False, indent=4)

        return document_path


    def fetch_and_save_articles(self) -> str:
        """Fetch articles, scrape their content, and save them to a JSON file."""
        self.remove_old_files()
        all_articles = []
        page = 1

        while True:
            articles = self.get_covid_hospitalization_news(page)
            if not articles:
                break

            for title, url in articles.items():
                print(f"Scraping article: {title}")
                content = self.scrape_article_with_bs4(url)
                if content:
                    all_articles.append({"title": title, "url": url, "content": content})

            page += 1

        return self.save_articles_to_json(all_articles)


if __name__ == '__main__':
    # Set resource paths
    cwd = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(cwd, '..', '..', 'cfg', 'newsapi.yaml')
    data_tmp = os.path.join(cwd, '..', '..', 'data', 'tmp')

    scraper = NewsScraper(config_path, data_tmp)
    saved_file = scraper.fetch_and_save_articles()
    print(f"Articles saved to: {saved_file}")