from typing import Any
from django.core.management.base import BaseCommand

from SUBS import UTILS




#!->Dajngo core management commands
def handle(self, *args, **options):
        #1->Grab all existing user subscription
        UTILS.syncsubs_groups_perms()