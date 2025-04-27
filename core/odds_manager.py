from django.core.cache import cache
from django.conf import settings
from .models import Odds, Match, Bookmaker
from decimal import Decimal

class OddsManager:
    @staticmethod
    def get_cache_key(match_id, market, bookmaker_id=None):
        if bookmaker_id:
            return f"odds:{match_id}:{market}:{bookmaker_id}"
        return f"odds:{match_id}:{market}"

    @staticmethod
    def cache_live_odds(match_id, market, odds_data, bookmaker_id=None):
        """Cache live odds with a short timeout"""
        cache_key = OddsManager.get_cache_key(match_id, market, bookmaker_id)
        cache.set(cache_key, odds_data, timeout=settings.LIVE_ODDS_CACHE_TIMEOUT)

    @staticmethod
    def get_odds(match_id, market, bookmaker_id=None, is_live=False):
        """Get odds from cache if live, otherwise from database"""
        if is_live:
            cache_key = OddsManager.get_cache_key(match_id, market, bookmaker_id)
            cached_odds = cache.get(cache_key)
            if cached_odds:
                return cached_odds

        # Fallback to database
        try:
            query = {
                'match_id': match_id,
                'market': market,
                'is_live': is_live
            }
            if bookmaker_id:
                query['bookmaker_id'] = bookmaker_id

            return Odds.objects.filter(**query).order_by('-bookmaker__priority').first()
        except Odds.DoesNotExist:
            return None

    @staticmethod
    def save_odds(match_id, market, bookmaker_name, odds_data, is_live=False):
        """Save odds to database and cache if live"""
        try:
            match = Match.objects.get(id=match_id)
            bookmaker, _ = Bookmaker.objects.get_or_create(
                oddsportal_name=bookmaker_name,
                defaults={'name': bookmaker_name}
            )

            odds_values = {
                'match': match,
                'bookmaker': bookmaker,
                'market': market,
                'is_live': is_live,
                'home_odds': Decimal(str(odds_data.get('home', 0))),
                'away_odds': Decimal(str(odds_data.get('away', 0)))
            }

            if 'draw' in odds_data:
                odds_values['draw_odds'] = Decimal(str(odds_data['draw']))
            if 'parameter' in odds_data:
                odds_values['parameter'] = odds_data['parameter']

            odds, created = Odds.objects.update_or_create(
                match=match,
                bookmaker=bookmaker,
                market=market,
                defaults=odds_values
            )

            if is_live:
                OddsManager.cache_live_odds(
                    match_id, 
                    market, 
                    odds_values,
                    bookmaker.id
                )

            return odds

        except (Match.DoesNotExist, ValueError) as e:
            print(f"Error saving odds: {str(e)}")
            return None