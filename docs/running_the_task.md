## Creating Task and Trigger Periodically

### Step 1 : Add Task 

- Create new file called `tasks.py` inside members directory
  ```
  members/
  ├── __init__.py
  ├── admin.py
  ├── apps.py
  ├── models.py
  ├── urls.py
  ├── views.py
  ├── tasks.py
  └── test.py
  ```
  
- Add below contents
  
  ```python
  import datetime
  from myworld.celery import app
  from .models import Job, Blog, JobStats, JobLogs
  import requests
  from bs4 import BeautifulSoup
  from dateutil.parser import parse
  import pytz
  
  utc=pytz.UTC
  
  @app.task(bind=True, name="extract")
  def extract(self, job_id):
      job_obj = Job.objects.get(pk=job_id)
      job_stats_obj = JobStats(job=job_obj, status="IN PROGRESS", start_date=datetime.datetime.now(), no_of_blogs_extracted=0)
      job_stats_obj.save()
      JobLogs(job_stats=job_stats_obj, log="Extraction stated", function_name="extract", date=datetime.datetime.now()).save()
      start_date = job_obj.start_date
      end_date = job_obj.end_date
      start_id = job_obj.start_no
      no_of_articles = job_obj.no_of_blogs
      url = "https://blog.python.org/"
      try:
          data = requests.get(url)
          page_soup = BeautifulSoup(data.text, 'html.parser')
  
          blogs = page_soup.select('div.date-outer')
          article_count = 0
          counter = 1
          for blog in blogs:
              article_count += 1
              if start_id and article_count < int(start_id):
                  continue
              if no_of_articles and counter > int(no_of_articles):
                  continue
              date = blog.select('.date-header span')[0].get_text()
  
              converted_date = parse(date)
              JobLogs(job_stats=job_stats_obj, log=f"Extracting {article_count}", function_name="extract", date=datetime.datetime.now()).save()
              if start_date and utc.localize(converted_date) < start_date:
                  continue
              if end_date and utc.localize(converted_date) > end_date:
                  continue
  
              post = blog.select('.post')[0]
  
              title = ""
              title_bar = post.select('.post-title')
              if len(title_bar) > 0:
                  title = title_bar[0].text
              else:
                  title = post.select('.post-body')[0].contents[0].text
  
              # getting the author and blog time
              post_footer = post.select('.post-footer')[0]
  
              author = post_footer.select('.post-author span')[0].text
  
              time = post_footer.select('abbr')[0].text
  
              blog_obj = Blog(title=title, author=author, release_date=date, blog_time=time)
              blog_obj.save()
              job_stats_obj.no_of_blogs_extracted += job_stats_obj.no_of_blogs_extracted
              job_stats_obj.save()
  
              print("\nTitle:", title.strip('\n'))
              print("Date:", date, )
              print("Time:", time)
              print("Author:", author)
              counter += 1
          JobLogs(job_stats=job_stats_obj, log=f"Total {counter} articles extracted: ", function_name="extract", date=datetime.datetime.now()).save()
          job_stats_obj.end_date = datetime.datetime.now()
          job_stats_obj.total_blogs = article_count
          job_stats_obj.status = "COMPLETED"
          job_stats_obj.save()
          JobLogs(job_stats=job_stats_obj, log="Extraction Done", function_name="extract", date=datetime.datetime.now()).save()
      except Exception as ex:
          JobLogs(job_stats=job_stats_obj, log=str(ex), function_name="extract", date=datetime.datetime.now()).save()
          job_stats_obj.end_date = datetime.datetime.now()
          job_stats_obj.total_blogs = article_count
          job_stats_obj.status = "FAILED"
          job_stats_obj.save()
          JobLogs(job_stats=job_stats_obj, log="Extraction Done", function_name="extract", date=datetime.datetime.now()).save()

  ```
- Crate new view to trigger the task
  - Add below code in views.py file
    ```python
    from members.tasks import extract
    from django.shortcuts import redirect
  
    def python_blog_scraping(request, job_id):
        extract.delay(job_id)
        return redirect('/admin/members/job/')

    ```

- Add Url for above view

  ```python
  path('python_blog_scraping/<int:job_id>', views.python_blog_scraping, name="scraping")
  ```

- Run below curl cmd to trigger the task.

  ```shell
  curl http://0.0.0.0:8000/members/python_blog_scraping/1
  ```
- Please make sure celery is running in worker container.

### Step 2 : Add Run button in job table to trigger the task
- Add below code inside Job class (admin.py)
  ```shell
  def run(self, obj):
    return format_html('<a class="button" href="{}">RUN</a>', reverse('scraping', args=(str(obj.pk))))
  
  run.short_description = 'Run'
  run.allow_tags = True
  list_display = ("job_name", "start_date", "end_date", "no_of_blogs", "start_no", "created_date", "run", "view_stats")
  ```
- click On **RUN** to trigger the task. `http://0.0.0.0:8000/admin/members/job/`

# Periodic Tasks
Using the celery Beat, we can configure tasks to be run periodically. This can be defined either implicitly or explicitly. The thing to keep in mind is to run a single scheduler at a time. Otherwise, this would lead to duplicate tasks. The scheduling depends on the time zone (CELERYTIMEZONE = "Asia/NewYork") configured in the settings.py
We can configure periodic tasks either by manually adding the configurations to the celery.py module or using the django-celery-beat package which allows us to add periodic tasks from the Django Admin by extending the Admin functionality to allow scheduling tasks.
## Manual Configuration
- Add below code to celery.py
  ```shell
  app.conf.beat_schedule = {
      #Scheduler Name
      'run-task-ten-seconds': {
          # Task Name (Name Specified in Decorator)
          'task': 'extract',
          # Schedule
          'schedule': 60.0,
          # Function Arguments
          'args': (1,)
      }
  }
  ```
  Note : Add Proper **job id** in **args**
- Restart your worker
  ```shell
  python -m celery -A myworld worker  -l info
  ```

## Using django-celery-beat
This extension enables the user to store periodic tasks in a Django database and manage the tasks using the Django Admin interface.  
Please check here : https://django-celery-beat.readthedocs.io/en/latest/
