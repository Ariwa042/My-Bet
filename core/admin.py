from django.contrib import admin
from .models import League, Team, Match, Deposit,Withdrawal, Cryptocurrency

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'country', 'created_at')
    list_filter = ('sport', 'country')
    search_fields = ('name', 'country')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'league', 'created_at')
    list_filter = ('sport', 'league')
    search_fields = ('name', 'league__name')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'match_date', 'status', 'sport')
    list_filter = ('status', 'sport', 'league')
    search_fields = ('home_team__name', 'away_team__name')
    date_hierarchy = 'match_date'

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'cryptocurrency', 'status', 'created_at')
    list_filter = ('status', 'cryptocurrency')
    search_fields = ('user__email', 'amount')
    ordering = ('-created_at',)

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'cryptocurrency', 'status', 'created_at')
    list_filter = ('status', 'cryptocurrency')
    search_fields = ('user__email', 'amount')
    ordering = ('-created_at',)

@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo', 'symbol')
    search_fields = ('name', 'symbol')
