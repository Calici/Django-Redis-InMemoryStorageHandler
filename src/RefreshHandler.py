from background_task import background
from django.core.cache import cache
from datetime import datetime
import time
from .requestHandler import ImageCache

# the schedule part is the maximum limit of time that the clean_cache_task can run
#time.sleep(25) specifies the time that the clean_cache_task will wait before running
@background(schedule=120)  
def clean_cache_task(howLongToWaitInSec: int = 25) -> None:
    time.sleep(howLongToWaitInSec)
    ImageCache.delete(ImageCache)
    print("Cache cleaned")

# The clean cache function is called in the src\apps.py file
