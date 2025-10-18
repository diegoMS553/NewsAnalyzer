import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import logging
from datetime import datetime
from config import Config
import re
from collections import Counter

# Descargar recursos de NLTK la primera vez
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

class VaderAnalyzer:
    """Analizador de sentimientos usando VADER (optimizado para texto de redes sociales)"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze_sentiment(self, text):
        """Analiza el sentimiento del texto usando VADER"""
        if not text:
            return None
        
        scores = self.analyzer.polarity_scores(text)
        
        # VADER devuelve: neg, neu, pos, compound
        # compound es el score normalizado entre -1 y 1
        compound_score = scores['compound']
        
        if compound_score >= 0.05:
            sentiment = 'positive'
        elif compound_score <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'compound_score': compound_score,
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'analyzer': 'VADER'
        }

class TextBlobAnalyzer:
    """Analizador de sentimientos usando TextBlob"""
    
    def analyze_sentiment(self, text):
        """Analiza el sentimiento del texto usando TextBlob"""
        if not text:
            return None
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'analyzer': 'TextBlob'
            }
        except Exception as e:
            logging.error(f"Error en TextBlob analysis: {e}")
            return None

class MarketSummaryAnalyzer:
    """Analizador de resumen de mercado usando Perplexity AI"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_market_summary(self):
        """Obtiene un resumen del mercado usando Perplexity AI"""
        try:
            from news_fetcher import PerplexityAPI
            from config import Config

            if not Config.PERPLEXITY_API_KEY:
                return None

            perplexity = PerplexityAPI()

            # Prompt específico para resumen de mercado
            messages = [{
                "role": "system",
                "content": "Eres un experto analista financiero. Proporciona un resumen conciso del estado actual del mercado financiero global. Evalúa si el día está siendo POSITIVO, NEGATIVO o NEUTRAL basado en indicadores clave como índices bursátiles, commodities, criptomonedas y eventos económicos. Incluye menciones específicas a índices principales (S&P 500, Dow Jones, NASDAQ, Bitcoin, etc.) y eventos importantes del día."
            }, {
                "role": "user",
                "content": "Proporciona un resumen del mercado financiero actual en español. Indica claramente si el sentimiento general del día es POSITIVO, NEGATIVO o NEUTRAL. Incluye datos específicos de índices principales y eventos económicos relevantes. Formato: 'SENTIMIENTO: [POSITIVO/NEGATIVO/NEUTRAL]\nRESUMEN: [texto del resumen]'"
            }]

            payload = {
                "model": "sonar",
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.3,
                "stream": False,
                "return_images": False,
                "return_related_questions": False,
                "search_recency_filter": "day"
            }

            import requests
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                json=payload,
                headers={
                    'Authorization': f'Bearer {Config.PERPLEXITY_API_KEY}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=15
            )

            response.raise_for_status()
            data = response.json()

            if 'choices' in data and data['choices']:
                content = data['choices'][0]['message']['content']

                # Parsear el contenido estructurado
                sentiment = 'neutral'
                summary = content.strip()

                # Buscar indicador de sentimiento
                if 'POSITIVO' in content.upper():
                    sentiment = 'positive'
                elif 'NEGATIVO' in content.upper():
                    sentiment = 'negative'
                elif 'NEUTRAL' in content.upper():
                    sentiment = 'neutral'

                return {
                    'sentiment': sentiment,
                    'summary': summary,
                    'raw_content': content,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de mercado: {e}")
            return None


class FinancialSentimentAnalyzer:
    """Analizador especializado en sentimientos financieros"""

    def __init__(self):
        self.vader = VaderAnalyzer()
        self.textblob = TextBlobAnalyzer()
        self.market_summary = MarketSummaryAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        # Palabras clave financieras con connotación positiva/negativa (expandidas)
        self.positive_financial_words = {
            # Crecimiento y ganancias
            'growth', 'profit', 'gain', 'rise', 'surge', 'bull', 'bullish', 'rally',
            'upward', 'increase', 'strong', 'boom', 'recovery', 'optimistic', 'positive',
            'beat expectations', 'outperform', 'milestone', 'record high', 'breakthrough',
            'earnings beat', 'revenue growth', 'profit margin', 'market cap', 'dividend',
            'buy rating', 'upgrade', 'momentum', 'breakout', 'support', 'resistance',
            'golden cross', 'bull market', 'rebound', 'bounce', 'climb', 'soar',
            'skyrocket', 'explode', 'surpass', 'exceed', 'top', 'lead', 'dominate',
            'outpace', 'accelerate', 'expand', 'thrive', 'prosper', 'flourish',

            # Indicadores positivos
            'green', 'up', 'high', 'peak', 'summit', 'zenith', 'pinnacle', 'apex',
            'culmination', 'climax', 'acme', 'meridian', 'noon', 'heyday', 'prime',
            'flush', 'bloom', 'blossom', 'flower', 'efflorescence', 'florescence',

            # Acciones positivas
            'buy', 'long', 'hold', 'accumulate', 'add', 'invest', 'purchase', 'acquire',
            'obtain', 'procure', 'secure', 'gain', 'win', 'achieve', 'attain', 'reach',

            # Noticias positivas
            'good news', 'great news', 'excellent', 'outstanding', 'superb', 'magnificent',
            'splendid', 'wonderful', 'marvelous', 'fantastic', 'tremendous', 'amazing',
            'incredible', 'unbelievable', 'extraordinary', 'phenomenal', 'exceptional'
        }

        self.negative_financial_words = {
            # Pérdidas y declives
            'loss', 'decline', 'fall', 'drop', 'crash', 'bear', 'bearish', 'recession',
            'downward', 'decrease', 'weak', 'collapse', 'crisis', 'pessimistic', 'negative',
            'miss expectations', 'underperform', 'concern', 'risk', 'uncertainty', 'volatile',
            'losses', 'declines', 'falls', 'drops', 'crashes', 'bears', 'recessions',
            'downwards', 'decreases', 'weaks', 'collapses', 'crises', 'pessimistics', 'negatives',
            'misses expectations', 'underperforms', 'concerns', 'risks', 'uncertainties', 'volatiles',

            # Indicadores negativos
            'red', 'down', 'low', 'bottom', 'nadir', 'trough', 'depth', 'abyss',
            'chasm', 'gulf', 'pit', 'void', 'emptiness', 'vacuum', 'nothingness',

            # Acciones negativas
            'sell', 'short', 'dump', 'liquidate', 'unload', 'dispose', 'shed', 'cut',
            'reduce', 'slash', 'trim', 'curtail', 'diminish', 'lessen', 'lower',

            # Noticias negativas
            'bad news', 'terrible news', 'awful', 'horrible', 'dreadful', 'atrocious',
            'abysmal', 'appalling', 'deplorable', 'lamentable', 'miserable', 'pathetic',
            'shocking', 'horrific', 'disastrous', 'catastrophic', 'devastating', 'ruinous',

            # Problemas financieros
            'debt', 'default', 'bankruptcy', 'insolvency', 'liquidation', 'foreclosure',
            'delinquency', 'arrears', 'overdue', 'unpaid', 'outstanding', 'liability',
            'obligation', 'burden', 'encumbrance', 'onus', 'weight', 'load', 'pressure',

            # Riesgos y preocupaciones
            'warning', 'alert', 'caution', 'danger', 'hazard', 'peril', 'threat', 'menace',
            'intimidation', 'bullying', 'harassment', 'oppression', 'suppression', 'repression',
            'tyranny', 'despotism', 'autocracy', 'dictatorship', 'totalitarianism', 'authoritarianism',

            # Eventos negativos
            'scandal', 'controversy', 'investigation', 'probe', 'inquiry', 'examination',
            'scrutiny', 'review', 'audit', 'inspection', 'assessment', 'evaluation',
            'appraisal', 'judgment', 'verdict', 'decision', 'ruling', 'sentence',

            # Mercado bajista
            'bear market', 'correction', 'pullback', 'retreat', 'reversal', 'turnaround',
            'u-turn', 'about-face', 'volte-face', 'flip-flop', 'change', 'shift', 'switch',
            'transition', 'transformation', 'metamorphosis', 'conversion', 'alteration',

            # Indicadores técnicos negativos
            'death cross', 'oversold', 'breakdown', 'breakout failure', 'false breakout',
            'head and shoulders', 'double top', 'triple top', 'descending triangle',
            'falling wedge', 'bear flag', 'bear pennant', 'descending channel'
        }

        # Palabras clave específicas de mercado cripto
        self.crypto_positive_words = {
            'moon', 'mooning', 'pump', 'pumping', 'lambo', 'diamond hands', 'hodl',
            'to the moon', 'rocket', 'gem', 'undervalued', 'buy the dip', 'dip buying',
            'accumulation', 'whale', 'whales buying', 'institutional money', 'adoption',
            'mainstream', 'mass adoption', 'partnership', 'integration', 'listing',
            'burn', 'burning', 'staking', 'yield farming', 'defi', 'nft', 'web3'
        }

        self.crypto_negative_words = {
            'dump', 'dumping', 'paper hands', 'panic sell', 'panic selling', 'sell off',
            'rug pull', 'rug', 'scam', 'exit scam', 'honeypot', 'rekt', 'liquidated',
            'margin call', 'forced liquidation', 'bear trap', 'whale dump', 'whales dumping',
            'fud', 'fear', 'uncertainty', 'doubt', 'manipulation', 'wash trading',
            'fake volume', 'delisting', 'banned', 'prohibited', 'illegal', 'unlawful'
        }
    
    def analyze_article(self, article):
        """Analiza el sentimiento de un artículo completo"""
        # Combinar título y descripción para análisis más completo
        full_text = f"{article.get('title', '')} {article.get('description', '')}"
        
        # Si el artículo ya tiene datos de sentimiento de Alpha Vantage, usarlos
        alpha_vantage_sentiment = None
        if 'sentiment_score' in article and 'sentiment_label' in article:
            alpha_vantage_sentiment = self._process_alpha_vantage_sentiment(article)
        
        # Análisis con ambos métodos
        vader_result = self.vader.analyze_sentiment(full_text)
        textblob_result = self.textblob.analyze_sentiment(full_text)
        
        # Análisis específico financiero
        financial_bias = self._analyze_financial_keywords(full_text)
        
        # Combinar resultados para obtener análisis final (incluyendo Alpha Vantage si está disponible)
        final_sentiment = self._combine_analyses(vader_result, textblob_result, financial_bias, alpha_vantage_sentiment)
        
        result = {
            'article': article,
            'sentiment_analysis': {
                'vader': vader_result,
                'textblob': textblob_result,
                'financial_bias': financial_bias,
                'final_sentiment': final_sentiment,
                'confidence': self._calculate_confidence(vader_result, textblob_result, financial_bias, alpha_vantage_sentiment),
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
        # Agregar datos de Alpha Vantage si están disponibles
        if alpha_vantage_sentiment:
            result['sentiment_analysis']['alpha_vantage'] = alpha_vantage_sentiment
            result['mentioned_tickers'] = article.get('mentioned_tickers', [])
            result['ticker_sentiments'] = article.get('ticker_sentiments', {})
        
        return result
    
    def _process_alpha_vantage_sentiment(self, article):
        """Procesa los datos de sentimiento de Alpha Vantage"""
        sentiment_score = article.get('sentiment_score', 0)
        sentiment_label = article.get('sentiment_label', 'NEUTRAL')
        
        # Mapear etiquetas de Alpha Vantage a nuestro formato
        label_mapping = {
            'Very-Bullish': 'very_positive',
            'Bullish': 'positive', 
            'Somewhat-Bullish': 'somewhat_positive',
            'Neutral': 'neutral',
            'Somewhat-Bearish': 'somewhat_negative',
            'Bearish': 'negative',
            'Very-Bearish': 'very_negative'
        }
        
        mapped_sentiment = label_mapping.get(sentiment_label, 'neutral')
        
        return {
            'sentiment': mapped_sentiment,
            'score': sentiment_score,
            'label': sentiment_label,
            'analyzer': 'Alpha Vantage',
            'confidence': min(abs(sentiment_score) * 2, 1.0)  # Convertir score a confianza
        }
    
    def _analyze_financial_keywords(self, text):
        """Analiza palabras clave específicas del ámbito financiero con análisis mejorado"""
        text_lower = text.lower()

        # Análisis de palabras financieras tradicionales
        positive_count = sum(1 for word in self.positive_financial_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_financial_words if word in text_lower)

        # Análisis de palabras cripto
        crypto_positive_count = sum(1 for word in self.crypto_positive_words if word in text_lower)
        crypto_negative_count = sum(1 for word in self.crypto_negative_words if word in text_lower)

        # Análisis de intensidad basado en contexto
        intensity_multiplier = self._calculate_intensity_multiplier(text)

        # Aplicar multiplicadores de intensidad
        positive_count = int(positive_count * intensity_multiplier)
        negative_count = int(negative_count * intensity_multiplier)
        crypto_positive_count = int(crypto_positive_count * intensity_multiplier)
        crypto_negative_count = int(crypto_negative_count * intensity_multiplier)

        # Peso mayor para palabras cripto (más volátiles)
        total_positive = positive_count + (crypto_positive_count * 1.5)
        total_negative = negative_count + (crypto_negative_count * 1.5)

        total_words = total_positive + total_negative

        if total_words == 0:
            return {
                'sentiment': 'neutral',
                'score': 0,
                'positive_keywords': 0,
                'negative_keywords': 0,
                'crypto_positive': 0,
                'crypto_negative': 0,
                'intensity_multiplier': intensity_multiplier
            }

        # Calcular score con pesos diferenciados
        financial_weight = 0.7
        crypto_weight = 0.3

        financial_score = (positive_count - negative_count) / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0
        crypto_score = (crypto_positive_count - crypto_negative_count) / (crypto_positive_count + crypto_negative_count) if (crypto_positive_count + crypto_negative_count) > 0 else 0

        combined_score = (financial_score * financial_weight) + (crypto_score * crypto_weight)

        # Determinar sentimiento basado en score combinado
        if combined_score > 0.15:
            sentiment = 'positive'
        elif combined_score < -0.15:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        return {
            'sentiment': sentiment,
            'score': combined_score,
            'positive_keywords': positive_count,
            'negative_keywords': negative_count,
            'crypto_positive': crypto_positive_count,
            'crypto_negative': crypto_negative_count,
            'intensity_multiplier': intensity_multiplier,
            'financial_score': financial_score,
            'crypto_score': crypto_score
        }

    def _calculate_intensity_multiplier(self, text):
        """Calcula un multiplicador basado en la intensidad del lenguaje"""
        text_lower = text.lower()

        # Palabras de intensidad alta
        high_intensity_words = {
            'extremely', 'incredibly', 'amazingly', 'unbelievably', 'massively', 'hugely',
            'enormously', 'tremendously', 'immensely', 'vastly', 'highly', 'severely',
            'critically', 'urgently', 'desperately', 'catastrophically', 'devastatingly'
        }

        # Palabras de intensidad media
        medium_intensity_words = {
            'very', 'quite', 'rather', 'pretty', 'fairly', 'somewhat', 'moderately',
            'reasonably', 'relatively', 'comparatively', 'significantly', 'considerably'
        }

        high_count = sum(1 for word in high_intensity_words if word in text_lower)
        medium_count = sum(1 for word in medium_intensity_words if word in text_lower)

        # Calcular multiplicador base
        base_multiplier = 1.0 + (high_count * 0.5) + (medium_count * 0.25)

        # Bonus por signos de exclamación (indican emoción fuerte)
        exclamation_count = text.count('!')
        base_multiplier += exclamation_count * 0.2

        # Bonus por palabras en mayúsculas (indican énfasis)
        uppercase_words = len(re.findall(r'\b[A-Z]{3,}\b', text))
        base_multiplier += (uppercase_words * 0.1)

        return min(base_multiplier, 3.0)  # Cap at 3.0
    
    def _combine_analyses(self, vader_result, textblob_result, financial_bias, alpha_vantage_result=None):
        """Combina los diferentes análisis para obtener un resultado final"""
        sentiments = []
        scores = []
        weights = []
        
        # Recopilar sentimientos con pesos
        if vader_result:
            sentiments.append(vader_result['sentiment'])
            scores.append(vader_result['compound_score'])
            weights.append(1.0)
        
        if textblob_result:
            sentiments.append(textblob_result['sentiment'])
            scores.append(textblob_result['polarity'])
            weights.append(1.0)
        
        if financial_bias:
            sentiments.append(financial_bias['sentiment'])
            scores.append(financial_bias['score'])
            weights.append(1.2)  # Peso ligeramente mayor para análisis financiero
        
        # Alpha Vantage tiene peso mayor por ser especializado en finanzas
        if alpha_vantage_result:
            sentiments.append(alpha_vantage_result['sentiment'])
            scores.append(alpha_vantage_result['score'])
            weights.append(2.0)  # Peso significativamente mayor para Alpha Vantage
        
        # Determinar sentimiento ponderado
        positive_weight = 0
        negative_weight = 0
        neutral_weight = 0
        
        for i, sentiment in enumerate(sentiments):
            weight = weights[i]
            if sentiment in ['positive', 'somewhat_positive', 'very_positive']:
                positive_weight += weight
            elif sentiment in ['negative', 'somewhat_negative', 'very_negative']:
                negative_weight += weight
            else:
                neutral_weight += weight
        
        # Determinar sentimiento final
        if positive_weight > negative_weight and positive_weight > neutral_weight:
            final_sentiment = 'positive'
        elif negative_weight > positive_weight and negative_weight > neutral_weight:
            final_sentiment = 'negative'
        else:
            final_sentiment = 'neutral'
        
        # Calcular score promedio
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Contar sentimientos individuales
        sentiment_counts = {
            'positive': sum(1 for s in sentiments if s in ['positive', 'somewhat_positive', 'very_positive']),
            'negative': sum(1 for s in sentiments if s in ['negative', 'somewhat_negative', 'very_negative']),
            'neutral': sum(1 for s in sentiments if s == 'neutral')
        }
        
        return {
            'sentiment': final_sentiment,
            'average_score': avg_score,
            'sentiment_distribution': sentiment_counts
        }
    
    def _calculate_confidence(self, vader_result, textblob_result, financial_bias, alpha_vantage_result=None):
        """Calcula la confianza del análisis basado en la concordancia entre métodos"""
        sentiments = []
        
        if vader_result:
            sentiments.append(vader_result['sentiment'])
        if textblob_result:
            sentiments.append(textblob_result['sentiment'])
        if financial_bias:
            sentiments.append(financial_bias['sentiment'])
        if alpha_vantage_result:
            sentiments.append(alpha_vantage_result['sentiment'])
        
        if not sentiments:
            return 0.0
        
        # Confianza basada en consenso, con bonus si Alpha Vantage está presente
        most_common_sentiment = max(set(sentiments), key=sentiments.count)
        agreement_count = sentiments.count(most_common_sentiment)
        
        confidence = agreement_count / len(sentiments)
        
        # Bonus de confianza si Alpha Vantage está presente y coincide
        if alpha_vantage_result and alpha_vantage_result['sentiment'] == most_common_sentiment:
            confidence += 0.2  # Bonus del 20%
        
        return min(confidence, 1.0)  # Cap at 100%
    
    def analyze_multiple_articles(self, articles, include_market_summary=True):
        """Analiza múltiples artículos y proporciona un resumen general con resumen de mercado"""
        if not articles:
            return {'error': 'No articles to analyze'}

        analyzed_articles = []
        sentiment_summary = {'positive': 0, 'negative': 0, 'neutral': 0}

        # Análisis detallado por fuente
        source_sentiments = {}
        ticker_impact = {}

        for article in articles:
            try:
                analysis = self.analyze_article(article)
                analyzed_articles.append(analysis)

                final_sentiment = analysis['sentiment_analysis']['final_sentiment']['sentiment']
                sentiment_summary[final_sentiment] += 1

                # Análisis por fuente
                source = article.get('source', 'Unknown')
                if source not in source_sentiments:
                    source_sentiments[source] = {'positive': 0, 'negative': 0, 'neutral': 0}
                source_sentiments[source][final_sentiment] += 1

                # Análisis de impacto por ticker
                if 'mentioned_tickers' in analysis:
                    for ticker in analysis['mentioned_tickers']:
                        if ticker not in ticker_impact:
                            ticker_impact[ticker] = {'positive': 0, 'negative': 0, 'neutral': 0}
                        ticker_impact[ticker][final_sentiment] += 1

            except Exception as e:
                self.logger.error(f"Error analyzing article: {e}")
                continue

        # Calcular tendencia general
        total_articles = len(analyzed_articles)
        if total_articles == 0:
            overall_sentiment = 'neutral'
        else:
            max_sentiment = max(sentiment_summary.items(), key=lambda x: x[1])
            overall_sentiment = max_sentiment[0]

        # Obtener resumen de mercado si está habilitado
        market_summary = None
        if include_market_summary:
            market_summary = self.market_summary.get_market_summary()

        # Calcular métricas avanzadas
        sentiment_volatility = self._calculate_sentiment_volatility(analyzed_articles)
        confidence_distribution = self._calculate_confidence_distribution(analyzed_articles)

        return {
            'analyzed_articles': analyzed_articles,
            'summary': {
                'total_articles': total_articles,
                'sentiment_breakdown': sentiment_summary,
                'overall_sentiment': overall_sentiment,
                'positive_percentage': (sentiment_summary['positive'] / total_articles * 100) if total_articles > 0 else 0,
                'negative_percentage': (sentiment_summary['negative'] / total_articles * 100) if total_articles > 0 else 0,
                'neutral_percentage': (sentiment_summary['neutral'] / total_articles * 100) if total_articles > 0 else 0,
                'source_sentiments': source_sentiments,
                'ticker_impact': ticker_impact,
                'sentiment_volatility': sentiment_volatility,
                'confidence_distribution': confidence_distribution
            },
            'market_summary': market_summary,
            'timestamp': datetime.now().isoformat()
        }

    def _calculate_sentiment_volatility(self, analyzed_articles):
        """Calcula la volatilidad del sentimiento (qué tan dispersos están los resultados)"""
        if not analyzed_articles:
            return 0.0

        scores = []
        for article in analyzed_articles:
            sentiment_data = article.get('sentiment_analysis', {})
            final_sentiment = sentiment_data.get('final_sentiment', {})
            avg_score = final_sentiment.get('average_score', 0)
            scores.append(avg_score)

        if len(scores) < 2:
            return 0.0

        # Calcular desviación estándar
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        return variance ** 0.5

    def _calculate_confidence_distribution(self, analyzed_articles):
        """Calcula la distribución de confianza de los análisis"""
        if not analyzed_articles:
            return {'high': 0, 'medium': 0, 'low': 0}

        confidence_buckets = {'high': 0, 'medium': 0, 'low': 0}

        for article in analyzed_articles:
            sentiment_data = article.get('sentiment_analysis', {})
            confidence = sentiment_data.get('confidence', 0)

            if confidence >= 0.8:
                confidence_buckets['high'] += 1
            elif confidence >= 0.5:
                confidence_buckets['medium'] += 1
            else:
                confidence_buckets['low'] += 1

        return confidence_buckets

    def get_market_summary_only(self):
        """Obtiene solo el resumen de mercado sin analizar artículos"""
        return self.market_summary.get_market_summary()

    def analyze_with_market_summary(self, articles):
        """Analiza artículos incluyendo resumen de mercado"""
        return self.analyze_multiple_articles(articles, include_market_summary=True)

if __name__ == "__main__":
    # Test del analizador
    analyzer = FinancialSentimentAnalyzer()
    
    # Artículo de prueba
    test_article = {
        'title': 'Stock Market Soars to Record High as Economy Shows Strong Growth',
        'description': 'Markets rallied today with significant gains across all sectors, driven by positive earnings reports and optimistic economic indicators.',
        'source': 'Test'
    }
    
    result = analyzer.analyze_article(test_article)
    print(f"Sentiment: {result['sentiment_analysis']['final_sentiment']['sentiment']}")
    print(f"Average Score: {result['sentiment_analysis']['final_sentiment']['average_score']:.3f}")
    print(f"Confidence: {result['sentiment_analysis']['confidence']:.3f}")