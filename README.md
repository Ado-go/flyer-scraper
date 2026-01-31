# Flyer Parser

A Python tool for scraping and parsing flyers from https://www.prospektmaschine.de.  
It uses Requests and BeautifulSoup for static HTML parsing and Selenium for handling dynamically loaded content.

The output is a structured JSON file containing information about all parsed flyers.

## Requirements

Install the required Python packages:

```bash
pip install requests beautifulsoup4 selenium
```

# Run the parser

```bash
python .\flyer_parser.py
```

## Features

The program:

- processes a selected flyer category,
- discovers all shops within that category,
- loads flyers for each shop using Selenium,
- extracts the following information:
  - flyer title,
  - thumbnail image URL,
  - shop name,
  - validity period (from – to),
  - timestamp of parsing,
- saves all collected data into a JSON file.
