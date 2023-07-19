from __future__ import annotations
from django.core.cache import cache
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist

import pathlib
from typing import Iterable

class ImageCache:
    TTL: timedelta = timedelta(minutes=5)

    def __init__(self, srcPath: pathlib.Path, cachePath: pathlib.Path, timeStamp: int):
        self.srcPath = pathlib.Path(srcPath)
        self.cachePath = pathlib.Path(cachePath)
        self.timeStamp = timeStamp

    
    def save(self):
        data: dict = {
            'srcPath': str(self.srcPath),
            'cachePath': str(self.cachePath),
            'timeStamp': self.timeStamp
        }
        # Set the cache key to the data dictionary
        cache.set(str(self.srcPath), data)

    def delete(self):
        cache.delete(str(self.srcPath))

    def update_ttl(self, commit: bool = False):
        self.timeStamp = int((datetime.now() + ImageCache.TTL).timestamp())
        if commit:
            self.save()

    def is_outdated(self) -> bool:
        return self.timeStamp < int(datetime.now().timestamp())

    @staticmethod
    def get(srcPath: pathlib.Path) -> ImageCache:
        entry = cache.get(str(srcPath))
        if entry is None:
            raise ObjectDoesNotExist
        else:
            return ImageCache(**entry)

    @staticmethod
    def create(module_root: pathlib.Path, fpath: pathlib.Path, cache_root: pathlib.Path) -> ImageCache:
        srcPath = module_root / fpath
        cachePath = cache_root / fpath
        timeStamp = int((datetime.now() + ImageCache.TTL).timestamp())
        return ImageCache(srcPath, cachePath, timeStamp)

    @staticmethod
    def entries() -> Iterable[ImageCache]:
        all_keys = cache.keys("*")
        for key in all_keys:
            values = cache.get(key)
            yield ImageCache(**values)

@csrf_exempt
def handle_post(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        module_root = pathlib.Path(request.POST.get('module_root'))
        fpath = pathlib.Path(request.POST.get('fpath'))
        cache_root = pathlib.Path(request.POST.get('cache_root'))

        try:
            img_cache = ImageCache.get(module_root / fpath)
            img_cache.update_ttl(commit=True)
        except ObjectDoesNotExist:
            img_cache = ImageCache.create(module_root, fpath, cache_root)
            img_cache.save()
        return JsonResponse({'status': 'success', 'cachePath': str(img_cache.cachePath)})
    else:
        return JsonResponse({'status': 'invalid request'}, status=400)
