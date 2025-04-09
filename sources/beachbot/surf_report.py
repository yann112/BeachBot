import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import date, timedelta

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
        today = date.today()
        tomorrow = today + timedelta(days=1)
        tomorrow_str_long = tomorrow.strftime('%A %d %B')
        
        prompt = f"""
            🏄‍♂️🤙 Report de surf **TRÈS COURT** pour demain, {tomorrow_str_long}, mode surfeur cool et **ULTRA CONCIS** pour SMS.

            Date du jour : {today.strftime('%A %d %B')}

            **Infos Spot :**
            - Nom : {self.local_beach_info['name']} ({self.local_beach_info['location']})
            - Description : {self.local_beach_info['description']}
            - {self.local_beach_info['perfect_wave_conditions']}
            - {self.local_beach_info['perfect_wind_conditions']}
            - {self.local_beach_info.get('best_tide_window', '')}

            **Avertissements :**
            - {self.local_beach_info.get('wave_height_warning', '')}
            - {self.local_beach_info.get('strong_offshore_wind_effect', '')}
            - {self.local_beach_info.get('high_tide_shorebreak_warning', '')}
            - {self.local_beach_info.get('rip_current_warning', '')}
            - **Seuil approximatif fort coefficient de marée :** ~{self.local_beach_info.get('strong_tide_approx', 85)}

            **Prévisions Brutes (pour analyse) :**
            ```
            {json.dumps(forecast_data, indent=2, ensure_ascii=False)}
            ```
 
            **Objectif :** Indique en quelques mots si ça vaut le coup de surfer demain (matin/midi/soir), en te basant sur les prévisions de vent et de houle et les infos du spot.

            **Analyse Concise :**
            - **Vent :** Indique direction et force (faible, modéré, fort). Signale si offshore (idéal si faible).
            - **Houle :** Indique hauteur et période. Signale si dans la fenêtre parfaite (0.5m-1.1m / 8s-12s). Signale si > 1.2m (engagé).
            - **Marée :** Indique niveau (haute, basse, mi-marée) si info dispo. Signale coeff > ~85 si info dispo.
 
            **Format SMS (ULTRA COURT) :**
            - **Matin :** (Qualité (Top/Moyen/Bof) + Vent + Houle + Marée (si pert.) + Alertes si besoin) ⏰
            - **Midi :** (Idem) 🍔
            - **Soir :** (Idem) 🌅 
            - **Tendance :** (Évolution houle/vent) 📈/⬇️
            - **Conclusion :** (Go/No Go) 🤙/👎 
            - **La blague a Alex** type "https://jokes-de-papa.com/", par contre reste trés serieux pour le reste du report

            **Consignes :** Très concis, style surfeur simple, infos vérifiées, emojis sparingly, jours ouvrés only. Merci ! 🤙
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
        
        self.local_beach_info = {
            "name": "Plage du Métro",
            "location": "Tarnos, France",
            "description": "Beach break landais populaire. Spot réputé pour ses pics changeants et son ambiance conviviale.",
            "perfect_wave_conditions": "🌊 **Parfait :** Houle 0.5m-1.1m / période 8s-12s.",
            "perfect_wind_conditions": "🌬️ **Parfait :** Vent faible (0-10 nœuds) et offshore (NE à SE).",
            "wave_height_warning": "⚠️ **Attention :** Houle > 1.2m = conditions engagées (vagues creuses et puissantes).",
            "strong_offshore_wind_threshold_knots": 15,
            "strong_offshore_wind_effect": f"💨 **Attention :** Vent offshore > {15} nœuds = take-off difficile (vagues trop creuses).",
            "strong_tide_approx": 100,
            "high_tide_shorebreak_warning": "⚠️ **Attention :** Marée haute (coeff > ~85) = shorebreak dangereux.",
            "rip_current_warning": "⚠️ **Attention :** Marée descendante (coeff > ~85) = forts courants/baïnes.",
            "best_tide_window": "🏄‍♂️ **Meilleur à mi-marée.**"
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