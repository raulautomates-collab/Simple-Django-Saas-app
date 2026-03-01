from typing import Any
from django.core.management.base import BaseCommand
from SUBS import UTILS




class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument("--clear-dangling",action='store_true',default=False)


    def handle(self, *args, **options:Any):
        #1->Grab all existing user subscription
        print(options)
        clear_dangling=options.get('clear_dangling')
        if clear_dangling:
          print('Clearing dangling subs not in use in stripe')  
          UTILS.cleardanglingsubs()
        else:
            print('Sync active subs')
            done=UTILS.refresh_user_subs(active_only=True)
            if done:
                print(done)
            print('Done')