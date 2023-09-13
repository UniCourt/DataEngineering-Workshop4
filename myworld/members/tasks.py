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
