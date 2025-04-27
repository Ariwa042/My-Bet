import asyncio
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from django.utils import timezone
from core.models import Match, League, Team
from core.odds_manager import OddsManager
from betting.market_type import *

class OddsPortalScraper:
    MARKET_MAPPING = {
        'football': {
            '1x2': '1x2',
            'asian-handicap': ('handicap', lambda x: float(re.search(r'([+-]?\d+\.?\d*)', x).group(1))),
            'over-under': ('over_under', lambda x: float(re.search(r'(\d+\.?\d*)', x).group(1))),
            'correct-score': 'correct_score',
            'both-teams-to-score': 'btts',
            'half-time/full-time': 'half_time_full_time',
            'total-goals': 'total_goals'
        },
        # ... keep existing market mappings ...
    }

    def __init__(self):
        self.base_url = "https://www.oddsportal.com"
        self.sport_paths = {
            'football': 'soccer',
            'basketball': 'basketball',
            'hockey': 'hockey'
        }
        self.odds_manager = OddsManager()

    async def scrape_matches(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            try:
                for sport_key, sport_path in self.sport_paths.items():
                    page = await context.new_page()
                    await self._process_sport(page, sport_key, sport_path)
                    await page.close()
            finally:
                await browser.close()

    async def _process_sport(self, page, sport_key, sport_path):
        try:
            await page.goto(f"{self.base_url}/{sport_path}/")
            await page.wait_for_selector('.main-menu-text', timeout=15000)
            
            leagues = await self._get_leagues(page, sport_key)
            for league in leagues:
                await self._process_league(page, league, sport_key)

        except Exception as e:
            print(f"Error scraping {sport_key}: {str(e)}")

    async def _get_leagues(self, page, sport):
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        leagues = []

        for link in soup.select('.main-menu-text a[href]'):
            url = link['href']
            if f"/{self.sport_paths[sport]}/" not in url:
                continue

            league_name = re.sub(r'\s+', ' ', link.text.strip())
            country, league_path = self._extract_league_info(url)
            
            league, _ = League.objects.update_or_create(
                name=league_name,
                sport=sport,
                defaults={
                    'oddsportal_path': league_path,
                    'country': country
                }
            )
            leagues.append(league)
        return leagues

    async def _process_league(self, page, league, sport):
        try:
            url = f"{self.base_url}{league.oddsportal_path}/"
            await page.goto(url)
            await page.wait_for_selector('.table-main', timeout=15000)
            
            while True:
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                for row in soup.select('.table-main tr.deactivate'):
                    await self._process_match_row(row, league, sport)
                
                next_btn = await page.query_selector('a[data-cy="pagination-next"]:not(.disabled)')
                if not next_btn:
                    break
                
                await next_btn.click()
                await page.wait_for_load_state('networkidle')

        except Exception as e:
            print(f"Error processing league {league.name}: {str(e)}")

    async def _process_match_row(self, row, league, sport):
        try:
            match_data = self._extract_match_data(row, league, sport)
            if not match_data:
                return

            match = await self._get_or_create_match(match_data)
            if not match:
                return

            # Process pre-match odds
            odds_data = self._extract_odds_data(row)
            if odds_data:
                for market, bookmaker_odds in odds_data.items():
                    for bookmaker, odds in bookmaker_odds.items():
                        self.odds_manager.save_odds(
                            match_id=match.id,
                            market=market,
                            bookmaker_name=bookmaker,
                            odds_data=odds,
                            is_live=match.status == 'live'
                        )

        except Exception as e:
            print(f"Error processing match row: {str(e)}")

    def _extract_match_data(self, row, league, sport):
        try:
            team_cell = row.select_one('.table-participant')
            teams = [t.strip() for t in team_cell.get_text(separator='|').split('|') if t.strip()]
            if len(teams) != 2:
                return None

            time_str = row.select_one('.datet').get_text(strip=True)
            match_time = self._parse_datetime(time_str)
            
            return {
                'home_team_name': teams[0],
                'away_team_name': teams[1],
                'league': league,
                'sport': sport,
                'match_date': match_time.date(),
                'match_time': match_time.time(),
                'status': 'live' if 'live' in row.get('class', []) else 'scheduled'
            }
        except Exception:
            return None

    async def _get_or_create_match(self, match_data):
        try:
            home_team, _ = Team.objects.get_or_create(
                name=match_data['home_team_name'],
                league=match_data['league'],
                defaults={'sport': match_data['sport']}
            )
            away_team, _ = Team.objects.get_or_create(
                name=match_data['away_team_name'],
                league=match_data['league'],
                defaults={'sport': match_data['sport']}
            )

            match, _ = Match.objects.update_or_create(
                home_team=home_team,
                away_team=away_team,
                match_date=match_data['match_date'],
                defaults={
                    'league': match_data['league'],
                    'sport': match_data['sport'],
                    'match_time': match_data['match_time'],
                    'status': match_data['status']
                }
            )
            return match
        except Exception as e:
            print(f"Error creating match: {str(e)}")
            return None

    def _extract_odds_data(self, row):
        odds_data = {}
        
        for odds_cell in row.select('.odds-nowrp'):
            market = odds_cell.get('data-market', '').lower().replace(' ', '-')
            bookmaker = odds_cell.get('data-bk', 'unknown')
            
            market_info = self.MARKET_MAPPING.get(odds_cell.get('data-sport'), {}).get(market)
            if not market_info:
                continue

            if isinstance(market_info, tuple):
                market_type, param_extractor = market_info
                parameter = param_extractor(odds_cell.get_text())
            else:
                market_type = market_info
                parameter = None

            odds_values = self._parse_odds_values(odds_cell)
            if odds_values:
                if market_type not in odds_data:
                    odds_data[market_type] = {}
                
                odds_data[market_type][bookmaker] = {
                    **odds_values,
                    'parameter': parameter
                }

        return odds_data

    def _parse_odds_values(self, cell):
        values = []
        for span in cell.select('span'):
            try:
                values.append(float(span.text.strip()))
            except (ValueError, TypeError):
                continue

        if not values:
            return None

        if len(values) == 3:
            return {'home': values[0], 'draw': values[1], 'away': values[2]}
        elif len(values) == 2:
            return {'home': values[0], 'away': values[1]}
        else:
            return {'home': values[0]}

    def _parse_datetime(self, time_str):
        try:
            date_part, time_part = re.match(r'(\w+)\s+(\d+:\d+)', time_str).groups()
            base_date = timezone.now().date()
            
            if date_part.lower() == 'tomorrow':
                base_date += timedelta(days=1)
            
            return timezone.make_aware(
                datetime.combine(
                    base_date,
                    datetime.strptime(time_part, "%H:%M").time()
                )
            )
        except Exception:
            return timezone.now()

    def _extract_league_info(self, url):
        parts = url.strip('/').split('/')
        if len(parts) >= 3:
            country = parts[1].replace('-', ' ').title()
            league_path = '/'.join(parts[:3])
            return country, f"/{league_path}"
        return 'Unknown', url

async def run_scraper():
    scraper = OddsPortalScraper()
    await scraper.scrape_matches()