from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from newspaper import Article


def custom_items(cate, soup, tag, class_name):
    items = soup.find_all(tag, attrs=class_name)
    if cate == "remove":
        for item in items:
            item.decompose()
    if cate == "add_dot":
        for item in items:
            item.string = item.text+"."


def get_dantri_article(url, hdr):
    description=""
    contents=""
    soup = BeautifulSoup(urlopen(Request(url, headers=hdr)), "lxml")
    if soup.find('div', class_='dt-news__sapo'):
        description = soup.find('div', class_='dt-news__sapo').find('h2').text
        contents = description
    news_contents = soup.find('div', class_='dt-news__content').find_all(
        lambda tag: tag.name == 'p' and not tag.attrs and not tag.next_element.name == 'strong')
    for item in news_contents:
        contents += " "+item.text
    return contents


def get_vnexpress_article(url, hdr):
    description=""
    contents=""
    soup = BeautifulSoup(urlopen(Request(url, headers=hdr)), "lxml")
    # title = soup.find('h1', class_='title-detail').text
    if soup.find('p', class_='description'):
        description = soup.find('p', class_='description').text
        contents = description
    news_contents = soup.find_all(
        'p', attrs={"class": "Normal", "style": ""})
    for item in news_contents:
        contents += " "+item.text
    return contents


def get_tuoitre_article(url, hdr):
    description=""
    contents=""
    soup = BeautifulSoup(urlopen(Request(url, headers=hdr)), "lxml")
    title = soup.find('h1', class_='article-title').text
    if soup.find('h2', class_='sapo'):
        description = soup.find('h2', class_='sapo').text.replace('TTO - ', '')
        contents = description 
    def get_content(tag):
        return tag.name == 'p' and (not tag.attrs or (tag.attrs == 1 and tag.attrs.values() == [])) and not tag.next_element.name == 'b'
    news_contents = soup.find(
        'div', class_='content fck').find_all(get_content)
    for item in news_contents:
        contents += " "+item.text
    return contents


def get_thanhnien_article(url, hdr):
    description=""
    contents=""
    soup = BeautifulSoup(urlopen(Request(url, headers=hdr)), "lxml")
    title = soup.find('h1', class_='details__headline').text
    if soup.find('div', id='chapeau'):
        description = soup.find('div', id='chapeau').text
        contents = description  
    news_contents = soup.find("div", id="abody")
    custom_items("remove", news_contents, "table", {"class": "imagefull"})
    custom_items("remove", news_contents, "table", {"class": "video"})
    custom_items("add_dot", news_contents, "h2", {"class": ""})
    contents += news_contents.text
    return contents


def get_nhandan_article(url, hdr):
    description=""
    contents=""
    soup = BeautifulSoup(
        urlopen(Request(url, headers=hdr)), "lxml")
    # title = soup.find('h1', class_='box-title-detail').text
    if soup.find('div', class_='box-des-detail'):
        contents = soup.find('div', class_='box-des-detail').find('p').text
        description = contents
    custom_items("add_dot", soup.find(
        "div", class_="detail-content-body"), "strong", {"class": ""})
    news_contents = soup.find(
        "div", class_="detail-content-body").find_all(lambda tag: tag.name == 'p' and not tag.attrs)
    for item in news_contents:
        contents += " "+item.text
    return contents


def get_plo_article(url, hdr):
    description=""
    contents=""
    soup = BeautifulSoup(urlopen(Request(url, headers=hdr)), "lxml")
    title = soup.find('h1', class_='main-title').text
    if soup.find(id='chapeau'):
        contents = (soup.find(id='chapeau').text).replace('(PLO)-', '')
        description = contents
    custom_items("remove", soup.find("div", id="abody"),
                 "article", {"class": "article-related"})
    custom_items("remove", soup.find("div", id="abody"),
                 "p", {"class": "item-photo"})
    news_contents = soup.find("div", id="abody").find_all(
        lambda tag: tag.name == 'p')
    for item in news_contents:
        contents += " "+item.text
    return contents


def get_vietnamnet_article(url, hdr):
    description=""
    contents=""
    soup = BeautifulSoup(urlopen(Request(url, headers=hdr)), "lxml")
    # title = soup.find('h1', class_='title').text
    if soup.find('div', class_="bold ArticleLead"):
        description = soup.find('div', class_="bold ArticleLead").text
    custom_items("remove", soup.find("div", id="ArticleContent"), "table", {
        "class": "FmsArticleBoxStyle"})
    custom_items("remove", soup.find(
        "div", id="ArticleContent"), "strong", {"class": ""})
    custom_items("remove", soup.find("div", id="ArticleContent"), "div", {
        "class": "inner-article"})
    news_contents = soup.find("div", id="ArticleContent").find_all(
        lambda tag: tag.name == 'p')
    for item in news_contents:
        contents += " "+item.text
    return contents


def get_nldo_article(url, hdr):
    description=""
    contents=""
    soup = BeautifulSoup(urlopen(Request(url, headers=hdr)), "lxml")
    # title = soup.find('h1', class_='title-content').text
    if soup.find('h2', class_='sapo-detail'):
        contents = (soup.find('h2',
                              class_='sapo-detail').text).replace("(NLĐO)", "")
        description = contents
    news_contents = soup.find(
        "div", class_="content-news-detail").find_all(lambda tag: tag.name == 'p' and not tag.attrs)
    for item in news_contents:
        contents += " "+item.text
    return contents


def get_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        contents = (
            article.text == "") and article.meta_data['description'] or article.text
        return contents
    except Exception as e:
        print(e)
