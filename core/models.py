#core/models.py
from django.db import models
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField
from django.db.models.signals import post_save
from django.dispatch import receiver


SPORT_CHOICES = [
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('tennis', 'Tennis'),
        ('cricket', 'Cricket'),
        ('rugby', 'Rugby'),
        ('hockey', 'Hockey'),
        ('volleyball', 'Volleyball'),
        ('baseball', 'Baseball'),
        ('american_football', 'American Football'),
        ('boxing', 'Boxing'),
        ('mixed_martial_arts', 'Mixed Martial Arts'),
    ]

TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
]

STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
]

class Cryptocurrency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    wallet_address = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='cryptocurrencies/', blank=True, null=True)

    def __str__(self):
        return f'{self.name} ({self.symbol})'

class League(models.Model):
    name = models.CharField(max_length=100)
    sport = models.CharField(max_length=100, choices=SPORT_CHOICES, default='football')
#    season = models.CharField(max_length=100, blank=True, null=True)
#    start_date = models.DateField(blank=True, null=True)
#    end_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='leagues/logos/', blank=True, null=True)
    oddsportal_path = models.CharField(max_length=200, blank=True, 
        help_text="Suffix for constructing OddsPortal URL")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Leagues"

    def __str__(self):
        return f"{self.name} ({self.country})"
    
class Team(models.Model):
    name = models.CharField(max_length=100)
    sport = models.CharField(max_length=100, choices=SPORT_CHOICES, default='football')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='teams', blank=True, null=True)
    logo = models.ImageField(upload_to='teams/logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Teams"

    def __str__(self):
        return f"{self.name} ({self.league.name})"
    
class Match(models.Model):
    sport = models.CharField(max_length=100, choices=SPORT_CHOICES, default='football')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='matches', blank=True, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_fixtures')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_fixtures')
    home_team_score = models.IntegerField(default=0, blank=True, null=True)
    away_team_score = models.IntegerField(default=0, blank=True, null=True)
    match_date = models.DateTimeField()
    match_time = models.TimeField()
    status = models.CharField(max_length=20, choices=[('scheduled', 'Scheduled'), ('live', 'Live'), ('finished', 'Finished')], default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"

class Bookmaker(models.Model):
    name = models.CharField(max_length=100)
    oddsportal_name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='bookmakers/logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-priority', 'name']

class Odds(models.Model):
    ODDS_TYPE_CHOICES = [
        ('decimal', 'Decimal'),
        ('fractional', 'Fractional'),
        ('american', 'American'),
    ]

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_odds')
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE, related_name='bookmaker_odds')
    market = models.CharField(max_length=50)
    parameter = models.FloatField(null=True, blank=True, help_text="For handicap, over/under markets")
    home_odds = models.DecimalField(max_digits=7, decimal_places=2)
    draw_odds = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    away_odds = models.DecimalField(max_digits=7, decimal_places=2)
    odds_type = models.CharField(max_length=20, choices=ODDS_TYPE_CHOICES, default='decimal')
    is_live = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Odds"
        unique_together = ('match', 'bookmaker', 'market', 'parameter')
        indexes = [
            models.Index(fields=['match', 'market', 'is_live']),
            models.Index(fields=['last_updated']),
        ]

    def __str__(self):
        return f"{self.match} - {self.market} ({self.bookmaker})"

class Deposit(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='deposits')
    deposit_id = ShortUUIDField(unique=True, length=10, max_length=15)
    cryptocurrency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=8)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='deposit')
    
    class Meta:
        verbose_name_plural = "Deposits"

    def __str__(self):
        return f"Deposit of {self.amount} {self.cryptocurrency} by {self.user} ({self.status})"

class Withdrawal(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='withdrawals')
    withdrawal_id = ShortUUIDField(unique=True, length=10, max_length=15)
    cryptocurrency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=8)
    destination_address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='withdrawal')

    class Meta:
        verbose_name_plural = "Withdrawals"
    def __str__(self):
        return f"Withdrawal of {self.amount} {self.cryptocurrency} by {self.user} ({self.status})"
    

@receiver(post_save, sender=Deposit)
def update_balance_on_deposit(sender, instance, **kwargs):
    if instance.status == 'completed':
        profile = instance.user.profile
        profile.balance += instance.amount
        profile.save()

@receiver(post_save, sender=Withdrawal)
def update_balance_on_withdrawal(sender, instance, **kwargs):
    if instance.status == 'completed':
        profile = instance.user.profile
        if profile.balance >= instance.amount:
            profile.balance -= instance.amount
            profile.save()

#update transaction when deposit or withdrawal status changes
#@receiver(post_save, sender=Deposit)
#@receiver(post_save, sender=Withdrawal)
#def update_transaction_status(sender, instance, **kwargs):
#    try:
#        # Update the corresponding transaction when deposit or spend status changes
#        transaction_type = 'deposit' if sender == Deposit else 'withdrawal'
#        transaction = Transaction.objects.filter(user=instance.user, type=transaction_type, amount=instance.amount).first()
#        if transaction and instance.status != transaction.status:
#            transaction.status = instance.status
#            transaction.save()
#    except Transaction.DoesNotExist:
#        pass