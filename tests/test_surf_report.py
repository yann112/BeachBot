import pytest
from pathlib import Path
from sources.beachbot.surf_report import SurfReportService

def test_generate_surf_report():
    """
    Test that the SurfReportService generates a non-empty surf report.
    """
    # Constants for testing
    TEST_URL = "https://www.windguru.cz/"
    STATION_NUMBER = 500968
    
    # Get the path to the root directory
    root_path = Path(__file__).parents[1]
    
    # Construct the path to the config file
    config_path = root_path / "sources" / "wgscraper" / "scraping_config.json"
    print(f"Using config from: {config_path}")
    
    # Create the service
    service = SurfReportService(
        config_path=str(config_path),
        url=TEST_URL,
        station_number=STATION_NUMBER,
        browser="chrome",
        headless=True,
        model = "meta-llama/llama-4-maverick:free"
    )
    
    # Generate a surf report and verify it's not empty
    report = service.generate_surf_report(num_forecasts=20)
    
    # Basic assertions
    assert report is not None
    assert len(report) > 0
    print(f"Successfully generated surf report with length: {len(report)}")