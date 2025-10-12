import requests
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import logging
from config import Config
import feedparser
import json
import hashlib
import os

class AlphaVantageNewsAPI:
    """Obtiene noticias y análisis de sentimiento usando Alpha Vantage API"""
    
    def __init__(self, api_key=None, cache_duration_minutes=15):
        self.api_key = api_key or Config.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.cache_duration = cache_duration_minutes * 60  # Convertir a segundos
        self.cache_dir = "cache"
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Asegura que el directorio de caché existe"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_key(self, params):
        """Genera una clave de caché basada en los parámetros"""
        # Crear una clave única basada en los parámetros
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key):
        """Obtiene la ruta del archivo de caché"""
        return os.path.join(self.cache_dir, f"alpha_vantage_{cache_key}.json")
    
    def _is_cache_valid(self, cache_file):
        """Verifica si el caché es válido"""
        if not os.path.exists(cache_file):
            return False
        
        file_age = time.time() - os.path.getmtime(cache_file)
        return file_age < self.cache_duration
    
    def _load_from_cache(self, cache_file):
        """Carga datos del caché"""
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.debug(f"Error cargando caché: {e}")
            return None
    
    def _save_to_cache(self, cache_file, data):
        """Guarda datos en el caché"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.debug(f"Error guardando caché: {e}")
    
    def fetch_financial_news(self, limit=10, tickers=None, topics=None, time_from=None, time_to=None, sort='LATEST'):
        """Obtiene noticias financieras con análisis de sentimiento de Alpha Vantage"""
        if not self.api_key:
            logging.warning("Alpha Vantage API key no configurada")
            return []
        
        params = {
            'function': 'NEWS_SENTIMENT',
            'apikey': self.api_key,
            'limit': min(limit, 1000),  # Alpha Vantage permite hasta 1000
            'sort': sort
        }
        
        # Agregar parámetros opcionales
        if tickers:
            if isinstance(tickers, list):
                tickers = ','.join(tickers)
            params['tickers'] = tickers
        
        if topics:
            if isinstance(topics, list):
                topics = ','.join(topics)
            params['topics'] = topics
        
        if time_from:
            params['time_from'] = time_from
        
        if time_to:
            params['time_to'] = time_to
        
        # Verificar caché primero
        cache_key = self._get_cache_key(params)
        cache_file = self._get_cache_file(cache_key)
        
        if self._is_cache_valid(cache_file):
            logging.info("Usando datos del caché para Alpha Vantage")
            cached_data = self._load_from_cache(cache_file)
            if cached_data:
                return self._process_articles_from_data(cached_data, limit)
        
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Verificar si hay error en la respuesta
            if 'Error Message' in data:
                logging.error(f"Alpha Vantage API Error: {data['Error Message']}")
                return []
            
            if 'Note' in data:
                note_msg = data['Note']
                logging.warning(f"Alpha Vantage API Note: {note_msg}")
                # Si es un rate limit, esperar un poco
                if 'API call frequency' in note_msg or 'rate limit' in note_msg.lower():
                    logging.info("Rate limit detectado, esperando 60 segundos...")
                    time.sleep(60)
                    return self.fetch_financial_news(limit, tickers, topics, time_from, time_to, sort)
                return []
            
            if 'Information' in data:
                info_msg = data['Information']
                logging.warning(f"Alpha Vantage API Information: {info_msg}")
                # Si es un rate limit, esperar un poco
                if 'API call frequency' in info_msg or 'rate limit' in info_msg.lower():
                    logging.info("Rate limit detectado, esperando 60 segundos...")
                    time.sleep(60)
                    return self.fetch_financial_news(limit, tickers, topics, time_from, time_to, sort)
                return []
            
            # Guardar en caché
            self._save_to_cache(cache_file, data)
            
            # Procesar los artículos
            return self._process_articles_from_data(data, limit)
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error de conexión con Alpha Vantage API: {e}")
            return []
        except Exception as e:
            logging.error(f"Error procesando respuesta de Alpha Vantage API: {e}")
            return []
    
    def _process_articles_from_data(self, data, limit):
        """Procesa los artículos desde los datos de la API"""
        articles = []
        feed_data = data.get('feed', [])
        
        for item in feed_data[:limit]:
            try:
                # Extraer información básica del artículo
                title = item.get('title', '')
                summary = item.get('summary', '')
                url = item.get('url', '')
                time_published = item.get('time_published', '')
                source = item.get('source', 'Alpha Vantage')
                
                # Extraer información de sentimiento
                overall_sentiment_score = item.get('overall_sentiment_score', 0)
                overall_sentiment_label = item.get('overall_sentiment_label', 'NEUTRAL')
                
                # Extraer información de tickers mencionados
                ticker_sentiment = item.get('ticker_sentiment', [])
                mentioned_tickers = []
                ticker_sentiments = {}
                
                for ticker_info in ticker_sentiment:
                    ticker = ticker_info.get('ticker', '')
                    if ticker:
                        mentioned_tickers.append(ticker)
                        ticker_sentiments[ticker] = {
                            'relevance_score': ticker_info.get('relevance_score', 0),
                            'ticker_sentiment_score': ticker_info.get('ticker_sentiment_score', 0),
                            'ticker_sentiment_label': ticker_info.get('ticker_sentiment_label', 'NEUTRAL')
                        }
                
                # Formatear fecha de publicación
                if time_published:
                    try:
                        # Alpha Vantage usa formato: 20231215T123000
                        if 'T' in time_published:
                            date_part, time_part = time_published.split('T')
                            year = date_part[:4]
                            month = date_part[4:6]
                            day = date_part[6:8]
                            hour = time_part[:2]
                            minute = time_part[2:4]
                            second = time_part[4:6]
                            published_at = f"{year}-{month}-{day}T{hour}:{minute}:{second}"
                        else:
                            published_at = datetime.now().isoformat()
                    except:
                        published_at = datetime.now().isoformat()
                else:
                    published_at = datetime.now().isoformat()
                
                # Crear descripción enriquecida con información de sentimiento
                sentiment_info = f"Sentimiento: {overall_sentiment_label} (Score: {overall_sentiment_score:.2f})"
                if mentioned_tickers:
                    sentiment_info += f" | Tickers: {', '.join(mentioned_tickers)}"
                
                enhanced_description = f"{summary}\n\n{sentiment_info}"
                
                articles.append({
                    'title': title,
                    'description': enhanced_description,
                    'content': summary,
                    'url': url,
                    'published_at': published_at,
                    'source': f'{source} (Alpha Vantage)',
                    'sentiment_score': overall_sentiment_score,
                    'sentiment_label': overall_sentiment_label,
                    'mentioned_tickers': mentioned_tickers,
                    'ticker_sentiments': ticker_sentiments
                })
                
            except Exception as item_error:
                logging.debug(f"Error procesando artículo de Alpha Vantage: {item_error}")
                continue
        
        logging.info(f"Obtenidos {len(articles)} artículos de Alpha Vantage")
        return articles
    
    def fetch_news_by_tickers(self, tickers, limit=10):
        """Obtiene noticias específicas para ciertos tickers"""
        if isinstance(tickers, str):
            tickers = [tickers]
        return self.fetch_financial_news(limit=limit, tickers=tickers)
    
    def fetch_news_by_topics(self, topics, limit=10):
        """Obtiene noticias por temas específicos"""
        if isinstance(topics, str):
            topics = [topics]
        return self.fetch_financial_news(limit=limit, topics=topics)
    
    def fetch_news_by_time_range(self, time_from, time_to=None, limit=10):
        """Obtiene noticias en un rango de tiempo específico"""
        return self.fetch_financial_news(limit=limit, time_from=time_from, time_to=time_to)

class NewsAPI:
    """Obtiene noticias usando NewsAPI (gratuito hasta 1000 requests/día)"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/everything"
    
    def fetch_financial_news(self, limit=10):
        """Obtiene noticias financieras de NewsAPI"""
        if not self.api_key:
            return []
        
        params = {
            'q': 'financial OR stock market OR economy OR trading',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': limit,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                if article.get('title') and article.get('description'):
                    articles.append({
                        'title': article['title'],
                        'description': article['description'],
                        'content': article.get('content', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('publishedAt'),
                        'source': 'NewsAPI'
                    })
            
            return articles
            
        except Exception as e:
            logging.error(f"Error fetching from NewsAPI: {e}")
            return []

class YahooFinanceNews:
    """Obtiene noticias de Yahoo Finance (gratuito)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://finance.yahoo.com/'
        }
        self.session.headers.update(self.headers)
    
    def fetch_financial_news(self, limit=10):
        """Obtiene noticias financieras de Yahoo Finance usando scraping como fallback"""
        articles = []
        
        # First try the yfinance library approach with better error handling
        try:
            tickers = ['^GSPC', '^DJI', '^IXIC', '^ORCL', '^TSLA', '^NVDA', '^MSFT', '^BTC', '^ETH', '^XRP', '^SOL' ]   # S&P 500, Dow Jones, NASDAQ, Russell 2000, Oracle, Tesla, Nvidia, Microsoft, Bitcoin, Ethereum,
            
            for ticker in tickers:
                try:
                    # Use a more robust approach with timeout
                    import yfinance as yf
                    stock = yf.Ticker(ticker)
                    
                    # Set a timeout for the request and handle potential JSON errors
                    try:
                        # Add a timeout and better error handling for yfinance requests
                        import socket
                        socket.setdefaulttimeout(10)
                        
                        # Try to get news with comprehensive error handling
                        try:
                            news = stock.news
                        except Exception as fetch_err:
                            logging.debug(f"Failed to fetch news for {ticker}: {fetch_err}")
                            continue
                            
                        # Check if news is valid and not empty
                        if not news:
                            logging.debug(f"No news data returned for {ticker}")
                            continue
                            
                        if not isinstance(news, list):
                            logging.debug(f"Invalid news data format for {ticker}: {type(news)}")
                            continue
                            
                        if len(news) == 0:
                            logging.debug(f"Empty news list returned for {ticker}")
                            continue
                            
                        # Process valid news items
                        for item in news[:max(1, limit//len(tickers))]:
                            try:
                                if not isinstance(item, dict):
                                    logging.debug(f"Skipping non-dict news item for {ticker}")
                                    continue
                                    
                                title = item.get('title', '')
                                if not title or not isinstance(title, str) or len(title.strip()) < 5:
                                    logging.debug(f"Skipping news item with invalid title for {ticker}")
                                    continue
                                    
                                # Extract other fields with validation
                                summary = item.get('summary', item.get('title', ''))
                                if not isinstance(summary, str):
                                    summary = str(summary) if summary else title
                                    
                                link = item.get('link', '')
                                if not isinstance(link, str):
                                    link = ''
                                    
                                # Handle publication time safely
                                pub_time = item.get('providerPublishTime')
                                if pub_time and isinstance(pub_time, (int, float)):
                                    try:
                                        published_at = datetime.fromtimestamp(pub_time).isoformat()
                                    except (ValueError, OSError):
                                        published_at = datetime.now().isoformat()
                                else:
                                    published_at = datetime.now().isoformat()
                                    
                                articles.append({
                                    'title': title.strip(),
                                    'description': summary[:200] + '...' if len(summary) > 200 else summary,
                                    'content': summary,
                                    'url': link,
                                    'published_at': published_at,
                                    'source': f'Yahoo Finance ({ticker})'
                                })
                                
                            except Exception as item_err:
                                logging.debug(f"Error processing news item for {ticker}: {item_err}")
                                continue
                                
                    except Exception as json_err:
                        # More specific error logging
                        error_msg = str(json_err)
                        if "Expecting value" in error_msg and "char 0" in error_msg:
                            logging.debug(f"Empty response or invalid JSON for {ticker} - this is normal when no news is available")
                        else:
                            logging.warning(f"Error processing news for {ticker}: {json_err}")
                        continue
                        
                except Exception as e:
                    logging.warning(f"Error fetching news for {ticker}: {e}")
                    continue
                    
            # If we got some articles from yfinance, return them
            if articles:
                return articles[:limit]
                
        except Exception as e:
            logging.warning(f"YFinance library failed: {e}")
        
        # Fallback: Try scraping Yahoo Finance directly
        try:
            return self._scrape_yahoo_finance_direct(limit)
        except Exception as e:
            logging.error(f"Yahoo Finance scraping fallback failed: {e}")
            return []
    
    def _scrape_yahoo_finance_direct(self, limit=10):
        """Fallback method to scrape Yahoo Finance directly"""
        try:
            url = "https://finance.yahoo.com/news/"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Look for news articles in Yahoo Finance structure
            news_items = soup.find_all(['h3', 'h2'], class_=lambda x: x and ('Mb(5px)' in str(x) or 'news' in str(x).lower()))
            
            if not news_items:
                # Try alternative selectors
                news_items = soup.find_all('a', href=lambda x: x and '/news/' in x)
            
            for item in news_items[:limit]:
                try:
                    if item.name == 'a':
                        title = item.get_text().strip()
                        link = item.get('href', '')
                    else:
                        link_elem = item.find('a')
                        if link_elem:
                            title = link_elem.get_text().strip()
                            link = link_elem.get('href', '')
                        else:
                            title = item.get_text().strip()
                            link = ''
                    
                    if link and not link.startswith('http'):
                        link = 'https://finance.yahoo.com' + link
                    
                    if title and len(title) > 10:
                        articles.append({
                            'title': title,
                            'description': title[:150] + '...',
                            'content': title,
                            'url': link,
                            'published_at': datetime.now().isoformat(),
                            'source': 'Yahoo Finance (Scraping)'
                        })
                        
                except Exception as item_error:
                    logging.debug(f"Error processing Yahoo Finance item: {item_error}")
                    continue
            
            return articles
            
        except Exception as e:
            logging.error(f"Error scraping Yahoo Finance directly: {e}")
            return []

class WebScraper:
    """Web scraper para fuentes de noticias financieras gratuitas"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Pragma': 'no-cache'
        }
        self.session.headers.update(self.headers)
    
    def scrape_marketwatch(self, limit=5):
        """Extrae noticias de MarketWatch con mejores selectores"""
        urls_to_try = [
            "https://www.marketwatch.com/latest-news",
            "https://www.marketwatch.com/newsviewer",
            "https://www.marketwatch.com/",
            "https://www.marketwatch.com/markets"
        ]
        
        successful_url = None
        response = None
        
        for url in urls_to_try:
            try:
                time.sleep(1)  # Small delay between requests
                response = self.session.get(url, timeout=20)
                if response.status_code == 200:
                    successful_url = url
                    break
                elif response.status_code == 401:
                    logging.warning(f"MarketWatch blocked access (401) for {url}")
                    continue
                else:
                    logging.debug(f"Status {response.status_code} for {url}")
                    continue
            except requests.exceptions.RequestException as e:
                logging.warning(f"Failed to access {url}: {e}")
                continue
        
        if not successful_url or not response:
            logging.error("All MarketWatch URLs failed")
            return []
        
        try:        
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Try multiple selectors for different MarketWatch layouts
            selectors_to_try = [
                {'tag': 'div', 'class_': ['article__content', 'story', 'element--article']},
                {'tag': 'article', 'class_': ['story', 'article']},
                {'tag': 'h3', 'class_': lambda x: x and 'headline' in str(x).lower()},
                {'tag': 'a', 'href': lambda x: x and '/story/' in x},
                {'tag': ['h2', 'h3', 'h4'], 'class_': None}
            ]
            
            news_items = []
            for selector in selectors_to_try:
                if selector.get('href'):
                    items = soup.find_all(selector['tag'], href=selector['href'])
                elif selector.get('class_'):
                    items = soup.find_all(selector['tag'], class_=selector['class_'])
                else:
                    items = soup.find_all(selector['tag'])
                
                if items:
                    news_items.extend(items)
                    break
            
            # If no items found with specific selectors, try general approach
            if not news_items:
                news_items = soup.find_all(['h2', 'h3', 'h4'])[:limit * 3]
            
            for item in news_items[:limit * 2]:
                try:
                    title = ''
                    link = ''
                    
                    # Extract title and link based on element type
                    if item.name in ['h2', 'h3', 'h4']:
                        title = item.get_text().strip()
                        link_elem = item.find('a') or item.find_parent('a')
                        link = link_elem.get('href', '') if link_elem else ''
                    elif item.name == 'a':
                        title = item.get_text().strip()
                        link = item.get('href', '')
                    else:
                        title_elem = item.find(['h3', 'h2', 'h4', 'a'])
                        if title_elem:
                            title = title_elem.get_text().strip()
                            if title_elem.name == 'a':
                                link = title_elem.get('href', '')
                            else:
                                link_elem = item.find('a')
                                link = link_elem.get('href', '') if link_elem else ''
                    
                    # Clean and validate title
                    if not title or len(title) < 15:
                        continue
                    
                    # Clean title from extra whitespace and newlines
                    title = ' '.join(title.split())
                    
                    # Fix relative links
                    if link and not link.startswith('http'):
                        if link.startswith('/'):
                            link = 'https://www.marketwatch.com' + link
                        else:
                            link = 'https://www.marketwatch.com/' + link
                    
                    # Look for description
                    desc_elem = item.find('p') or item.find_next('p')
                    if desc_elem:
                        description = desc_elem.get_text().strip()
                        description = ' '.join(description.split())  # Clean whitespace
                    else:
                        description = title[:120] + '...'
                    
                    # Filter for financial news
                    combined_text = title + " " + description
                    if self._is_financial_news(combined_text) and len(title) >= 15:
                        articles.append({
                            'title': title,
                            'description': description,
                            'content': description,
                            'url': link,
                            'published_at': datetime.now().isoformat(),
                            'source': 'MarketWatch'
                        })
                        
                    if len(articles) >= limit:
                        break
                        
                except Exception as item_error:
                    logging.debug(f"Error processing MarketWatch item: {item_error}")
                    continue
            
            if articles:
                logging.info(f"Successfully scraped {len(articles)} MarketWatch articles from {successful_url}")
            else:
                logging.debug(f"No suitable articles found on {successful_url}")
            
            return articles
            
        except Exception as e:
            logging.error(f"Error scraping MarketWatch: {e}")
            return []
    
    def scrape_investing_com(self, limit=5):
        """Extrae noticias de Investing.com con medidas anti-detección"""
        urls_to_try = [
            "https://www.investing.com/news/economy",
            "https://www.investing.com/news/stock-market-news",
            "https://www.investing.com/news/"
        ]
        
        for url_index, url in enumerate(urls_to_try):
            try:
                # Add random delay to avoid being detected as bot
                if url_index > 0:
                    time.sleep(2)
                
                # Update referer for each request
                headers = self.headers.copy()
                headers['Referer'] = 'https://www.investing.com/'
                
                response = self.session.get(url, headers=headers, timeout=20)
                
                # Handle different response codes
                if response.status_code == 403:
                    logging.warning(f"403 Forbidden for {url}, trying next URL")
                    continue
                elif response.status_code == 429:
                    logging.warning(f"Rate limited for {url}, waiting and trying next URL")
                    time.sleep(5)
                    continue
                elif response.status_code != 200:
                    logging.warning(f"Status {response.status_code} for {url}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = []
                
                # Try multiple selectors for different page layouts
                selectors_to_try = [
                    {'tag': 'article', 'class_': ['js-article-item', 'articleItem']},
                    {'tag': 'div', 'class_': ['largeTitle', 'title', 'articleItem']},
                    {'tag': 'a', 'href': lambda x: x and '/news/' in x},
                    {'tag': ['h2', 'h3'], 'class_': lambda x: x and 'title' in str(x).lower()}
                ]
                
                for selector in selectors_to_try:
                    if selector.get('href'):
                        news_items = soup.find_all(selector['tag'], href=selector['href'])
                    elif selector.get('class_'):
                        news_items = soup.find_all(selector['tag'], class_=selector['class_'])
                    else:
                        news_items = soup.find_all(selector['tag'])
                    
                    if news_items:
                        break
                
                # Process found news items
                for item in news_items[:limit * 2]:  # Get extra items to filter
                    try:
                        title = ''
                        link = ''
                        
                        # Extract title and link based on item structure
                        if item.name == 'a':
                            title = item.get_text().strip()
                            link = item.get('href', '')
                        else:
                            # Look for title in various elements
                            title_elem = item.find(['h3', 'h2', 'h4', 'a', 'span'])
                            if title_elem:
                                title = title_elem.get_text().strip()
                                # Try to find link
                                link_elem = item.find('a', href=True) or title_elem if title_elem.name == 'a' else None
                                link = link_elem.get('href', '') if link_elem else ''
                        
                        # Clean and validate
                        if not title or len(title) < 10:
                            continue
                            
                        if link and not link.startswith('http'):
                            link = 'https://www.investing.com' + link
                        
                        # Look for description
                        desc_elem = item.find('p') or item.find('span', class_=lambda x: x and 'summary' in str(x).lower())
                        description = desc_elem.get_text().strip() if desc_elem else title[:150] + '...'
                        
                        # Filter for financial news
                        if self._is_financial_news(title + " " + description):
                            articles.append({
                                'title': title,
                                'description': description,
                                'content': description,
                                'url': link,
                                'published_at': datetime.now().isoformat(),
                                'source': 'Investing.com'
                            })
                            
                        if len(articles) >= limit:
                            break
                            
                    except Exception as item_error:
                        logging.debug(f"Error processing Investing.com item: {item_error}")
                        continue
                
                # If we got articles, return them
                if articles:
                    logging.info(f"Successfully scraped {len(articles)} articles from {url}")
                    return articles
                else:
                    logging.debug(f"No articles found on {url}")
                    
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request error for {url}: {e}")
                continue
            except Exception as e:
                logging.warning(f"Error scraping {url}: {e}")
                continue
        
        logging.error("All Investing.com URLs failed")
        return []
    
    def _is_financial_news(self, text):
        """Determina si el texto es una noticia financiera"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in Config.FINANCIAL_KEYWORDS)

class RSSFeedNews:
    """Obtiene noticias de RSS feeds financieros gratuitos"""
    
    def __init__(self):
        # Updated with working RSS feeds (ordered by reliability)
        self.rss_feeds = [
            'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',  # WSJ Markets - most reliable
            'https://www.nasdaq.com/feed/rssoutbound?category=stocks',  # NASDAQ
            'https://finance.yahoo.com/news/rssindex',  # Yahoo Finance
            'https://feeds.reuters.com/reuters/businessNews',  # Reuters
            'https://www.ft.com/rss/feed/companies',  # Financial Times
            'https://feeds.bloomberg.com/markets/news.rss'  # Bloomberg (may be limited)
        ]
        
        # Set up session with proper headers for RSS feeds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml'
        })
    
    def fetch_financial_news(self, limit=10):
        """Obtiene noticias de RSS feeds financieros con mejor manejo de errores"""
        articles = []
        articles_per_feed = max(1, limit // len(self.rss_feeds))
        
        for feed_index, feed_url in enumerate(self.rss_feeds):
            try:
                # Add delay between feeds to avoid being rate limited
                if feed_index > 0:
                    time.sleep(1)
                
                logging.debug(f"Fetching RSS feed: {feed_url}")
                
                # Try to fetch with requests first (for better error handling)
                try:
                    response = self.session.get(feed_url, timeout=15)
                    if response.status_code == 200:
                        feed = feedparser.parse(response.content)
                    else:
                        logging.warning(f"RSS feed returned status {response.status_code}: {feed_url}")
                        # Fallback to feedparser's built-in fetching
                        feed = feedparser.parse(feed_url)
                except requests.exceptions.RequestException:
                    # Fallback to feedparser's built-in fetching
                    feed = feedparser.parse(feed_url)
                
                # Check if feed was parsed successfully
                if hasattr(feed, 'bozo') and feed.bozo:
                    logging.warning(f"RSS feed parsing issues for {feed_url}: {getattr(feed, 'bozo_exception', 'Unknown error')}")
                
                if not hasattr(feed, 'entries') or not feed.entries:
                    logging.warning(f"No entries found in RSS feed: {feed_url}")
                    continue
                
                feed_articles_count = 0
                for entry in feed.entries:
                    if feed_articles_count >= articles_per_feed:
                        break
                        
                    try:
                        # Extract title and description with better fallbacks
                        title = entry.get('title', '').strip()
                        description = (entry.get('summary', '') or 
                                     entry.get('description', '') or 
                                     entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '').strip()
                        
                        # Skip if no title
                        if not title or len(title) < 10:
                            continue
                        
                        # Clean HTML tags from description if present
                        if description:
                            from bs4 import BeautifulSoup
                            description = BeautifulSoup(description, 'html.parser').get_text().strip()
                            description = ' '.join(description.split())  # Clean whitespace
                        
                        # Use title as description fallback
                        if not description:
                            description = title[:150] + '...'
                        
                        # Extract URL
                        url = entry.get('link', '') or entry.get('guid', '')
                        
                        # Extract publication date
                        pub_date = entry.get('published', '') or entry.get('pubDate', '')
                        if not pub_date:
                            pub_date = datetime.now().isoformat()
                        
                        # Get source name
                        source_name = f'RSS-{feed_url.split("/")[2]}'
                        if 'reuters' in feed_url.lower():
                            source_name = 'Reuters RSS'
                        elif 'cnn' in feed_url.lower():
                            source_name = 'CNN Money RSS'
                        elif 'nasdaq' in feed_url.lower():
                            source_name = 'NASDAQ RSS'
                        elif 'yahoo' in feed_url.lower():
                            source_name = 'Yahoo Finance RSS'
                        elif 'wsj' in feed_url.lower() or 'dj.com' in feed_url.lower():
                            source_name = 'WSJ RSS'
                        
                        # Filter for financial news
                        combined_text = title + " " + description
                        if self._is_financial_news(combined_text):
                            articles.append({
                                'title': title,
                                'description': description[:300] + '...' if len(description) > 300 else description,
                                'content': description,
                                'url': url,
                                'published_at': pub_date,
                                'source': source_name
                            })
                            feed_articles_count += 1
                    
                    except Exception as entry_error:
                        logging.debug(f"Error processing RSS entry: {entry_error}")
                        continue
                
                if feed_articles_count > 0:
                    logging.debug(f"Got {feed_articles_count} articles from {feed_url}")
                else:
                    logging.debug(f"No suitable articles found in {feed_url}")
                        
            except Exception as e:
                logging.warning(f"Error fetching RSS feed {feed_url}: {e}")
                continue
        
        if articles:
            logging.info(f"Successfully fetched {len(articles)} articles from RSS feeds")
        else:
            logging.warning("No articles fetched from any RSS feeds")
            
        return articles[:limit]
    
    def _is_financial_news(self, text):
        """Determina si el texto es una noticia financiera"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in Config.FINANCIAL_KEYWORDS)

class NewsAggregator:
    """Agregador que combina múltiples fuentes de noticias"""
    
    def __init__(self, enable_scraping=False):
        self.news_api = NewsAPI()
        self.alpha_vantage_api = AlphaVantageNewsAPI()
        self.yahoo_news = YahooFinanceNews()
        self.rss_news = RSSFeedNews()
        self.logger = logging.getLogger(__name__)
        
        # Solo habilitar scraping si se especifica explícitamente
        self.enable_scraping = enable_scraping
        if self.enable_scraping:
            self.web_scraper = WebScraper()
        else:
            self.web_scraper = None
    
    def fetch_all_news(self, max_articles=None):
        """Obtiene noticias de todas las fuentes disponibles"""
        max_articles = max_articles or Config.MAX_NEWS_PER_ANALYSIS
        all_articles = []
        
        # Verificar si Alpha Vantage está disponible y configurado
        alpha_vantage_available = bool(Config.ALPHA_VANTAGE_API_KEY)
        
        if alpha_vantage_available:
            # Alpha Vantage como fuente principal pero sin dominar completamente
            try:
                alpha_vantage_articles = self.alpha_vantage_api.fetch_financial_news(max_articles // 3)
                all_articles.extend(alpha_vantage_articles)
                self.logger.info(f"Obtenidos {len(alpha_vantage_articles)} artículos de Alpha Vantage")
                
                # Mantener cuotas balanceadas para otras fuentes
                newsapi_quota = max_articles // 4
                yahoo_quota = max_articles // 4
                scraping_quota = max_articles // 6
                    
            except Exception as e:
                self.logger.warning(f"Alpha Vantage API no disponible: {e}")
                alpha_vantage_available = False
                # Usar cuotas normales si Alpha Vantage falla
                newsapi_quota = max_articles // 3
                yahoo_quota = max_articles // 3
                scraping_quota = max_articles // 4
        else:
            # Si Alpha Vantage no está disponible, usar cuotas normales
            newsapi_quota = max_articles // 3
            yahoo_quota = max_articles // 3
            scraping_quota = max_articles // 4
        
        # Intentar obtener de NewsAPI
        try:
            newsapi_articles = self.news_api.fetch_financial_news(newsapi_quota)
            all_articles.extend(newsapi_articles)
            self.logger.info(f"Obtenidos {len(newsapi_articles)} artículos de NewsAPI")
        except Exception as e:
            self.logger.warning(f"NewsAPI no disponible: {e}")
        
        # Yahoo Finance
        try:
            yahoo_articles = self.yahoo_news.fetch_financial_news(yahoo_quota)
            all_articles.extend(yahoo_articles)
            self.logger.info(f"Obtenidos {len(yahoo_articles)} artículos de Yahoo Finance")
        except Exception as e:
            self.logger.warning(f"Yahoo Finance no disponible: {e}")
        
        # Web scraping como fallback (solo si está habilitado)
        scraped_articles = []
        
        if self.enable_scraping and self.web_scraper:
            # Intentar MarketWatch
            try:
                mw_articles = self.web_scraper.scrape_marketwatch(scraping_quota // 2)
                scraped_articles.extend(mw_articles)
                self.logger.info(f"Obtenidos {len(mw_articles)} artículos de MarketWatch")
            except Exception as e:
                self.logger.warning(f"MarketWatch no disponible: {e}")
            
            # Intentar Investing.com
            try:
                inv_articles = self.web_scraper.scrape_investing_com(scraping_quota // 2)
                scraped_articles.extend(inv_articles)
                self.logger.info(f"Obtenidos {len(inv_articles)} artículos de Investing.com")
            except Exception as e:
                self.logger.warning(f"Investing.com no disponible: {e}")
            
            all_articles.extend(scraped_articles)
            self.logger.info(f"Obtenidos {len(scraped_articles)} artículos de web scraping total")
        else:
            self.logger.info("Web scraping deshabilitado para producción")
        
        # RSS feeds como fuente adicional
        try:
            # Asegurar que siempre intentemos obtener de RSS feeds
            rss_quota = max(2, max_articles // 8)  # Mínimo 2 artículos de RSS
            rss_articles = self.rss_news.fetch_financial_news(rss_quota)
            all_articles.extend(rss_articles)
            self.logger.info(f"Obtenidos {len(rss_articles)} artículos de RSS feeds")
        except Exception as e:
            self.logger.warning(f"RSS feeds no disponibles: {e}")
        
        # Si tenemos pocos artículos, intentar obtener más de las fuentes que funcionaron
        if len(all_articles) < max_articles // 2:
            self.logger.info("Pocos artículos obtenidos, intentando obtener más de fuentes disponibles...")
            
            # Intentar obtener más de Yahoo Finance si funcionó
            if len([a for a in all_articles if 'Yahoo' in a.get('source', '')]) > 0:
                try:
                    additional_yahoo = self.yahoo_news.fetch_financial_news(max_articles // 4)
                    all_articles.extend(additional_yahoo)
                    self.logger.info(f"Obtenidos {len(additional_yahoo)} artículos adicionales de Yahoo Finance")
                except Exception as e:
                    self.logger.debug(f"No se pudieron obtener artículos adicionales de Yahoo Finance: {e}")
            
            # Intentar obtener más de NewsAPI si funcionó
            if len([a for a in all_articles if 'NewsAPI' in a.get('source', '')]) > 0:
                try:
                    additional_newsapi = self.news_api.fetch_financial_news(max_articles // 4)
                    all_articles.extend(additional_newsapi)
                    self.logger.info(f"Obtenidos {len(additional_newsapi)} artículos adicionales de NewsAPI")
                except Exception as e:
                    self.logger.debug(f"No se pudieron obtener artículos adicionales de NewsAPI: {e}")
        
        # Eliminar duplicados por título
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            title_lower = article['title'].lower().strip()
            if title_lower not in seen_titles and len(title_lower) > 10:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        # Mostrar estadísticas de fuentes
        self._log_source_statistics(unique_articles)
        
        return unique_articles[:max_articles]
    
    def _log_source_statistics(self, articles):
        """Registra estadísticas de las fuentes utilizadas"""
        source_counts = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        self.logger.info("📊 Estadísticas de fuentes:")
        for source, count in source_counts.items():
            self.logger.info(f"   {source}: {count} artículos")
    
    def fetch_news_by_tickers(self, tickers, max_articles=None):
        """Obtiene noticias específicas para ciertos tickers usando Alpha Vantage"""
        max_articles = max_articles or Config.MAX_NEWS_PER_ANALYSIS
        try:
            articles = self.alpha_vantage_api.fetch_news_by_tickers(tickers, max_articles)
            self.logger.info(f"Obtenidos {len(articles)} artículos para tickers: {tickers}")
            return articles
        except Exception as e:
            self.logger.error(f"Error obteniendo noticias por tickers: {e}")
            return []
    
    def fetch_news_by_topics(self, topics, max_articles=None):
        """Obtiene noticias por temas específicos usando Alpha Vantage"""
        max_articles = max_articles or Config.MAX_NEWS_PER_ANALYSIS
        try:
            articles = self.alpha_vantage_api.fetch_news_by_topics(topics, max_articles)
            self.logger.info(f"Obtenidos {len(articles)} artículos para temas: {topics}")
            return articles
        except Exception as e:
            self.logger.error(f"Error obteniendo noticias por temas: {e}")
            return []
    
    def fetch_news_by_time_range(self, time_from, time_to=None, max_articles=None):
        """Obtiene noticias en un rango de tiempo específico usando Alpha Vantage"""
        max_articles = max_articles or Config.MAX_NEWS_PER_ANALYSIS
        try:
            articles = self.alpha_vantage_api.fetch_news_by_time_range(time_from, time_to, max_articles)
            self.logger.info(f"Obtenidos {len(articles)} artículos para rango de tiempo: {time_from} - {time_to}")
            return articles
        except Exception as e:
            self.logger.error(f"Error obteniendo noticias por rango de tiempo: {e}")
            return []

if __name__ == "__main__":
    # Test del agregador
    logging.basicConfig(level=logging.INFO)
    aggregator = NewsAggregator()
    news = aggregator.fetch_all_news(5)
    
    print(f"Obtenidas {len(news)} noticias:")
    for article in news:
        print(f"- {article['title']} ({article['source']})")