#betting/models.py
from django.db import models
from account.models import User, Profile
from core.models import League, Team,Match, SPORT_CHOICES
from django.utils import timezone
from .market_type import (
    FOOTBALL_MARKET_CHOICES, BASKETBALL_MARKET_CHOICES,
    TENNIS_MARKET_CHOICES, CRICKET_MARKET_CHOICES,
    RUGBY_MARKET_CHOICES, HOCKEY_MARKET_CHOICES,
    VOLLEYBALL_MARKET_CHOICES, BASEBALL_MARKET_CHOICES,
    AMERICAN_FOOTBALL_MARKET_CHOICES, BOXING_MMA_MARKET_CHOICES
)

class MarketType(models.Model):
    sport = models.CharField(max_length=100, choices=SPORT_CHOICES)
    name = models.CharField(max_length=100)
    market_key = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_available_markets(sport):
        market_choices = {
            'football': FOOTBALL_MARKET_CHOICES,
            'basketball': BASKETBALL_MARKET_CHOICES,
            'tennis': TENNIS_MARKET_CHOICES,
            'cricket': CRICKET_MARKET_CHOICES,
            'rugby': RUGBY_MARKET_CHOICES,
            'hockey': HOCKEY_MARKET_CHOICES,
            'volleyball': VOLLEYBALL_MARKET_CHOICES,
            'baseball': BASEBALL_MARKET_CHOICES,
            'american_football': AMERICAN_FOOTBALL_MARKET_CHOICES,
            'boxing': BOXING_MMA_MARKET_CHOICES,
            'mixed_martial_arts': BOXING_MMA_MARKET_CHOICES,
        }
        return market_choices.get(sport, [])

    def __str__(self):
        return f"{self.name} ({self.sport})"

    class Meta:
        unique_together = ('sport', 'market_key')

        verbose_name_plural = "Market Types"

class Odds(models.Model):
    market_type = models.ForeignKey(MarketType, on_delete=models.CASCADE, related_name='odds')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='odds')
    odds_value = models.FloatField()
    odds_type = models.CharField(max_length=50, choices=[('decimal', 'Decimal'), ('fractional', 'Fractional'), ('moneyline', 'Moneyline')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.market_type} - {self.odds_value} ({self.odds_type})"

    class Meta:
        unique_together = ('market_type', 'match')

        verbose_name_plural = "Odds"

class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bets')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='bets')
    market_type = models.ForeignKey(MarketType, on_delete=models.CASCADE, related_name='bets')
    odds = models.ForeignKey(Odds, on_delete=models.CASCADE, related_name='bets')
    stake = models.FloatField()
    potential_return = models.FloatField()
    bet_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('won', 'Won'), ('lost', 'Lost')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.match} - {self.market_type} - {self.bet_status}"

    class Meta:
        verbose_name_plural = "Bets"
        ordering = ['-created_at']
