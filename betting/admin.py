from django.contrib import admin
from .models import MarketType, Odds, Bet
# Register your models here.

@admin.register(MarketType)
class MarketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'market_key', 'is_active', 'created_at')
    list_filter = ('sport', 'is_active')
    search_fields = ('name', 'market_key')
    date_hierarchy = 'created_at'

@admin.register(Odds)
class OddsAdmin(admin.ModelAdmin):
    list_display = ('market_type', 'match', 'odds_value', 'odds_type', 'created_at')
    search_fields = ('market_type__name', 'match__home_team__name', 'match__away_team__name')
    list_filter = ('market_type', 'odds_type')
    ordering = ('-created_at',)
    list_per_page = 20
    fieldsets = (
        (None, {
            'fields': ('market_type', 'match', 'odds_value', 'odds_type')
        }),
    )
    readonly_fields = ('created_at',)

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'market_type', 'odds', 'stake', 'potential_return', 'bet_status', 'created_at')
    search_fields = ('user__username', 'match__home_team__name', 'match__away_team__name')
    list_filter = ('bet_status',)
    ordering = ('-created_at',)
    list_per_page = 20
    fieldsets = (
        (None, {
            'fields': ('user', 'match', 'market_type', 'odds', 'stake', 'potential_return', 'bet_status')
        }),
    )
    readonly_fields = ('created_at',)