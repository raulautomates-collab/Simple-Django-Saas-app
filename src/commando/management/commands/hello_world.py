from typing import Any
from django.core.management.base import BaseCommand

class Command(BaseCommand):#basic hello world function
    
    def handle(self, *args: Any, **options: Any):
        print('Homie ,you trippin,gay ass motherfuc**er')