from typing import Any
from django.core.management.base import BaseCommand
from SUBS import UTILS


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('--clear-dangling',action='store_true')

    def handle(self, *args, **options:Any):
        clear_dangling=options.get('clear_dangling')
        if clear_dangling:
         print('Clear dangling not in use active subs in stripe')

         UTILS.cleardanglingsubs()
        else:
            
          print(options)
          print('Done')