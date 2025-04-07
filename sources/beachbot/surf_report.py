import json
from pathlib import Path
from typing import Dict, Any, Optional

from .llm import OpenRouterClient
from ..wgscraper.sources.wgscraper.scraper import ScraperWg

class SurfReportPromptGenerator:
    """
    A class to generate prompts for an LLM to create surf reports based on
    pre-organized weather data from a scraper.
    """
    
    def __init__(self, local_beach_info: Dict[str, str], openrouter_client):
        """
        Initialize the SurfReportPromptGenerator with beach info and LLM client.
        
        Args:
            local_beach_info: Dictionary with beach information (name, location, description, best conditions)
            openrouter_client: OpenRouter client instance for making LLM requests
        """
        self.local_beach_info = local_beach_info
        self.client = openrouter_client
    
    def generate_prompt(self, forecast_data: Dict[str, Any]) -> str:
        """
        Generate a prompt for the LLM to create a surf report.
        
        Args:
            forecast_data: Dictionary containing organized forecast information from the scraper
            
        Returns:
            str: The complete prompt for the LLM
        """
        # Generate the prompt for the LLM using the pre-organized forecast data
        prompt = f"""
            Générez un rapport de surf concis pour aujourd'hui en utilisant les données suivantes :

            Prévisions : {json.dumps(forecast_data, indent=2, ensure_ascii=False)}

            Informations sur la plage locale :
            - Nom : {self.local_beach_info['name']}
            - Lieu : {self.local_beach_info['location']}
            - Description : {self.local_beach_info['description']}
            - Meilleures conditions : {self.local_beach_info['best_conditions']}

            Le rapport doit inclure :
            - Conditions de surf globales pour la journée.
            - Informations détaillées sur la vitesse du vent, la vitesse des rafales, la direction du vent, la hauteur de la houle, la période de la houle, la direction de la houle, la température, la couverture nuageuse et les précipitations.
            - Recommandations basées sur les meilleures conditions pour surfer sur ce spot.
            - Tout conseil ou avertissement supplémentaire pour les surfeurs.

            Le rapport doit être en français et concis, adapté pour être envoyé via WhatsApp. Si des conditions meilleures sont prévues dans les prochains jours, veuillez les notifier.
            """
        return prompt
    
    def get_surf_report(self, forecast_data: Dict[str, Any]) -> str:
        """
        Generate the prompt and get the surf report from the LLM.
        
        Args:
            forecast_data: Dictionary containing organized forecast information from the scraper
            
        Returns:
            str: The surf report from the LLM
        """
        prompt = self.generate_prompt(forecast_data)
        
        try:
            # Call the LLM using the OpenRouter client
            response = self.client(prompt)
            return response
        except Exception as e:
            return f"Erreur lors de la génération du rapport de surf: {str(e)}"


class SurfReportService:
    """
    A service class that coordinates scraping weather data and generating surf reports.
    """
    
    def __init__(self, config_path: str, url: str, station_number: int, browser: str = "chrome", headless: bool = True):
        """
        Initialize the SurfReportService.
        
        Args:
            config_path: Path to the scraper configuration file
            url: URL to scrape weather data from
            station_number: Station number for weather data
            browser: Browser to use for scraping
            headless: Whether to use headless browser mode
        """
        self.config_path = config_path
        self.url = url
        self.station_number = station_number
        self.browser = browser
        self.headless = headless
        
        # Beach information
        self.local_beach_info = {
            "name": "Plage du Métro",
            "location": "Tarnos, France",
            "description": "Un spot de surf populaire connu pour ses vagues constantes et son paysage magnifique.",
            "best_conditions": "Les meilleures conditions sont généralement avec des vents d'est (offshore) et une hauteur de houle d'environ 1 mètre avec une période de 9-10 secondes."
        }
        
        # Initialize OpenRouter client
        self.llm_client = OpenRouterClient()
        
        # Initialize prompt generator
        self.prompt_generator = SurfReportPromptGenerator(self.local_beach_info, self.llm_client)
    
    def generate_surf_report(self, num_forecasts: int = 20) -> str:
        """
        Generate a surf report by scraping weather data and passing it to the LLM.
        
        Args:
            num_forecasts: Number of forecasts to retrieve
            
        Returns:
            str: The generated surf report
        """
        try:
            # Scrape weather data
            with ScraperWg(
                config_path=self.config_path,
                url=self.url,
                station_number=self.station_number,
                browser=self.browser,
                headless_browser=self.headless
            ) as scraper:
                # Get forecast data
                forecast_data = scraper.get_formatted_forecast(num_forecasts)
                
                # Generate surf report using the LLM
                surf_report = self.prompt_generator.get_surf_report(forecast_data)
                
                return surf_report
        except Exception as e:
            return f"Erreur lors de la génération du rapport de surf: {str(e)}"
    
    @staticmethod
    def get_default_config_path() -> str:
        """
        Get the default path to the scraper configuration file.
        
        Returns:
            str: Path to the configuration file
        """
        # Get the path to the root directory
        root_path = Path(__file__).parents[1]
        
        # Construct the path to the config file
        config_path = root_path / "sources" / "wgscraper" / 'scraping_config.json'
        
        return str(config_path)


# Example of how to use the class
if __name__ == "__main__":
    # Constants for the example
    TEST_URL = "https://example.com/weather-data"  # Replace with your actual URL
    STATION_NUMBER = 500968
    
    # Get the default config path
    config_path = SurfReportService.get_default_config_path()
    print(f"Using config from: {config_path}")
    
    # Create the service and generate a surf report
    service = SurfReportService(
        config_path=config_path,
        url=TEST_URL,
        station_number=STATION_NUMBER,
        browser="chrome",
        headless=True
    )
    
    # Generate and print the surf report
    report = service.generate_surf_report(num_forecasts=20)
    print(report)