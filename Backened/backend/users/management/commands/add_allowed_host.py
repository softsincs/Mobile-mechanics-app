from django.core.management.base import BaseCommand
from pathlib import Path
from django.conf import settings


class Command(BaseCommand):
    help = 'Add a host to dynamic_allowed_hosts.txt so it is included in ALLOWED_HOSTS.'

    def add_arguments(self, parser):
        parser.add_argument('host', nargs='?', help='Hostname or IP to allow')

    def handle(self, *args, **options):
        host = options.get('host')
        if not host:
            host = input('Enter host (e.g. 206.189.185.16 or example.com): ').strip()
        if not host:
            self.stderr.write('No host provided; aborting.')
            return

        path = Path(settings.BASE_DIR) / 'dynamic_allowed_hosts.txt'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)

        # Read existing
        with path.open('r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]

        if host in lines:
            self.stdout.write(self.style.SUCCESS(f'{host} already present in {path}'))
            return

        with path.open('a', encoding='utf-8') as f:
            f.write(host + '\n')

        self.stdout.write(self.style.SUCCESS(f'Added {host} to {path}'))
