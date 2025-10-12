import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import logging
from datetime import datetime
from config import Config

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

class FinancialSentimentAnalyzer:
    """Analizador especializado en sentimientos financieros"""
    
    def __init__(self):
        self.vader = VaderAnalyzer()
        self.textblob = TextBlobAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        # Palabras clave financieras con connotación positiva/negativa
        self.positive_financial_words = {
            'growth', 'profit', 'gain', 'rise', 'surge', 'bull', 'bullish', 'rally',
            'upward', 'increase', 'strong', 'boom', 'recovery', 'optimistic', 'positive',
            'beat expectations', 'outperform', 'milestone', 'record high', 'breakthrough'
        }
        
        self.negative_financial_words = {
            'loss', 'decline', 'fall', 'drop', 'crash', 'bear', 'bearish', 'recession',
            'downward', 'decrease', 'weak', 'collapse', 'crisis', 'pessimistic', 'negative',
            'miss expectations', 'underperform', 'concern', 'risk', 'uncertainty', 'volatile'
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
        """Analiza palabras clave específicas del ámbito financiero"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_financial_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_financial_words if word in text_lower)
        
        total_words = positive_count + negative_count
        
        if total_words == 0:
            return {'sentiment': 'neutral', 'score': 0, 'positive_keywords': 0, 'negative_keywords': 0}
        
        score = (positive_count - negative_count) / total_words
        
        if score > 0.2:
            sentiment = 'positive'
        elif score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_keywords': positive_count,
            'negative_keywords': negative_count
        }
    
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
    
    def analyze_multiple_articles(self, articles):
        """Analiza múltiples artículos y proporciona un resumen general"""
        if not articles:
            return {'error': 'No articles to analyze'}
        
        analyzed_articles = []
        sentiment_summary = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in articles:
            try:
                analysis = self.analyze_article(article)
                analyzed_articles.append(analysis)
                
                final_sentiment = analysis['sentiment_analysis']['final_sentiment']['sentiment']
                sentiment_summary[final_sentiment] += 1
                
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
        
        return {
            'analyzed_articles': analyzed_articles,
            'summary': {
                'total_articles': total_articles,
                'sentiment_breakdown': sentiment_summary,
                'overall_sentiment': overall_sentiment,
                'positive_percentage': (sentiment_summary['positive'] / total_articles * 100) if total_articles > 0 else 0,
                'negative_percentage': (sentiment_summary['negative'] / total_articles * 100) if total_articles > 0 else 0,
                'neutral_percentage': (sentiment_summary['neutral'] / total_articles * 100) if total_articles > 0 else 0
            },
            'timestamp': datetime.now().isoformat()
        }

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