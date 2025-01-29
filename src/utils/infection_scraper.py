from delphi_epidata import Epidata
from datetime import datetime, timedelta
import pandas as pd
import glob
import os
import yaml
import logging
from typing import List, Dict, Any


class FluDataHandler:
    """Handles the retrieval, processing, and storage of flu-related data."""


    def __init__(self, config_path: str, data_tmp: str, data_ref: str):
        self.config_path = config_path
        self.data_tmp = data_tmp
        self.data_ref = data_ref
        self.logger = logging.getLogger(__name__)  # Module-level logger
        self._configure_logger()

    def _configure_logger(self):
        """Set up logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(os.path.join(self.data_tmp, "flu_data_handler.log")),
                logging.StreamHandler()
            ]
        )

    @staticmethod
    def get_fluview_data(start_epiweek: int, end_epiweek: int) -> List[Dict[str, Any]]:
        """
        Fetch COVID flu data for a range of epiweeks from the FluView API.

        Args:
            start_epiweek (int): The start epiweek (e.g., 202301 for the 1st week of 2023).
            end_epiweek (int): The end epiweek.

        Returns:
            List[Dict[str, Any]]: List of retrieved records, or an empty list if the API call fails.
        """
        regions = [
            'cen1', 'cen2', 'cen3', 'cen4', 'cen5', 'cen6', 'cen7', 'cen8', 'cen9'
        ]
        states = [
            "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id", "il", "in", 
            "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", 
            "nh", "nj", "nm", "ny_minus_jfk", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", 
            "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy"
        ]
        all_locations = regions + states

        res = Epidata.fluview(all_locations, Epidata.range(start_epiweek, end_epiweek))

        if res['result'] == 1:
            logging.info(f"Success: Retrieved {len(res['epidata'])} records.")
            return res['epidata']
        else:
            logging.error(f"Error retrieving flu data: {res.get('message', 'Unknown error')}")
            return []


    def load_cdc_regions(self) -> Dict[str, str]:
        """
        Load CDC region mappings from a YAML file.

        Returns:
            Dict[str, str]: Mapping of region codes to region names.
        """
        try:
            with open(os.path.join(self.data_ref, 'cdc_regions.yaml'), 'r', encoding='utf-8') as file:
                cdc_regions = yaml.safe_load(file)
            return {key.upper(): value['name'].upper() for key, value in cdc_regions.items()}
        except FileNotFoundError:
            self.logger.error("CDC regions file not found.")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing CDC regions YAML file: {e}")
            raise


    def process_and_save_flu_data(self, start_epiweek: int, end_epiweek: int) -> str:
        """
        Retrieve, process, and save flu data to a CSV file.

        Args:
            start_epiweek (int): The start epiweek.
            end_epiweek (int): The end epiweek.

        Returns:
            str: Path to the saved CSV file.
        """
        flu_data = self.get_fluview_data(start_epiweek, end_epiweek)

        if not flu_data:
            self.logger.warning("No flu data retrieved.")
            raise RuntimeError("No flu data retrieved.")

        df = pd.DataFrame(flu_data)
        df['region'] = df['region'].str.upper()

        region_name_map = self.load_cdc_regions()
        df['region_name'] = df['region'].map(region_name_map)

        csv_filename = os.path.join(
            self.data_tmp, f"fluview_data_{datetime.now().strftime('%Y-%m-%d')}.csv"
        )
        df.to_csv(csv_filename, index=False)
        self.logger.info(f"Flu data saved to {csv_filename}.")
        return csv_filename


    def remove_old_files(self) -> None:
        """Remove outdated flu data files from the temporary directory."""
        old_files = glob.glob(os.path.join(self.data_tmp, "fluview_data*"))
        for file in old_files:
            os.remove(file)
            self.logger.info(f"Removed file: {file}")


    def update_infection_data(self) -> str:
        """
        Update flu data by removing old files and fetching the latest data.

        Returns:
            str: Path to the updated data file.
        """
        self.remove_old_files()

        today = datetime.now()
        year, week, _ = today.isocalendar()
        current_epiweek = int(f"{year}{week:02}")
        start_epiweek = current_epiweek - 200

        return self.process_and_save_flu_data(start_epiweek, current_epiweek)


if __name__ == "__main__":
    # Set resource paths
    cwd = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(cwd, '..', '..', 'cfg', 'newsapi.yaml')
    data_tmp = os.path.join(cwd, '..', '..', 'data', 'tmp')
    data_ref = os.path.join(cwd, '..', '..', 'data', 'ref')

    # Initialize the flu data handler
    flu_handler = FluDataHandler(cfg_path, data_tmp, data_ref)

    # Change working directory to temporary data folder
    os.chdir(data_tmp)

    # Update infection data
    updated_file = flu_handler.update_infection_data()
    print(f"Updated flu data saved to: {updated_file}")

'''
from delphi_epidata import Epidata
from datetime import datetime, timedelta
import pandas as pd
import glob
import os
import yaml

cwd = os.path.abspath(__file__)
cfg_path = os.path.join(cwd,'..','..', '..', 'cfg', 'newsapi.yaml')
data_tmp = os.path.join(cwd, '..', '..', '..', 'data', 'tmp')
data_ref = os.path.join(cwd, '..', '..', '..', 'data', 'ref')


# Function to get both state and region COVID flu data for a given range of epiweeks
def get_fluview_data(start_epiweek, end_epiweek):
    # Define all regions to get data for
    regions = [
        'cen1', 'cen2', 'cen3', 'cen4', 'cen5', 'cen6', 'cen7', 'cen8', 'cen9'
    ]
    states =  [
        "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id", "il", "in", 
        "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", 
        "nh", "nj", "nm", "ny_minus_jfk", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", 
        "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy"
    ]
    
    # Combine regions and states into one list
    all_locations = regions + states

    # Fetch data from the FluView API
    res = Epidata.fluview(all_locations, Epidata.range(start_epiweek, end_epiweek))

    # Check for success
    if res['result'] == 1:
        print(f"Success: Retrieved {len(res['epidata'])} records")
        return res['epidata']
    else:
        print(f"Error: {res['message']}")
        return []


# Main function to get and save flu data for all regions and states
def main():
    # Calculate current epiweek (year and week number)
    today = datetime.now()
    year, week, _ = today.isocalendar()
    current_epiweek = int(f"{year}{week:02}")

    # Set the start and end epiweek (last 10 weeks)
    start_epiweek = current_epiweek - 200
    end_epiweek = current_epiweek

    # Get flu data for all regions and states
    flu_data = get_fluview_data(start_epiweek, end_epiweek)

    # Convert the flu data to a DataFrame
    df = pd.DataFrame(flu_data)
    df['region'] = df['region'].str.upper()

    # Add region
    # Parse the YAML data
    with open(os.path.join(data_ref, 'cdc_regions.yaml'), 'rb') as file:
        cdc_regions = yaml.safe_load(file)

    # Create a dictionary mapping region codes to region names
    region_name_map = {key.upper(): value['name'].upper() for key, value in cdc_regions.items()}

    # Assume df is your DataFrame with a 'region' column
    df['region_name'] = df['region'].map(region_name_map)

    # Save the DataFrame to a CSV file
    csv_filename = f"fluview_data_{datetime.now().strftime('%Y-%m-%d')}.csv"
    df.to_csv(csv_filename, index=False)
    #print(f"Flu data saved to {csv_filename}")
    return csv_filename


def remove_old_files():
     avail_data = glob.glob(r'fluview_data*', root_dir = data_tmp)
     for file in avail_data:
         os.remove(os.path.join(data_tmp, file))


# to be used in streamlit app for updates
def update_infection_data():
    # cleanup old files
    remove_old_files()
    # get new data
    file_name = main()

    #return new file name
    return file_name

if __name__ == "__main__":

    os.chdir(data_tmp)

    main()
'''