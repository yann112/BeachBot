# BeachBot

**"A bot to generate surf reports using meteo data."**

This bot scrapes meteorological data to generate surf reports. It also utilizes a submodule for specific functionalities.

## Prerequisites

Before running BeachBot, ensure you have the following installed:

* **Python 3.7+:** You can download it from [python.org](https://www.python.org/downloads/).
* **pip:** Python package installer (usually included with Python installations).
* **Git:** For managing the repository and its submodule.

## Setup

1.  **Clone the repository with submodules:**
    When cloning the BeachBot repository, you need to initialize and update its submodules. Use the following command:
    ```bash
    git clone --recurse-submodules <repository_url>
    cd BeachBot
    ```
    *(Replace `<repository_url>` with the actual URL of your repository)*

    If you have already cloned the repository without the `--recurse-submodules` option, you can initialize and update the submodules using these commands:
    ```bash
    git submodule init
    git submodule update
    ```

2.  **Install dependencies:**
    Navigate to the root directory of the BeachBot project and install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
    *(Make sure you have a `requirements.txt` file listing all necessary Python packages, including `pathlib`, `python-dotenv`, and any libraries used by `SurfReportService`, `EmailSender`, and the submodule)*

## Environment Variables

BeachBot relies on environment variables for configuration. You need to create a `.env` file in the root directory of the project and populate it with the following information:

```dotenv
SCRAPPER_CONFIG=<path/to/your/scrapper_config.json>
TEST_URL=<URL_of_the_weather_data_source>
STATION_NUMBER=<identifier_for_the_weather_station>
SMTPSERVER=<your_smtp_server_address>
SMTPORT=<your_smtp_server_port>
SENDEREMAIL=<your_email_address_for_sending_reports>
RECEIVEREMAIL=<the_email_address_to_send_reports_to>
EMAILPASSWORD=<your_email_password>
OPEN_ROUTER_API_KEY=<your_OpenRouter_API_key>
BROWSER=chrome
HEADLESS=True
MODEL=openrouter/quasar-alpha


Explanation of the environment variables:

    SCRAPPER_CONFIG: The file path to your configuration file for the data scraping process. This file likely contains settings for how the bot should extract information from the weather data source.
    TEST_URL: The URL of the website or API endpoint from which the meteorological data is fetched.
    STATION_NUMBER: An identifier (e.g., a number or code) that specifies the particular weather station or data point you are interested in.
    SMTPSERVER: The address of your SMTP (Simple Mail Transfer Protocol) server. This is required if you intend to send the generated surf reports via email. Examples include smtp.gmail.com, smtp.office365.com, etc.
    SMTPORT: The port number used by your SMTP server. Common ports are 587 (for TLS/STARTTLS) or 465 (for SSL).
    SENDEREMAIL: The email address that the bot will use to send the surf reports.
    RECEIVEREMAIL: The email address(es) where the generated surf reports should be sent. You can use the same address as SENDEREMAIL if you want to receive them yourself.
    EMAILPASSWORD: The password for the SENDEREMAIL account. Be cautious about storing sensitive information like passwords directly in files.
    OPEN_ROUTER_API_KEY: Your API key for accessing the OpenRouter service. You can obtain an API key from the OpenRouter website.
    BROWSER: Specifies the browser to use for web scraping. Currently set to chrome. Ensure the corresponding browser is installed and ChromeDriver (if Chrome is used) is correctly set up.
    HEADLESS: Determines whether the browser should run in headless mode (without a visible GUI). Set to True to run in the background.
    MODEL: Specifies the OpenRouter model to use for language processing tasks. Currently set to openrouter/quasar-alpha.

## Running the Bot

To execute the BeachBot and generate a surf report, run the main script with the -m flag (otherwise you will have relative import error):

python -m sources.beachbot.main

## Debugging
this is the config for vs code:
        {
            "name": "Run BeachBot Module",
            "type": "debugpy",
            "request": "launch",
            "module": "sources.beachbot.main",
            "cwd": "${workspaceFolder}",
            "console": "integratedTerminal",
            "justMyCode": true,
            "envFile": "${workspaceFolder}/.env"
        }
