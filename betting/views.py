from django.shortcuts import render
from django.views.generic import ListView
from .models import MarketType
from core.models import Match

class MarketTypeListView(ListView):
    model = MarketType
    template_name = 'betting/market_list.html'
    context_object_name = 'markets'

    def get_queryset(self):
        sport = self.kwargs.get('sport')
        if sport:
            return MarketType.objects.filter(sport=sport, is_active=True)
        return MarketType.objects.filter(is_active=True)

def match_betting_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    markets = MarketType.get_available_markets(match.sport)
    context = {
        'match': match,
        'markets': markets,
    }
    return render(request, 'betting/match_betting.html', context)
