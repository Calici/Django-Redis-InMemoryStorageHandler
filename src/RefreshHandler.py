from background_task import background
from datetime import datetime
import time
from .requestHandler import ImageCache

# the schedule part is the maximum limit of time that the clean_cache_task can run
#time.sleep(25) specifies the time that the clean_cache_task will wait before running
@background(schedule=120)
def clean_cache_task(howLongToWaitInSec: int = 25) -> None:
    time.sleep(howLongToWaitInSec)
    for entry in ImageCache.entries():
        if entry.is_outdated():
            entry.delete()
    print("Cache cleaned")

