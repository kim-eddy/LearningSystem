from django.core.management.base import BaseCommand
from MyProject.scrapper import scraped_data  
from MyProject.models import Topic  

class Command(BaseCommand):
    help = 'Scrape learning content for specified topics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topics',
            nargs='+',
            type=str,
            help='List of topics to scrape (e.g., python loops functions)',
        )

    def handle(self, *args, **options):
        topics = options['topics']
        if not topics:
            # fallback: use topic names from database
            topics = list(Topic.objects.values_list('name', flat=True))

        self.stdout.write(self.style.NOTICE(f"Scraping topics: {topics}"))

        results = scraped_data(topics)

        self.stdout.write(self.style.SUCCESS(f"Scraped and stored {len(results)} items into MongoDB."))
