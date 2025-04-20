import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import date

from .llm import OpenRouterClient
from ..wgscraper.sources.wgscraper.scraper import ScraperWg

class SurfReportPromptGenerator:
    """
    A class to generate prompts for an LLM to create surf reports based on
    pre-organized weather data from a scraper.
    """
    
    def __init__(self, station_infos: Dict[str, str], openrouter_client):
        """
        Initialize the SurfReportPromptGenerator with beach info and LLM client.
        
        Args:
            station_infos: Dictionary with beach information (name, location, description, best conditions)
            openrouter_client: OpenRouter client instance for making LLM requests
        """
        self.station_infos = station_infos
        self.client = openrouter_client
    
    def generate_prompt(self, forecast_data: Dict[str, Any]) -> str:
        """
        Generate a prompt for the LLM to create a surf report.
        
        Args:
            forecast_data: Dictionary containing organized forecast information from the scraper
            
        Returns:
            str: The complete prompt for the LLM
        """
        today = date.today()
        
        prompt = f"""
            Today : {today.strftime('%A %d %B')}

            **Station Infos :**
            {self.station_infos}

            **Raw Forecast(for analysis) :**
            ```
            {json.dumps(forecast_data, indent=2, ensure_ascii=False)}
            ```
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
    
    def __init__(
        self,
        station_number: int,
        url: str = None,
        browser: str = None,
        headless: bool = None,
        model: str = None,
        scrapper_config_path: str = None,
        beachbot_config_path: str = None,
        logger: logging.getLogger = None
            ):
        """
        Initialize the SurfReportService.
        
        Args:
            scrapper_config_path: Path to the scraper configuration file
            beachbot_config_path: Path to the beachbot config
            url: URL to scrape weather data from
            station_number: Station number for weather data
            browser: Browser to use for scraping
            headless: Whether to use headless browser mode
        """
        self.logger = logger or logging.getLogger(__file__)
        self.scrapper_config_path = scrapper_config_path or (Path(__file__).parents[1] / 'wgscraper' / 'scraping_config.json')
        self.beachbot_config = self._read_beachbot_config(beachbot_config_path)
        self.url = url or "https://www.windguru.cz/"
        self.station_number = station_number
        self.browser = "chrome" or browser
        self.headless = True or headless
        self.model=model
        
        self.station_infos= self.beachbot_config["station_number"][str(self.station_number)]
        # Initialize OpenRouter client
        self.llm_client = OpenRouterClient(model=self.model)
        
        # Initialize prompt generator
        self.prompt_generator = SurfReportPromptGenerator(self.station_infos, self.llm_client)
    
    def _read_beachbot_config(self, config_path):
        default_path = Path(__file__).parents[2] / 'bot_config.json'
        file_path = config_path if config_path is not None else default_path
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        return config_data

    def generate_surf_report(self, num_forecasts: int = None) -> str:
        """
        Generate a surf report by scraping weather data and passing it to the LLM.
        
        Args:
            num_forecasts: Number of forecasts to retrieve
            
        Returns:
            str: The generated surf report
        """
        try:
            self.logger.info("launching Scraper")
            with ScraperWg(
                logger=self.logger,
                config_path=self.scrapper_config_path,
                url=self.url,
                station_number=self.station_number,
                browser=self.browser,
                headless_browser=self.headless
            ) as scraper:
                self.logger.info("launching formatter")
                forecast_data = scraper.get_formatted_forecast(num_forecasts)
                self.logger.info(forecast_data)
                # Generate surf report using the LLM
                surf_report = self.prompt_generator.get_surf_report(forecast_data)
                self.logger.info(surf_report)
                return surf_report
        except Exception as e:
            self.logger.error(e)
            return f"Erreur lors de la génération du rapport de surf: {str(e)}"
