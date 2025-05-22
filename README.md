# xAI Live Search API Interface

A Streamlit application that provides a user-friendly interface for testing the xAI Live Search API with fully configurable parameters.

[Official xAI Live Search API Documentation](https://docs.x.ai/docs/guides/live-search)

## Features

- Comprehensive interface for the xAI Live Search API
- Configurable search parameters including mode, date range, and maximum results
- Support for all data sources: Web, News, X (Twitter), and RSS feeds
- Country-specific search filtering
- Website exclusion capabilities
- Citation display and formatting
- Request payload preview
- Formatted response display

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
streamlit run app.py
```

## Usage

1. Enter your xAI API key in the sidebar
2. Compose your query in the Basic Query tab
3. Configure advanced search parameters in the Advanced Options tab (optional)
4. Click the "Send Request" button
5. View the API response in the API Response tab

## Search Parameters

### Basic Parameters
- **Search Mode**: Choose between "auto" (model decides), "on" (always search), or "off" (never search)
- **Date Range**: Restrict search results to a specific time period
- **Return Citations**: Include source citations in the response
- **Maximum Search Results**: Limit the number of data sources considered (1-50)

### Data Sources
- **Web Search**: Configure country code, safe search, and excluded websites
- **News Search**: Configure country code, safe search, and excluded websites
- **X (Twitter) Search**: Specify X handles to include
- **RSS Feed**: Provide an RSS feed URL

## Requirements

- Python 3.7+
- Streamlit
- Requests
- pytz
- python-dateutil
- xAI API key (available during beta until June 5, 2025)
