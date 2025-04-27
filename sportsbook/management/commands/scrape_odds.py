import asyncio
from django.core.management.base import BaseCommand
from sportsbook.oddsportal import run_scraper

class Command(BaseCommand):
    help = 'Scrape odds from OddsPortal'

    def handle(self, *args, **options):
        self.stdout.write('Starting odds scraper...')
        asyncio.run(run_scraper())
        self.stdout.write(self.style.SUCCESS('Successfully scraped odds'))