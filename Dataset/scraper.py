import csv
import json
import argparse
import sys
import os
from datetime import datetime, timedelta
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

# function to parse command-line arguments
def parse_args():
    categories = ['business']

    countries = ['us']

    sources = ["cnbc", "reuters", "the-guardian-uk"]
    
    parser = argparse.ArgumentParser(description='Fetch and save news articles related to specific topics using NewsAPI')
    parser.add_argument('-k', '--key', required=True, help='API Key for NewsAPI')
    parser.add_argument('-u', '--country', choices=countries, help='Country code for zip (default: "us")')
    parser.add_argument('-c', '--category', choices=categories, help='Country code for zip (default: "us")')
    parser.add_argument('-s', '--source', choices=sources, help='Country code for zip (default: "us")')
    args = parser.parse_args()

    if args.source and (args.country or args.category):
        print('The --sources flag can\'t be used with the --category or --country flags.', file=sys.stderr)
        sys.exit(1)

    if (args.country and not args.category ) or (args.category and not args.country):
        print('--category and --country must both be used together.', file=sys.stderr)
        sys.exit(1) 

    return args
    args = parser.parse_args()
    return args

# function to save fetched articles to a CSV file
def save_articles_to_csv(articles, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Headlines', 'Time', 'Description'])
        for article in articles:
            writer.writerow([article['title'], article['publishedAt'], article['description']])

# fetch and save news articles
def main():
    args = parse_args()

    # Define the search queries for each source
    queries = {
        "cnbc": "S&P 500",
        "reuters": "business",
        "the-guardian-uk": "business"  # Assuming 'the-guardian-uk' for U.S. business news; adjust as needed
    }

    # Define your date range (Note: Historical access may be limited by the API tier)
    start_date = datetime(2017, 12, 31)
    end_date = datetime(2020, 7, 19)

    for source, query in queries.items():
        all_articles = []

        # Format dates for NewsAPI
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')

        # URL for the NewsAPI endpoint
        NEWS_API_URL = 'https://newsapi.org/v2/everything'
        params = {
            'apiKey': args.key,
            'q': query,  # Query related to S&P 500 for CNBC and business for Reuters and The Guardian
            'from': from_date,
            'to': to_date,
            'sources': source,
            'sortBy': 'publishedAt',  # Sort articles by publication date
            'pageSize': 100,  # Adjust pageSize as needed within API limits
        }

        # fetch articles from the NewsAPI
        try:
            response = urlopen(f'{NEWS_API_URL}?{urlencode(params)}')
            data = json.loads(response.read().decode('utf8'))
            articles = data.get('articles', [])
            all_articles.extend(articles)

            filename = f"{source}_news_headlines.csv"
            save_articles_to_csv(articles, filename)
            print(f"Saved articles to {filename}")

        except HTTPError as err:
            print(f"Failed to fetch articles for {source} with query '{query}': {err}", file=sys.stderr)
            continue

if __name__ == '__main__':
    main()
