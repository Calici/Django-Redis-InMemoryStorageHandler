from django.test import TestCase, Client
from django.core.cache import cache
from datetime import datetime, timedelta
from .refreshHandler import clean_cache_task
from .requestHandler import ImageCache
from pathlib import Path

class CleanCacheTaskTest(TestCase):
    def test_cache_cleanup(self) -> None:
        # Add a file to cache that has a timestamp older than now
        old_file = ImageCache(
            srcPath=Path('/path/to/old_file'),
            cachePath=Path('/path/to/old_cache'),
            timeStamp=int((datetime.now() - timedelta(minutes=10)).timestamp())
        )
        cache.set(str(old_file.srcPath), old_file.__dict__)

        # Add a file to cache that has a timestamp newer than now
        new_file = ImageCache(
            srcPath=Path('/path/to/new_file'),
            cachePath=Path('/path/to/new_cache'),
            timeStamp=int((datetime.now() + timedelta(seconds=30)).timestamp())
        )
        cache.set(str(new_file.srcPath), new_file.__dict__)

        # Run the clean_cache_task synchronously
        clean_cache_task.now(1)

        # Assert that the old_file was removed from the cache
        self.assertIsNone(cache.get(str(old_file.srcPath)))

        # Assert that the new_file is still in the cache
        self.assertIsNotNone(cache.get(str(new_file.srcPath)))

class HandlePostTest(TestCase):
    def test_handle_post_new_entry(self) -> None:
        client = Client()
        module_root = Path('/path/to/module_root')
        fpath = Path('/path/to/fpath')
        cache_root = Path('/path/to/cache_root')
        src_path = module_root / fpath
        cache.delete(str(src_path))  # Ensure the cache is empty to start with

        response = client.post('/handle_post/', {
            'module_root': str(module_root),
            'fpath': str(fpath),
            'cache_root': str(cache_root),
        })
        self.assertEqual(response.status_code, 200)

        # Check that the data has been added to the cache
        cached_data = cache.get(str(src_path))
        self.assertIsNotNone(cached_data)

        # Verify the content of cached_data
        self.assertEqual(cached_data['srcPath'], str(src_path))
        self.assertEqual(cached_data['cachePath'], str(cache_root / fpath))
        self.assertIsInstance(cached_data['timeStamp'], int)

    def test_handle_post_existing_entry(self) -> None:
        client = Client()
        module_root = Path('/path/to/module_root1')
        fpath = Path('/path/to/fpath1')
        cache_root = Path('/path/to/cache_root1')
        # print(cache_root)
        src_path = module_root / fpath

        # Create an initial cache entry
        initial_file = ImageCache(
            srcPath=src_path,
            cachePath=cache_root / fpath,
            timeStamp=int((datetime.now() + timedelta(minutes=5)).timestamp())
        )
        initial_file.save()  # Changed from cache.set() to use ImageCache's save() method

        response = client.post('/handle_post/', {
            'module_root': str(module_root),
            'fpath': str(fpath),
            'cache_root': str(cache_root),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['cachePath'], str(cache_root / fpath))

        # Check that the data has not been altered in the cache
        cached_data = ImageCache.get(src_path)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data.srcPath, initial_file.srcPath)
        self.assertEqual(cached_data.cachePath, initial_file.cachePath)
