import pymysql
from app import app
from text_rank import execute_text_rank
from crawler.content_getter import get_article
from db_config import mysql
from flask import jsonify
from flask import flash, request
from newspaper import Article
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import schedule
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


# def custom_items(cate, soup, tag, class_name):
#     items = soup.find_all(tag, attrs=class_name)
#     if cate == "remove":
#         for item in items:
#             item.decompose()
#     if cate == "add_dot":
#         for item in items:
#             item.string = item.text+"."


# def getContents(urlArticle):
#     if ("https://m." in urlArticle):
#         urlArticle = urlArticle.replace("https://m.", "https://")
#     try:
#         contents = ""
#         description = ""
#         hdr = {'User-Agent': 'Mozilla/5.0'}
#         if ("https://dantri.com.vn/" in urlArticle):
#             soup = BeautifulSoup(
#                 urlopen(Request(urlArticle, headers=hdr)), "lxml")
#             if soup.find('div', class_='dt-news__sapo'):
#                 description = soup.find(
#                     'div', class_='dt-news__sapo').find('h2').text
#                 contents += description
#             news_contents = soup.find('div', class_='dt-news__content').find_all(
#                 lambda tag: tag.name == 'p' and not tag.attrs and not tag.next_element.name == 'strong')
#             for item in news_contents:
#                 contents += " "+item.text
#             return contents
#         elif ("https://vnexpress.net/" in urlArticle):
#             soup = BeautifulSoup(
#                 urlopen(Request(urlArticle, headers=hdr)), "lxml")
#             title = soup.find('h1', class_='title-detail').text
#             if soup.find('p', class_='description'):
#                 description = soup.find('p', class_='description').text
#                 contents += description
#             news_contents = soup.find_all(
#                 'p', attrs={"class": "Normal", "style": ""})
#             for item in news_contents:
#                 contents += " "+item.text
#             return contents
#         elif ("https://tuoitre.vn/" in urlArticle):
#             soup = BeautifulSoup(
#                 urlopen(Request(urlArticle, headers=hdr)), "lxml")
#             title = soup.find('h1', class_='article-title').text
#             if soup.find('h2', class_='sapo'):
#                 contents += soup.find('h2', class_='sapo').text
#                 contents = contents.replace('TTO - ', '')
#                 description += contents

#             def get_content(tag):
#                 return tag.name == 'p' and (not tag.attrs or (tag.attrs == 1 and tag.attrs.values() == [])) and not tag.next_element.name == 'b'
#             news_contents = soup.find(
#                 'div', class_='content fck').find_all(get_content)
#             for item in news_contents:
#                 contents += " "+item.text
#             return contents
#         elif ("https://thanhnien.vn/" in urlArticle):
#             soup = BeautifulSoup(
#                 urlopen(Request(urlArticle, headers=hdr)), "lxml")
#             title = soup.find('h1', class_='details__headline').text
#             if soup.find('div', id='chapeau'):
#                 contents += soup.find('div', id='chapeau').text
#                 description += contents
#             news_contents = soup.find("div", id="abody")
#             custom_items("remove", news_contents,
#                          "table", {"class": "imagefull"})
#             custom_items("remove", news_contents, "table", {"class": "video"})
#             custom_items("add_dot", news_contents, "h2", {"class": ""})
#             contents += news_contents.text
#             return contents
#         elif ("https://nhandan.com.vn/" in urlArticle):
#             soup = BeautifulSoup(
#                 urlopen(Request(urlArticle, headers=hdr)), "lxml")
#             title = soup.find('h1', class_='box-title-detail').text
#             if soup.find('div', class_='box-des-detail'):
#                 contents += soup.find('div',
#                                       class_='box-des-detail').find('p').text
#                 description += contents
#             custom_items("add_dot", soup.find(
#                 "div", class_="detail-content-body"), "strong", {"class": ""})
#             news_contents = soup.find(
#                 "div", class_="detail-content-body").find_all(lambda tag: tag.name == 'p' and not tag.attrs)
#             for item in news_contents:
#                 contents += " "+item.text
#             return contents
#         elif ("https://plo.vn/" in urlArticle):
#             soup = BeautifulSoup(
#                 urlopen(Request(urlArticle, headers=hdr)), "lxml")
#             title = soup.find('h1', class_='main-title').text
#             if soup.find(id='chapeau'):
#                 contents += (soup.find(id='chapeau').text).replace('(PLO)-', '')
#                 description += contents
#             custom_items("remove", soup.find("div", id="abody"),
#                          "article", {"class": "article-related"})
#             custom_items("remove", soup.find("div", id="abody"),
#                          "p", {"class": "item-photo"})
#             news_contents = soup.find("div", id="abody").find_all(
#                 lambda tag: tag.name == 'p')
#             for item in news_contents:
#                 contents += " "+item.text
#             return contents
#         elif ("https://vietnamnet.vn/" in urlArticle):
#             soup = BeautifulSoup(
#                 urlopen(Request(urlArticle, headers=hdr)), "lxml")
#             title = soup.find('h1', class_='title').text
#             if soup.find('div', class_="bold ArticleLead"):
#                 description += soup.find('div', class_="bold ArticleLead").text
#             custom_items("remove", soup.find("div", id="ArticleContent"), "table", {
#                          "class": "FmsArticleBoxStyle"})
#             custom_items("remove", soup.find(
#                 "div", id="ArticleContent"), "strong", {"class": ""})
#             custom_items("remove", soup.find("div", id="ArticleContent"), "div", {
#                          "class": "inner-article"})
#             news_contents = soup.find("div", id="ArticleContent").find_all(
#                 lambda tag: tag.name == 'p')
#             for item in news_contents:
#                 contents += " "+item.text
#             return contents
#         elif ("https://nld.com.vn/" in urlArticle):
#             soup = BeautifulSoup(
#                 urlopen(Request(urlArticle, headers=hdr)), "lxml")
#             title = soup.find('h1', class_='title-content').text
#             if soup.find('h2', class_='sapo-detail'):
#                 contents += (soup.find('h2',
#                              class_='sapo-detail').text).replace("(NLĐO)", "")
#                 description += contents
#             news_contents = soup.find(
#                 "div", class_="content-news-detail").find_all(lambda tag: tag.name == 'p' and not tag.attrs)
#             for item in news_contents:
#                 contents += " "+item.text
#             return contents
#         else:
#             article = Article(urlArticle)
#             article.download()
#             article.parse()
#             contents = (
#                 article.text == "") and article.meta_data['description'] or article.text
#             return contents
#     except:
#         print("Can't download from url!")
#         return ""


def create_article_summary(id):
    with app.app_context():
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                '''SELECT um.url FROM you_news.UrlMeta um
                WHERE um.id=%s;''', id)
            row = cursor.fetchone()
            # content = getContents(row['url'])
            article = Article(row['url'])
            article.download()
            article.parse()
            content = (article.text ==
                       "") and article.meta_data['description'] or article.text
            summary = execute_text_rank(content, 2)
            row = (summary == ' ') and {
                'summary': article.meta_data['description']} or {'summary': summary}
            resp = jsonify(row)
            print("1")
            resp.status_code = 200
            return resp
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()


@app.route('/')
def article_group():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''SELECT * FROM you_news.articlegroup
        order by processorCounterId desc LIMIT 0,5;''')
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/articlegroup/<int:id>&<int:guid>')
def get_all_url_of_an_article_group(id, guid):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''SELECT ag.id 'groupId', ag.`rank` 'groupRank', agu.`rank` 'articleRank', um.*
            FROM you_news.ArticleGroupUrl agu
            inner join ArticleGroup ag on (agu.guid = ag.guid)
            inner join UrlMeta um on (agu.url = um.url)
            where um.image <> '' and ag.id = %s  or ag.guid = %s
            order by agu.processorCounterId desc, ag.`rank`, agu.`rank`
            limit 0, 20;''', (id, guid))
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/article/<int:id>')
def create_article_summary(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''SELECT um.url FROM you_news.UrlMeta um
            WHERE um.id=%s;''', id)
        row = cursor.fetchone()
        # content = getContents(row['url'])
        article = Article(row['url'])
        article.download()
        article.parse()
        content = (article.text ==
                   "") and article.meta_data['description'] or article.text
        summary = execute_text_rank(content, 2)
        row = (summary == ' ') and {
            'summary': article.meta_data['description']} or {'summary': summary}
        resp = jsonify(row)
        print("1")
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/articlegroup/<int:id>')
def create_article_group_summary(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''SELECT ag.id 'groupId', ag.`rank` 'groupRank', agu.`rank` 'articleRank', um.*
            FROM you_news.ArticleGroupUrl agu
            inner join ArticleGroup ag on (agu.guid = ag.guid)
            inner join UrlMeta um on (agu.url = um.url)
            where um.image <> '' and ag.id = %s
            order by agu.processorCounterId desc, ag.`rank`, agu.`rank`
            limit 0, 5;''', id)
        rows = cursor.fetchall()
        content = ''
        for urlAg in rows:
            content += " "+get_article(urlAg['url'], '')
        summary = execute_text_rank(content, 5)
        print(summary)
        print(content)
        rows = {'summary': content}
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def update_database():
    print(datetime.datetime.now())
    with app.app_context():
        try:
            hdr = {'User-Agent': 'Mozilla/5.0'}
            sql = "INSERT INTO you_news.articlegroupsummary(agId, articleId, createdAt, summaryContent, title, image) VALUES(%s, %s, %s, %s, %s, %s)"
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('''SELECT * FROM you_news.articlegroup
            order by processorCounterId desc, articlegroup.`rank` LIMIT 0,5;''')
            rows = cursor.fetchall()
            for row in rows:
                cursor.execute(
                    '''SELECT ag.id 'groupId', ag.`rank` 'groupRank', agu.`rank` 'articleRank', um.*
                FROM you_news.ArticleGroupUrl agu
                inner join ArticleGroup ag on (agu.guid = ag.guid)
                inner join UrlMeta um on (agu.url = um.url)
                where um.image <> '' and ag.id = %s
                order by agu.processorCounterId desc, ag.`rank`, agu.`rank`
                limit 0, 3;''', row['id'])
                data = cursor.fetchall()
                for item in data:
                    image = item['image']
                    content = get_article(item['url'], hdr)
                    summary = execute_text_rank(content, 3)
                    values = (row['id'], item['id'], datetime.datetime.now(),
                              summary, row['title'], image)
                    try:
                        cursor.execute(sql, values)
                        conn.commit()
                        print("====")
                    except Exception as e:
                        print(e)
            return True, None
        except Exception as e:
            print(e)
            return False, e
        finally:
            print("Success")
            cursor.close()
            conn.close()


@app.route('/tonghop', methods=['GET', 'POST'])
def add_article_group_summary():
    with app.app_context():
        status, err = update_database()
        if status:
            resp = jsonify("Update success")
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(str(err))
            resp.status_code = 400
            return resp


sched = BackgroundScheduler()
sched.add_job(update_database, 'cron', minute="*/5")
sched.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


def main():
    if __name__ == '__main__':
        app.run()


main()
