# Django-Redis-InMemoryStorageHandler


1. Clone the repository:
   ```bash
   git clone https://github.com/Calici/Django-Redis-InMemoryStorageHandler.git
   ```

2. Change to the cloned repository directory:
   ```bash
   cd Django-Redis-InMemoryStorageHandler
   ```

3. Install the required package using pip:
   ```bash
   pip install django4-background-tasks
   ```

4. Start the Docker container for Redis in detached mode:
   ```bash
   docker-compose up -d
   ```

5. Run the Django server:
   ```bash
   python manage.py runserver
   ```

   Note: If you visit the page, you may not see anything displayed.

6. Allows the use of the RefreshHandler function for Background Task handling(Write on new terminal):
   ```bash
   python manage.py process_tasks
   ```

7. Run the tests(Write on new terminal):
   ```bash
   python manage.py test
   ```

Files to check related to the in-memory cache:
 
- `docker-compose.yaml` :  Run a dockerized Redis Server
- `src/refreshHandler.py` : 
- `src/requestHandler.py` : Request Handling + Redis Schema Specification within the Request Handler
- `src/tests.py` : Unit Tests
- `src/app.py` (calls the `refreshHandler`)
- `src/urls.py`
- `Redis/settings.py` (refer to [this link](https://www.dragonflydb.io/faq/how-to-use-redis-with-django) for more information)

