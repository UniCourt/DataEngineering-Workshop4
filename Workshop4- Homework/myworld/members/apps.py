from django.apps import AppConfig
import psycopg2
import requests
import re
from bs4 import BeautifulSoup, element
import datetime
from dateutil.parser import parse


db_name = 'member_db'
db_user = 'postgres'
db_pass = '123456'
db_host = 'psql-db'
db_port = '5432'

conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_pass, host=db_host, port=db_port)

def add_row_to_blog(title, author, date, time):
    sql = """INSERT INTO members_blog (title, release_date, blog_time, author, created_date) VALUES (%s, %s::DATE, %s::TIME, %s, NOW())"""

    with conn:
        with conn.cursor() as curs:
            time=time.replace('\u202f',"")
            curs.execute(sql, (title, date, time, author))

def truncate_table():
    print("Truncating contents all the tables")
    with conn:
        with conn.cursor() as curs:
            curs.execute("TRUNCATE members_blog CASCADE;")

def start_extraction(start_date=None, end_date=None):
    print("Extraction started")
    url = "https://blog.python.org/"
  
    data = requests.get(url)
    page_soup = BeautifulSoup(data.text, 'html.parser')
    
    if start_date:
        start_date = parse(start_date)
    if end_date:
        end_date = parse(end_date)
    
    blogs = page_soup.select('div.date-outer')
    truncate_table()
    for blog in blogs:
        date = blog.select('.date-header span')[0].get_text()
    
        converted_date = parse(date)
    
        if start_date and converted_date < start_date:
            continue
        if end_date and converted_date > end_date:
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
    
        add_row_to_blog(title, author, date, time)
    
        print("\nTitle:", title.strip('\n'))
        print("Date:", date, )
        print("Time:", time)
        print("Author:", author)
    
        # print("Number of blogs read:", count)
        print(
            "\n---------------------------------------------------------------------------------------------------------------\n")

if __name__ == "__main__":
    start_extraction()
    

class MembersConfig(AppConfig):
    default_auto_field='django.db.models.BigAutoField'
    name = 'members'

