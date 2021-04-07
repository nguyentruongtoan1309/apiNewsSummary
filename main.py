from threading import Thread
import pymysql
from app import app
from db_config import mysql
from flask import jsonify
from flask import flash, request
from newspaper import Article
import numpy as np
import asyncio
import nltk
import networkx as nx
import heapq
import regex
from pyvi import ViTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import threading
import spacy
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import schedule


def get_current_time():
    cdate = datetime.datetime.now()
    # c_time = datetime.time(datetime.now())
    return cdate


def read_vi_stopwords(file_name):
    stop_words = []
    stop_words = [stopword.rstrip('\n')
                  for stopword in open(file_name, encoding="utf_8")]
    return stop_words


def getContents(urlArticle):
    try:
        article = Article(urlArticle)
        article.download()
        article.parse()
        content = (article.text ==
                   "") and article.meta_data['description'] or article.text
        return content
    except:
        print("Can't download from url!")
        return ""


def textRank(content, senNum):
    # nltk.download("punkt")  # one time execution
    contents_parsed = content.replace('\n', ' ').replace('\r', '')
    contents_parsed = " ".join(regex.split(
        "\s+", contents_parsed, flags=regex.UNICODE))
    origin_text = regex.split(
        r'(?<!\w\.\w.)(?<![A-Z][a-z])(?<=\.|\?|\;|\!)\s(?![a-z])', contents_parsed)
    # Xóa 1 câu nếu câu tương đồng với 1 câu khác trong content
    nlp = spacy.load('vi_spacy_model')
    i = 0
    while i < len(origin_text):
        doc1 = nlp(origin_text[i])
        j = i+1
        while j < len(origin_text):
            doc2 = nlp(origin_text[j])
            if (doc1.similarity(doc2) > 0.75):
                origin_text.pop(j)
            j += 1
        i += 1
    origin_sentences = []
    for sen in origin_text:
        senLower = sen.lower()  # Biến đổi hết thành chữ thường
        origin_sentences.append(senLower)

    if int(senNum) >= len(origin_text):
        senNum = str(len(origin_text) - 1)

    sentence_tokenized = []
    for sentence in origin_sentences:
        sent_tokenized = ViTokenizer.tokenize(sentence)
        sentence_tokenized.append(sent_tokenized)

    stop_words = read_vi_stopwords("vietnamese-stopwords-dash.txt")

    def remove_stopwords(sen):
        sen_new = " ".join([i for i in sen if i not in stop_words])
        return sen_new

    sentences_without_sw = [remove_stopwords(
        r.split()) for r in sentence_tokenized]
    sentences_without_sw = list(dict.fromkeys(sentences_without_sw))
    word_embeddings = {}
    f = open("vi.txt", encoding="utf_8", errors="ignore")
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype="float32")
        word_embeddings[word] = coefs
    f.close()
    sentence_vectors = []
    for i in sentences_without_sw:
        if len(i) != 0:
            v = sum([word_embeddings.get(w, np.zeros((100,))) for w in i.split()]) / (
                len(i.split()) + 0.001
            )
        else:
            v = np.zeros((100,))
        sentence_vectors.append(v)
    # similarity matrix
    sim_mat = np.zeros(
        [len(sentences_without_sw), len(sentences_without_sw)])
    # khởi tạo ma trận với điểm số tương tự cosine.
    for i in range(len(sentences_without_sw)):
        for j in range(len(sentences_without_sw)):
            if i != j:
                sim_mat[i][j] = cosine_similarity(
                    sentence_vectors[i].reshape(1, 100),
                    sentence_vectors[j].reshape(1, 100),
                )[0, 0]
    # chuyển đổi ma trận tương tự sim_mat thành một đồ thị
    nx_graph = nx.from_numpy_array(sim_mat)
    # áp dụng thuật toán Xếp hạng trang để xếp hạng câu
    scores = nx.pagerank(nx_graph)
    top_sentences = heapq.nlargest(int(senNum), scores, key=scores.get)
    summary = ""
    top_sentences.sort()
    for i in top_sentences:
        summary += " " + origin_text[i]
    return summary


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
            summary = textRank(content, 2)
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
        summary = textRank(content, 2)
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
            content += " "+getContents(urlAg['url'])
        summary = textRank(content, 5)
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
    print(get_current_time())
    with app.app_context():
        try:
            sql = "INSERT INTO you_news.articlegroupsummary(agId, createdAt, summaryContent, title, image) VALUES(%s, %s, %s, %s, %s)"
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
                limit 0, 5;''', row['id'])
                data = cursor.fetchall()
                image = ''
                content = ''
                for item in data:
                    if(image == ''):
                        image += item['image']
                    content += " " + getContents(item['url'])
                summary = textRank(content, 5)
                print('==============')
                values = (row['id'], datetime.datetime.now(),
                          summary, row['title'], image)
                try:
                    cursor.execute(sql, values)
                    conn.commit()
                except Exception as e:
                    print(e)
            return True, None
        except Exception as e:
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


def test():
    print("o")

# def Schedule():
#     schedule.every(5).seconds.do(update_database)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)


sched = BackgroundScheduler()
sched.add_job(update_database, 'cron', minute="*/1")
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

# t2 = threading.Thread(target=main)
# t2.start()
# t2.join()
