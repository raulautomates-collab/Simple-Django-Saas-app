from typing import Any
from django.core.management.base import BaseCommand
import helpers
from helpers import downloader
from django.conf import settings

STATICFILES_VENDOR_DIR=getattr(settings,'STATICFILES_VENDOR_DIR')#=>out


#source files
VENDOR_STATICFILES={
    "flowbite.min.css":"https://cdn.jsdelivr.net/npm/flowbite@4.0.1/dist/flowbite.min.css",
    "flowbite.min.js":"https://cdn.jsdelivr.net/npm/flowbite@4.0.1/dist/flowbite.min.js",
    "flowbite.css":"https://cdnjs.cloudflare.com/ajax/libs/flowbite/3.1.2/flowbite.css",
    "flowbite.js":"https://cdnjs.cloudflare.com/ajax/libs/flowbite/3.1.2/flowbite.js"
}


class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any):
        self.stdout.write('Downloading the static files,stop nagging me homie!.Gay ass motherfucker')
        completed_urls=[]

        for name,url in VENDOR_STATICFILES.items():
            
            out_path=STATICFILES_VENDOR_DIR / name
            dl_success=downloader.download_to_local(url,out_path)
            if dl_success:
                completed_urls.append(url)
            else:
                self.stdout.write(self.style.ERROR(f'Failed to download {url}.Try again dawg'))    
            
            print(name,url,out_path)
        if set(completed_urls)==set(VENDOR_STATICFILES.values()):
            self.stdout.write(self.style.SUCCESS('Succesfully updated all vendor static files,now get out before I clip yo ass !'))
        else:
            self.stdout.write(self.style.WARNING('Some files was not updated dawg')) 
            
               