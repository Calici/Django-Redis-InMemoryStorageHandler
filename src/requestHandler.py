from django.core.cache import cache
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta


import pathlib
from django.core.exceptions import ObjectDoesNotExist
from typing import Iterable
class ImageCache:
    TTL: timedelta = timedelta(minutes=5)
    
    def __init__(self, module_root : pathlib.Path, fpath : pathlib.Path, cache_root: pathlib.Path):
        self.src_path: str = f"{module_root}{fpath}"
        self.cache_path: str = f"{cache_root}{fpath}"
        self.timeStamp: int=int((datetime.now() + ImageCache.TTL).timestamp())
        
    def save(self):
        data: dict = {
            'srcPath': self.src_path,
            'cachePath': self.cache_path,
            'timeStamp': self.timeStamp
        }
        # Set the cache key to the data dictionary
        cache.set(self.src_path, data)
        
    def delete(self):
        for key in cache.iter_keys('*'):
            cached_data = cache.get(key)
            if ImageCache.is_outdated(ImageCache, cached_data):
                    cache.delete(key)
#     raise NotImplementedError
    def get(self, src_path)->dict:
        self.save()
        return cache.get(src_path)


    def is_outdated(self, cached_data) -> bool:
        return cached_data['timeStamp'] < int(datetime.now().timestamp())
# 
    def entries(self)-> None:  
        all_keys =cache.keys("*")
        for key in all_keys:
            values = cache.get(key)
            print(f"\nsrcPath: {values['srcPath']}, cachePath: {values['cachePath']}, timeStamp: {values['timeStamp']}")

  
@csrf_exempt
def handle_post(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        module_root: str = request.POST.get('module_root')
        fpath: str = request.POST.get('fpath')
        cache_root: str = request.POST.get('cache_root')
        
        imageCache=ImageCache(module_root, fpath, cache_root)
        cached_data: dict = imageCache.get(imageCache.src_path)
        if cached_data is not None:
            # If an entry exists, return the cachePath
            return JsonResponse({'status': 'success','cachePath': cached_data['cachePath']})

        imageCache.save()
        imageCache.entries()
        return JsonResponse({'status': 'success', 'cachePath': imageCache.cache_path})
    else:
        return JsonResponse({'status': 'invalid request'}, status=400)
