from django.contrib import admin
from .models import Students, Blog, Job, JobLogs, JobStats
from django.urls import reverse
from django.utils.html import format_html

class DjStudentAdmin(admin.ModelAdmin):
   list_display = ("first_name", "last_name", "address", "roll_number", "mobile", "branch")
   list_filter = ("branch",)

class DjBlogAdmin(admin.ModelAdmin):
  list_display = ("title", "release_date", "blog_time", "author", "created_date")
  list_filter = ("author",)


class DjJob(admin.ModelAdmin):
  def run(self, obj):
    return format_html('<a class="button" href="{}">RUN</a>', reverse('scraping', args=(str(obj.pk))))

  def view_stats(self, obj):
    path = "../jobstats/?q={}".format(obj.pk)
    return format_html(f'''<a class="button" href="{path}">stats</a>''')

  run.short_description = 'Run'
  run.allow_tags = True
  view_stats.short_description = 'Stats'
  view_stats.allow_tags = True

  list_display = ("job_name", "start_date", "end_date", "no_of_blogs", "start_no", "created_date", "run", "view_stats")
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


# Register your models here.
admin.site.register(Blog, DjBlogAdmin)
admin.site.register(Students, DjStudentAdmin)
admin.site.register(Job, DjJob)
admin.site.register(JobStats, DjJobStats)
admin.site.register(JobLogs, DjJobLogs)
