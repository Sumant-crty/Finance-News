import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from flask import Flask, send_from_directory
import os

class FinancialNewsAggregator:
    def __init__(self):
        """Initialize the financial news aggregator with multiple sources"""
        self.rss_sources = {
            # Major Financial News - RSS
            'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
            'Reuters Business': 'https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best',
            'Financial Times': 'https://www.ft.com/?format=rss',
            'Wall Street Journal': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
            'MarketWatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'CNBC': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'CNN Business': 'http://rss.cnn.com/rss/money_latest.rss',
            'Fox Business': 'https://moxie.foxbusiness.com/google-publisher/latest.xml',

            # Indian Financial News
            'Economic Times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
            'Economic Times Markets': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
            'Business Standard': 'https://www.business-standard.com/rss/home_page_top_stories.rss',
            'Business Standard Markets': 'https://www.business-standard.com/rss/markets-106.rss',
            'Mint': 'https://www.livemint.com/rss/news',
            'Mint Money': 'https://www.livemint.com/rss/money',
            'Moneycontrol': 'https://www.moneycontrol.com/rss/latestnews.xml',
            'Business Today': 'https://www.businesstoday.in/rss-feeds',
            'Financial Express': 'https://www.financialexpress.com/feed/',

            # International Markets
            'Yahoo Finance': 'https://finance.yahoo.com/news/rssindex',
            'Seeking Alpha': 'https://seekingalpha.com/feed.xml',
            'Investing.com': 'https://www.investing.com/rss/news.rss',
            'Forbes Money': 'https://www.forbes.com/money/feed/',
            'The Motley Fool': 'https://www.fool.com/feeds/index.aspx',

            # Crypto & Fintech
            'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'Cointelegraph': 'https://cointelegraph.com/rss',
            'TechCrunch Fintech': 'https://techcrunch.com/category/fintech/feed/',


            # Commodities & Trading
            'Kitco Gold News': 'https://www.kitco.com/rss/KitcoNews.xml',
            'Oil Price': 'https://oilprice.com/rss/main',

            # Analysis & Opinion
            'Barrons': 'https://www.barrons.com/feed',
            'Investor\'s Business Daily': 'https://www.investors.com/feed/',
        }

        self.scraping_sources = [
            {
                'name': 'Bloomberg Markets',
                'url': 'https://www.bloomberg.com/markets',
                'method': self.scrape_bloomberg
            },
            {
                'name': 'Reuters Markets',
                'url': 'https://www.reuters.com/markets/',
                'method': self.scrape_reuters
            },
            {
                'name': 'CNBC Markets',
                'url': 'https://www.cnbc.com/world-markets/',
                'method': self.scrape_cnbc
            },
            {
                'name': 'Financial Times Markets',
                'url': 'https://www.ft.com/markets',
                'method': self.scrape_ft
            },
            {
                'name': 'Moneycontrol News',
                'url': 'https://www.moneycontrol.com/news/business/markets/',
                'method': self.scrape_moneycontrol
            },
            {
                'name': 'NSE India News',
                'url': 'https://www.nseindia.com/market-data/live-market-indices',
                'method': self.scrape_nse
            },
            {
                'name': 'BSE India',
                'url': 'https://www.bseindia.com/',
                'method': self.scrape_bse
            },
            {
                'name': 'Zerodha Varsity',
                'url': 'https://zerodha.com/varsity/',
                'method': self.scrape_zerodha
            }
        ]

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def fetch_rss_feed(self, url, source_name):
        """Fetch financial news from RSS feed"""
        headlines = []
        try:
            print(f"Fetching from {source_name}...")
            feed = feedparser.parse(url)

            if feed.bozo:
                print(f"  Warning: Feed parsing issue for {source_name}")

            for entry in feed.entries[:20]:
                title = entry.get('title', 'No title')
                link = entry.get('link', '#')
                published = entry.get('published', entry.get('updated', 'Recent'))
                description = entry.get('summary', '')[:200]

                headlines.append({
                    'title': title,
                    'link': link,
                    'source': source_name,
                    'published': published,
                    'description': description
                })

            print(f"  ✓ Found {len(headlines)} headlines from {source_name}")

        except Exception as e:
            print(f"  ✗ Error fetching {source_name}: {str(e)}")

        return headlines

    def scrape_bloomberg(self, url):
        """Scrape Bloomberg"""
        headlines = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = soup.find_all('a', href=True)
            for article in articles:
                title = article.get_text(strip=True)
                link = article.get('href', '')

                if link and not link.startswith('http'):
                    link = 'https://www.bloomberg.com' + link

                if (
                    title and len(title) > 20 and
                    'bloomberg.com' in link and
                    '/news/' in link
                ):
                    headlines.append({
                        'title': title,
                        'link': link,
                        'source': 'Bloomberg Markets',
                        'published': 'Recent',
                        'description': ''
                    })

                if len(headlines) >= 15:
                    break

        except Exception as e:
            print(f"    Error: {str(e)}")

        return headlines

    def scrape_reuters(self, url):
        """Scrape Reuters"""
        headlines = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = soup.find_all(['h2', 'h3', 'h4'])
            for article in articles:
                link_tag = article.find('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')

                    if link and not link.startswith('http'):
                        link = 'https://www.reuters.com' + link

                    if title and len(title) > 20:
                        headlines.append({
                            'title': title,
                            'link': link,
                            'source': 'Reuters Markets',
                            'published': 'Recent',
                            'description': ''
                        })

                if len(headlines) >= 15:
                    break

        except Exception as e:
            print(f"    Error: {str(e)}")

        return headlines

    def scrape_cnbc(self, url):
        """Scrape CNBC"""
        headlines = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = soup.find_all('a', href=True)
            for article in articles:
                title = article.get_text(strip=True)
                link = article.get('href', '')

                if not link.startswith('http') and link.startswith('/'):
                    link = 'https://www.cnbc.com' + link

                if (
                    title and len(title) > 20 and
                    'cnbc.com' in link
                ):
                    headlines.append({
                        'title': title,
                        'link': link,
                        'source': 'CNBC Markets',
                        'published': 'Recent',
                        'description': ''
                    })

                if len(headlines) >= 15:
                    break

        except Exception as e:
            print(f"    Error: {str(e)}")

        return headlines

    def scrape_ft(self, url):
        """Scrape Financial Times"""
        headlines = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = soup.find_all(['h2', 'h3'])
            for article in articles:
                link_tag = article.find('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')

                    if link and not link.startswith('http'):
                        link = 'https://www.ft.com' + link

                    if title and len(title) > 20:
                        headlines.append({
                            'title': title,
                            'link': link,
                            'source': 'Financial Times Markets',
                            'published': 'Recent',
                            'description': ''
                        })

                if len(headlines) >= 15:
                    break

        except Exception as e:
            print(f"    Error: {str(e)}")

        return headlines

    def scrape_moneycontrol(self, url):
        """Scrape Moneycontrol"""
        headlines = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = soup.find_all('a', href=True)
            for article in articles:
                title = article.get_text(strip=True)
                link = article.get('href', '')

                if (
                    title and len(title) > 25 and
                    link.startswith('http') and
                    'moneycontrol.com' in link
                ):
                    headlines.append({
                        'title': title,
                        'link': link,
                        'source': 'Moneycontrol News',
                        'published': 'Recent',
                        'description': ''
                    })

                if len(headlines) >= 15:
                    break

        except Exception as e:
            print(f"    Error: {str(e)}")

        return headlines

    def scrape_nse(self, url):
        """Scrape NSE India"""
        headlines = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # NSE often requires specific handling
            articles = soup.find_all(['h2', 'h3', 'h4'])
            for article in articles:
                link_tag = article.find('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')

                    if link and not link.startswith('http'):
                        link = 'https://www.nseindia.com' + link

                    if title and len(title) > 15:
                        headlines.append({
                            'title': title,
                            'link': link,
                            'source': 'NSE India News',
                            'published': 'Recent',
                            'description': ''
                        })

                if len(headlines) >= 10:
                    break

        except Exception as e:
            print(f"    Error: {str(e)}")

        return headlines

    def scrape_bse(self, url):
        """Scrape BSE India"""
        headlines = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = soup.find_all('a', href=True)
            for article in articles:
                title = article.get_text(strip=True)
                link = article.get('href', '')

                if link and not link.startswith('http'):
                    link = 'https://www.bseindia.com' + link

                if (
                    title and len(title) > 20 and
                    'bseindia.com' in link
                ):
                    headlines.append({
                        'title': title,
                        'link': link,
                        'source': 'BSE India',
                        'published': 'Recent',
                        'description': ''
                    })

                if len(headlines) >= 10:
                    break

        except Exception as e:
            print(f"    Error: {str(e)}")

        return headlines

    def scrape_zerodha(self, url):
        """Scrape Zerodha Varsity"""
        headlines = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = soup.find_all(['h2', 'h3'])
            for article in articles:
                link_tag = article.find('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')

                    if link and not link.startswith('http'):
                        link = 'https://zerodha.com' + link

                    if title and len(title) > 15:
                        headlines.append({
                            'title': title,
                            'link': link,
                            'source': 'Zerodha Varsity',
                            'published': 'Recent',
                            'description': ''
                        })

                if len(headlines) >= 10:
                    break

        except Exception as e:
            print(f"    Error: {str(e)}")

        return headlines

    def fetch_all_news(self):
        """Fetch financial news from all available sources"""
        all_headlines = []

        print("=" * 70)
        print(" " * 15 + "FINANCIAL NEWS AGGREGATION")
        print("=" * 70)
        print()

        # Fetch from RSS feeds
        print("💰 Fetching from RSS Feeds...")
        print("-" * 70)
        for source_name, url in self.rss_sources.items():
            headlines = self.fetch_rss_feed(url, source_name)
            all_headlines.extend(headlines)
            time.sleep(0.5)

        print()
        print("🌐 Attempting to scrape additional sources...")
        print("-" * 70)

        # Try scraping sources
        for source in self.scraping_sources:
            try:
                print(f"Attempting to scrape {source['name']}...")
                scraped_headlines = source['method'](source['url'])
                if scraped_headlines:
                    all_headlines.extend(scraped_headlines)
                    print(f"  ✓ Found {len(scraped_headlines)} headlines from {source['name']}")
                else:
                    print(f"  ✗ No headlines found from {source['name']}")
            except Exception as e:
                print(f"  ✗ Could not scrape {source['name']}: {str(e)}")

            time.sleep(1)

        print()
        print("=" * 70)
        print(f"Total headlines collected: {len(all_headlines)}")
        print("=" * 70)

        # Remove duplicates
        seen_titles = set()
        unique_headlines = []
        for headline in all_headlines:
            title_lower = headline['title'].lower().strip()
            if title_lower not in seen_titles and len(title_lower) > 10:
                seen_titles.add(title_lower)
                unique_headlines.append(headline)

        print(f"Unique headlines after deduplication: {len(unique_headlines)}")
        print()

        return unique_headlines

def generate_html(headlines):
    """Generate beautiful HTML page with financial news"""

    # Group headlines by source
    grouped_headlines = {}
    for headline in headlines:
        source = headline['source']
        if source not in grouped_headlines:
            grouped_headlines[source] = []
        grouped_headlines[source].append(headline)

    # Categorize sources
    categories = {
        'International Markets': ['Bloomberg', 'Reuters', 'Financial Times', 'Wall Street Journal', 'MarketWatch', 'CNBC', 'CNN Business', 'Fox Business', 'Yahoo Finance', 'Seeking Alpha', 'Investing.com', 'Forbes Money', 'The Motley Fool', 'Barrons', "Investor's Business Daily"],
        'Indian Markets': ['Economic Times', 'Business Standard', 'Mint', 'Moneycontrol', 'Business Today', 'Financial Express', 'NSE India News', 'BSE India', 'Zerodha Varsity'],
        'Crypto & Fintech': ['CoinDesk', 'TechCrunch Fintech'],
        'Commodities': ['Kitco Gold News', 'Oil Price']
    }

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financial News - Showcased by Mr Bukkan</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                padding: 20px;
                padding-bottom: 40px;
            }}

            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
                margin-bottom: 20px;
            }}

            .header {{
                background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
                color: white;
                padding: 35px 30px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '💹';
                position: absolute;
                font-size: 200px;
                opacity: 0.1;
                right: -50px;
                top: -50px;
            }}

            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                position: relative;
                line-height: 1.3;
            }}

            .header p {{
                font-size: 1.3em;
                opacity: 0.95;
                position: relative;
            }}

            .market-ticker {{
                background: #000;
                color: #0f0;
                padding: 15px;
                font-family: 'Courier New', monospace;
                overflow: hidden;
                border-bottom: 2px solid #0f0;
            }}

            .ticker-content {{
                display: inline-block;
                white-space: nowrap;
                animation: scroll 30s linear infinite;
            }}

            @keyframes scroll {{
                0% {{ transform: translateX(100%); }}
                100% {{ transform: translateX(-100%); }}
            }}

            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                background: #f8f9fa;
                padding: 30px;
                border-bottom: 2px solid #e9ecef;
            }}

            .stat-item {{
                text-align: center;
                padding: 20px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}

            .stat-item:hover {{
                transform: translateY(-5px);
            }}

            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}

            .stat-label {{
                font-size: 0.95em;
                color: #666;
                margin-top: 8px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            .timestamp {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 15px;
                text-align: center;
                color: white;
                font-size: 1em;
                font-weight: 600;
                border-bottom: 2px solid #f5576c;
            }}

            .filters {{
                padding: 25px 30px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-bottom: 1px solid #dee2e6;
            }}

            .filter-search {{
                margin-bottom: 20px;
            }}

            .filter-search input {{
                width: 100%;
                padding: 15px 25px;
                border: 3px solid #2c5364;
                border-radius: 30px;
                font-size: 1.05em;
                outline: none;
                transition: all 0.3s ease;
                background: white;
            }}

            .filter-search input:focus {{
                box-shadow: 0 0 20px rgba(44, 83, 100, 0.4);
                border-color: #1e3c72;
            }}

            .category-filters {{
                margin-bottom: 15px;
            }}

            .category-btn {{
                padding: 10px 20px;
                margin: 5px;
                border: 2px solid #2c5364;
                background: white;
                color: #2c5364;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
                font-size: 0.9em;
            }}

            .category-btn:hover {{
                background: #2c5364;
                color: white;
                transform: scale(1.05);
            }}

            .category-btn.active {{
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                border-color: #1e3c72;
            }}

            .filter-buttons {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                max-height: 250px;
                overflow-y: auto;
                padding: 10px;
                background: white;
                border-radius: 10px;
            }}

            .filter-btn {{
                padding: 8px 18px;
                border: 2px solid #667eea;
                background: white;
                color: #667eea;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.85em;
                white-space: nowrap;
                font-weight: 500;
            }}

            .filter-btn:hover {{
                background: #667eea;
                color: white;
                transform: scale(1.05);
            }}

            .filter-btn.active {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-color: #667eea;
            }}

            .content {{
                padding: 30px;
                background: #f8f9fa;
                min-height: 400px;
                margin-bottom: 0;
            }}

            .category-section {{
                margin-bottom: 50px;
                page-break-inside: avoid;
            }}

            .category-header {{
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                padding: 20px 30px;
                border-radius: 10px;
                margin-bottom: 25px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}

            .category-title {{
                font-size: 1.8em;
                font-weight: bold;
                display: flex;
                align-items: center;
                gap: 15px;
            }}

            .source-section {{
                margin-bottom: 40px;
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                page-break-inside: avoid;
            }}

            .source-header {{
                display: flex;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 3px solid #2c5364;
            }}

            .source-icon {{
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                margin-right: 15px;
                font-size: 1.3em;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            }}

            .source-name {{
                font-size: 1.5em;
                font-weight: bold;
                color: #2c3e50;
            }}

            .source-count {{
                margin-left: auto;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 8px 20px;
                border-radius: 25px;
                font-size: 0.9em;
                font-weight: 600;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }}

            .headlines-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
            }}

            .headline-card {{
                background: white;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 25px;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}

            .headline-card::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                width: 5px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                transform: scaleY(0);
                transition: transform 0.3s ease;
            }}

            .headline-card:hover {{
                border-color: #667eea;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                transform: translateY(-5px);
            }}

            .headline-card:hover::before {{
                transform: scaleY(1);
            }}

            .headline-card a {{
                text-decoration: none;
                color: #2c3e50;
                display: block;
            }}

            .headline-title {{
                font-size: 1.15em;
                line-height: 1.6;
                margin-bottom: 12px;
                font-weight: 600;
                color: #1a1a1a;
            }}

            .headline-card:hover .headline-title {{
                color: #667eea;
            }}

            .headline-description {{
                font-size: 0.9em;
                color: #666;
                line-height: 1.5;
                margin-bottom: 12px;
            }}

            .headline-meta {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.85em;
                color: #6c757d;
                margin-top: 15px;
                padding-top: 12px;
                border-top: 1px solid #e9ecef;
            }}

            .published-date {{
                font-style: italic;
                display: flex;
                align-items: center;
                gap: 5px;
            }}

            .read-more {{
                color: #667eea;
                font-weight: 700;
                text-transform: uppercase;
                font-size: 0.8em;
                letter-spacing: 1px;
            }}

            .no-headlines {{
                text-align: center;
                padding: 80px 20px;
                color: #666;
            }}

            .no-headlines-icon {{
                font-size: 5em;
                margin-bottom: 20px;
            }}

            .footer {{
                background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
                position: relative;
                z-index: 1;
            }}

            .footer h3 {{
                font-size: 1.5em;
                margin-bottom: 20px;
            }}

            .source-list {{
                margin: 25px 0;
                font-size: 0.9em;
                opacity: 0.9;
                line-height: 2;
            }}

            .footer-links {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid rgba(255,255,255,0.2);
            }}

            .footer-link {{
                color: #667eea;
                text-decoration: none;
                margin: 0 15px;
                font-weight: 600;
            }}

            .footer-link:hover {{
                text-decoration: underline;
                color: #764ba2;
            }}

            @media (max-width: 768px) {{
                .headlines-grid {{
                    grid-template-columns: 1fr;
                }}

                .stats {{
                    grid-template-columns: 1fr;
                }}

                .header h1 {{
                    font-size: 1.5em;
                    line-height: 1.4;
                }}

                .header p {{
                    font-size: 1em;
                }}

                .filter-buttons {{
                    max-height: 150px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💹 Financial News - Showcased by Mr Bukkan</h1>
                <p>Real-Time Market Updates from 40+ Sources</p>
            </div>

            <div class="market-ticker">
                <div class="ticker-content">
                    📊 LIVE MARKET NEWS • Latest Updates from Bloomberg, Reuters, WSJ, ET, Moneycontrol & More •
                    Markets • Stocks • Crypto • Commodities • Banking • Fintech •
                    💰 Stay Informed with Real-Time Financial Intelligence •
                </div>
            </div>

            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">{len(headlines)}</div>
                    <div class="stat-label">Total Headlines</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(grouped_headlines)}</div>
                    <div class="stat-label">News Sources</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">4</div>
                    <div class="stat-label">Categories</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">🔴 LIVE</div>
                    <div class="stat-label">Status</div>
                </div>
            </div>

            <div class="timestamp">
                🕐 Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Market Hours: NYSE, NASDAQ, NSE, BSE
            </div>

            <div class="filters">
                <div class="filter-search">
                    <input type="text" id="searchBox" placeholder="🔍 Search financial news, stocks, companies..." onkeyup="searchHeadlines()">
                </div>

                <div class="category-filters">
                    <button class="category-btn active" onclick="filterCategory('all')">All Categories</button>
                    <button class="category-btn" onclick="filterCategory('International Markets')">🌍 International</button>
                    <button class="category-btn" onclick="filterCategory('Indian Markets')">🇮🇳 Indian Markets</button>
                    <button class="category-btn" onclick="filterCategory('Crypto & Fintech')">₿ Crypto & Fintech</button>
                    <button class="category-btn" onclick="filterCategory('Commodities')">📦 Commodities</button>
                </div>

                <div class="filter-buttons" id="sourceFilters">
                    <button class="filter-btn active" onclick="filterSource('all')">All Sources ({len(headlines)})</button>
    """

    for source in sorted(grouped_headlines.keys()):
        html_content += f"""
                    <button class="filter-btn" onclick="filterSource('{source}')">{source} ({len(grouped_headlines[source])})</button>
        """

    html_content += """
                </div>
            </div>

            <div class="content" id="newsContent">
    """

    if headlines:
        for category, sources_in_category in categories.items():
            category_headlines = {k: v for k, v in grouped_headlines.items() if any(s in k for s in sources_in_category)}

            if category_headlines:
                category_icons = {
                    'International Markets': '🌍',
                    'Indian Markets': '🇮🇳',
                    'Crypto & Fintech': '₿',
                    'Banking & Finance': '🏦',
                    'Commodities': '📦'
                }

                html_content += f"""
                <div class="category-section" data-category="{category}">
                    <div class="category-header">
                        <div class="category-title">
                            <span>{category_icons.get(category, '📊')}</span>
                            <span>{category}</span>
                        </div>
                    </div>
                """

                for source in sorted(category_headlines.keys()):
                    source_headlines = category_headlines[source]
                    html_content += f"""
                    <div class="source-section" data-source="{source}">
                        <div class="source-header">
                            <div class="source-icon">{source[0]}</div>
                            <div class="source-name">{source}</div>
                            <div class="source-count">{len(source_headlines)} articles</div>
                        </div>

                        <div class="headlines-grid">
                    """

                    for headline in source_headlines:
                        published = headline.get('published', 'Recent')
                        if len(published) > 50:
                            published = published[:50] + '...'

                        description = headline.get('description', '')
                        if description:
                            if len(description) > 150:
                                description = description[:150] + '...'
                            description_html = f'<div class="headline-description">{description}</div>'
                        else:
                            description_html = ''

                        html_content += f"""
                            <div class="headline-card">
                                <a href="{headline['link']}" target="_blank" rel="noopener noreferrer">
                                    <div class="headline-title">{headline['title']}</div>
                                    {description_html}
                                    <div class="headline-meta">
                                        <span class="published-date">🕒 {published}</span>
                                        <span class="read-more">Read More →</span>
                                    </div>
                                </a>
                            </div>
                        """

                    html_content += """
                        </div>
                    </div>
                    """

                html_content += """
                </div>
                """
    else:
        html_content += """
                <div class="no-headlines">
                    <div class="no-headlines-icon">📭</div>
                    <h2>No Financial News Available</h2>
                    <p>Please check your connection and try again.</p>
                </div>
        """

    html_content += """
            </div>

            <div class="footer">
                <h3>💹 Multi-Source Financial News - bukkan1309@gmail.com </h3>
                <p style="font-size: 1.1em; margin: 15px 0;">Your One-Stop Destination for Market Intelligence</p>

                <div class="source-list">
                    <strong>Trusted Sources:</strong><br>
                    Bloomberg • Reuters • Financial Times • Wall Street Journal • CNBC • MarketWatch •
                    Economic Times • Moneycontrol • Business Standard • Mint • Yahoo Finance •
                    CoinDesk • Cointelegraph • And 30+ More Premium Sources
                </div>

                <div class="footer-links">
                    <a href="#sumant chakravarty as Mr Bukkan" class="footer-link">About</a>
                    <a href="#" class="footer-link">Privacy Policy</a>
                    <a href="#" class="footer-link">Sources</a>
                    <a href="#" class="footer-link">API</a>
                    <a href="#" class="footer-link">Contact</a>
                </div>

                <p style="margin-top: 25px; font-size: 0.85em; opacity: 0.8;">
                    📰 All content belongs to respective publishers | Not financial advice |
                    For informational purposes only
                </p>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                    <p style="font-size: 0.9em; opacity: 0.7;">
                        © 2026 Mr Bukkan. All Rights Reserved.
                    </p>
                </div>
            </div>
        </div>

        <!-- Watermark -->
        <div style="position: fixed; bottom: 10px; left: 10px; background: rgba(0,0,0,0.7); color: rgba(255,255,255,0.6); padding: 8px 15px; border-radius: 5px; font-size: 0.75em; z-index: 9999; font-family: 'Courier New', monospace; pointer-events: none;">
            © 2026 Mr Bukkan
        </div>

        <script>
            let currentCategory = 'all';
            let currentSource = 'all';

            function filterCategory(category) {
                currentCategory = category;
                const sections = document.querySelectorAll('.category-section');
                const buttons = document.querySelectorAll('.category-btn');

                buttons.forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');

                // Clear search and source filter
                document.getElementById('searchBox').value = '';
                resetSourceFilters();

                if (category === 'all') {
                    sections.forEach(section => section.style.display = 'block');
                } else {
                    sections.forEach(section => {
                        if (section.dataset.category === category) {
                            section.style.display = 'block';
                        } else {
                            section.style.display = 'none';
                        }
                    });
                }
            }

            function filterSource(source) {
                currentSource = source;
                const sections = document.querySelectorAll('.source-section');
                const buttons = document.querySelectorAll('.filter-btn');

                buttons.forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');

                // Clear search
                document.getElementById('searchBox').value = '';

                if (source === 'all') {
                    sections.forEach(section => {
                        section.style.display = 'block';
                        const cards = section.querySelectorAll('.headline-card');
                        cards.forEach(card => card.style.display = 'block');
                    });
                } else {
                    sections.forEach(section => {
                        if (section.dataset.source === source) {
                            section.style.display = 'block';
                        } else {
                            section.style.display = 'none';
                        }
                    });
                }
            }

            function resetSourceFilters() {
                currentSource = 'all';
                const buttons = document.querySelectorAll('.filter-btn');
                buttons.forEach(btn => btn.classList.remove('active'));
                document.querySelector('.filter-btn').classList.add('active');
            }

            function searchHeadlines() {
                const searchTerm = document.getElementById('searchBox').value.toLowerCase();
                const sections = document.querySelectorAll('.source-section');
                const categoryButtons = document.querySelectorAll('.category-btn');
                const sourceButtons = document.querySelectorAll('.filter-btn');

                // Reset filters
                categoryButtons.forEach(btn => btn.classList.remove('active'));
                sourceButtons.forEach(btn => btn.classList.remove('active'));

                if (searchTerm === '') {
                    sections.forEach(section => {
                        section.style.display = 'block';
                        const cards = section.querySelectorAll('.headline-card');
                        cards.forEach(card => card.style.display = 'block');
                    });
                    document.querySelector('.category-btn').classList.add('active');
                    document.querySelector('.filter-btn').classList.add('active');
                    return;
                }

                sections.forEach(section => {
                    const cards = section.querySelectorAll('.headline-card');
                    let hasVisibleCard = false;

                    cards.forEach(card => {
                        const title = card.querySelector('.headline-title').textContent.toLowerCase();
                        const description = card.querySelector('.headline-description');
                        const descText = description ? description.textContent.toLowerCase() : '';

                        if (title.includes(searchTerm) || descText.includes(searchTerm)) {
                            card.style.display = 'block';
                            hasVisibleCard = true;
                        } else {
                            card.style.display = 'none';
                        }
                    });

                    section.style.display = hasVisibleCard ? 'block' : 'none';
                });
            }

            // Scroll to top button
            window.onscroll = function() {
                if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
                    if (!document.getElementById('scrollTopBtn')) {
                        const btn = document.createElement('button');
                        btn.id = 'scrollTopBtn';
                        btn.innerHTML = '↑';
                        btn.style.cssText = `
                            position: fixed;
                            bottom: 30px;
                            right: 30px;
                            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                            color: white;
                            border: none;
                            border-radius: 50%;
                            width: 55px;
                            height: 55px;
                            font-size: 26px;
                            cursor: pointer;
                            box-shadow: 0 5px 20px rgba(0,0,0,0.4);
                            z-index: 1000;
                            transition: all 0.3s ease;
                        `;
                        btn.onclick = function() {
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                        };
                        btn.onmouseover = function() {
                            this.style.transform = 'scale(1.15)';
                        };
                        btn.onmouseout = function() {
                            this.style.transform = 'scale(1)';
                        };
                        document.body.appendChild(btn);
                    }
                } else {
                    const btn = document.getElementById('scrollTopBtn');
                    if (btn) btn.remove();
                }
            };

            // Auto-refresh indicator (optional - uncomment if you want auto-refresh)
            /*
            setInterval(() => {
                const timestamp = document.querySelector('.timestamp');
                timestamp.style.animation = 'pulse 1s ease';
                setTimeout(() => {
                    timestamp.style.animation = '';
                }, 1000);
            }, 60000); // Pulse every minute
            */
        </script>
    </body>
    </html>
    """

    return html_content

def main():
    """Main function to run the financial news aggregator"""
    print("\n" + "="*70)
    print(" " * 12 + "FINANCIAL NEWS AGGREGATOR")
    print(" " * 15 + "40+ Premium Sources")
    print("="*70 + "\n")

    # Create aggregator instance
    aggregator = FinancialNewsAggregator()

    # Fetch all news
    headlines = aggregator.fetch_all_news()

from flask import Flask, send_from_directory
import os

financeNews = Flask(__name__)

def generate_html(headlines):
    # your existing HTML generation logic
    return "<html>...</html>"

@financeNews.route('/')
def index():
    headlines = get_headlines()   # however you collect them
    if headlines:
        html_content = generate_html(headlines)

        # Save to frontend/index.html
        output_dir = 'frontend'
        output_file_path = os.path.join(output_dir, 'index.html')
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Serve the file
        return send_from_directory(output_dir, 'index.html')
    else:
        return "<h2>No headlines were collected. Please check your internet connection.</h2>"

if __name__ == '__main__':
    financeNews.run(host='0.0.0.0', port=5000)
