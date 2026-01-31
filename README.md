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

### Command-line arguments

You can control the parser using the following optional arguments:

| Argument     | Description                  | Default              |
| ------------ | ---------------------------- | -------------------- |
| `--category` | Shop category to parse       | `/hypermarkte/`      |
| `--output`   | Name of the output JSON file | `parsed_flyers.json` |

Example:

```bash
python flyer_parser.py --category /elektronik/ --output elektronik_flyers.json
```

## Features

The program:

- processes a selected shop category,
- discovers all shops within that category,
- loads flyers for each shop using Selenium,
- extracts the following information:
  - flyer title,
  - thumbnail image URL,
  - shop name,
  - validity period (from – to),
  - timestamp of parsing,
- saves all collected data into a JSON file.
