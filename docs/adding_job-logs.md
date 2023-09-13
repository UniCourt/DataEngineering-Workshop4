## Adding Job , Job stats and Job logs
We need following models to run and track asynchronous task.

- Job : Job is nothing but task which contains meta information required to run task.
- Job stats : This contains stats for each job runs.
- Job Logs : This contains logs which helps us to track asynchronous task. 

### Step 1 : Creating the required models
- Edit the file to create the required modles

```python
class Job(models.Model):
    job_name = models.CharField(max_length=500)
    start_date = models.DateTimeField('Blog start date', null=True)
    end_date = models.DateTimeField('Blog end date', null=True)
    start_no = models.IntegerField(verbose_name="No of blogs to skip", null=True)
    no_of_blogs = models.IntegerField(verbose_name="No of blogs to extract", null=True)
    created_date = models.DateTimeField('Job created date', auto_now_add=True, null=True)

    def __str__(self):
        return self.job_name


class JobStats(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    total_blogs = models.IntegerField(verbose_name="Total blogs found", null=True)
    no_of_blogs_extracted = models.IntegerField(verbose_name='No of blogs extracted', null=True)
    start_date = models.DateTimeField('Extraction start date', null=True)
    end_date = models.DateTimeField('Extraction start date', null=True)

    def __str__(self):
        return self.job


class JobLogs(models.Model):
    job_stats = models.ForeignKey(JobStats, on_delete=models.CASCADE)
    log = models.TextField(verbose_name="job logs")
    function_name = models.TextField(verbose_name="Function name")
    date = models.DateTimeField('Log date', null=True, auto_now_add=True)
```
### Step 2 : Add models in admin.py

To display models in front we need to register models in admin.py

  ```shell
  from .models import Students, Blog, Job, JobLogs, JobStats
  from django.urls import reverse
  from django.utils.html import format_html
    
  class DjJob(admin.ModelAdmin):
     
    def view_stats(self, obj):
      path = "../jobstats/?q={}".format(obj.pk)
      return format_html(f'''<a class="button" href="{path}">stats</a>''')
  
    view_stats.short_description = 'Stats'
    view_stats.allow_tags = True
  
    list_display = ("job_name", "start_date", "end_date", "no_of_blogs", "start_no", "created_date", "view_stats")
    list_filter = ("job_name", "start_date")
    readonly_fields = ("created_date",)
  
  class DjJobStats(admin.ModelAdmin):
    def view_logs(self, obj):
      path = "../joblogs/?q={}".format(obj.pk)
      return format_html(f'''<a class="button" href="{path}">Logs</a>''')
  
    view_logs.short_description = 'Stats'
    view_logs.allow_tags = True
    list_display = ("job", "status", "view_logs", "total_blogs", "no_of_blogs_extracted", "start_date", "end_date")
    search_fields = ('job__pk',)
  
  class DjJobLogs(admin.ModelAdmin):
    list_display = ("date", "log", "function_name")
    search_fields = ('job_stats__pk',)
  
  
  admin.site.register(Job, DjJob)
  admin.site.register(JobStats, DjJobStats)
  admin.site.register(JobLogs, DjJobLogs)
  ```

### Step 3: Create tables for above models

- Exec into webapp container
  
    ```shell
    docker exec -it workshop_web_container sh
    ```
    
- Run makemigrations

    ```shell
    python manage.py makemigrations
    ```

- Run migrate

    ```shell
    python manage.py migrate
    ```

#### Note : Please verify models in front end by running webapp `http://0.0.0.0:8000/admin/`
