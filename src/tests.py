from django.test import TestCase, Client
from django.core.cache import cache
# from .views import get_recipe
# from .models import Recipe
from datetime import datetime, timedelta
from .refreshHandler import clean_cache_task
from pathlib import Path

class CleanCacheTaskTest(TestCase):
    def test_cache_cleanup(self)-> None:
        # Add a file to cache that has a timestamp older than now
        old_file_data = {
            'srcPath': '/path/to/old_file',
            'cachePath': '/path/to/old_cache',
            'timeStamp': int((datetime.now() - timedelta(minutes=10)).timestamp())
        }
        cache.set('/path/to/old_file', old_file_data)
        
        # Add a file to cache that has a timestamp newer than now
        new_file_data = {
            'srcPath': '/path/to/new_file',
            'cachePath': '/path/to/new_cache',
            'timeStamp': int((datetime.now() + timedelta(seconds=30)).timestamp())
        }
        cache.set('/path/to/new_file', new_file_data)

        # Run the clean_cache_task synchronously
        clean_cache_task.now(1)

        # Assert that the old_file_data was removed from the cache
        self.assertIsNone(cache.get('/path/to/old_file'))

        # Assert that the new_file_data is still in the cache
        self.assertIsNotNone(cache.get('/path/to/new_file'))

class HandlePostTest(TestCase):
    def test_handle_post_new_entry(self) -> None:
        client = Client()
        module_root = '/path/to/module_root'
        fpath = '/path/to/fpath'
        cache_root = '/path/to/cache_root'
        src_path = f"{module_root}{fpath}"
        cache.delete(src_path)  # Ensure the cache is empty to start with

        response = client.post('/handle_post/', {
            'module_root': module_root,
            'fpath': fpath,
            'cache_root': cache_root,
        })
        self.assertEqual(response.status_code, 200)

        # Check that the data has been added to the cache
        cached_data = cache.get(src_path)
        self.assertIsNotNone(cached_data)

        # Verify the content of cached_data
        self.assertEqual(cached_data['srcPath'], src_path)
        self.assertEqual(cached_data['cachePath'], f"{cache_root}{fpath}")
        self.assertIsInstance(cached_data['timeStamp'], int)

    def test_handle_post_existing_entry(self) -> None:
        client = Client()
        module_root = '/path/to/module_root1'
        fpath = '/path/to/fpath1'
        cache_root = '/path/to/cache_root1'
        src_path = f"{module_root}{fpath}"

        # Create an initial cache entry
        initial_data: dict = {
            'srcPath': src_path,
            'cachePath': f"{cache_root}{fpath}",
            'timeStamp': int((datetime.now() + timedelta(minutes=5)).timestamp())
        }
        cache.set(src_path, initial_data)

        response = client.post('/handle_post/', {
            'module_root': module_root,
            'fpath': fpath,
            'cache_root': cache_root,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['cachePath'], f"{cache_root}{fpath}")
        

        



        # Check that the data has not been altered in the cache
        cached_data = cache.get(src_path)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, initial_data)