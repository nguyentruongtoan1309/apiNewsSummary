from crawler.article_content import *
from urllib.parse import urlparse
def get_article(url, hdr):
    if ("https://m." in url):
        url = url.replace("https://m.", "https://")
    url_netloc = urlparse(url).netloc
    try:
        article_dict = {
            'dantri.com.vn': get_dantri_article,
            'vnexpress.net': get_vnexpress_article,
            'tuoitre.vn': get_tuoitre_article,
            'thanhnien.vn': get_thanhnien_article,
            'nhandan.com.vn':get_nhandan_article,
            'plo.vn':get_plo_article,
            'nldo.com.vn':get_nldo_article,
            'vietnamnet.vn': get_vietnamnet_article
        }
        return article_dict[url_netloc](url, hdr)
    except Exception as e:
        print(e)
        return get_content(url)