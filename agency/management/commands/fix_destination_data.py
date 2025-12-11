from django.core.management.base import BaseCommand
from app_admin.models import Destination
from agency.models import Travelpackage

class Command(BaseCommand):
    help = 'Fix travel package destination data'

    def handle(self, *args, **options):
        # First, create the Munnar destination if it doesn't exist
        destination, created = Destination.objects.get_or_create(
            name='Munnar',
            defaults={
                'description': 'Munnar is a town in the Western Ghats mountain range in Kerala, India.',
                'location': 'Kerala, India'
            }
        )
        
        # Update any travel packages that have invalid destination_id
        try:
            invalid_package = Travelpackage.objects.get(pk=1)
            invalid_package.destination = destination
            invalid_package.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated travel package destination to {destination.name}'))
        except Travelpackage.DoesNotExist:
            self.stdout.write(self.style.WARNING('Travel package with ID 1 not found'))