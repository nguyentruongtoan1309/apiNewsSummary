from newspaper import Article
import numpy as np
import nltk
import networkx as nx
import heapq
import regex
from pyvi import ViTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import spacy

def read_vi_stopwords(file_name):
    stop_words = []
    stop_words = [stopword.rstrip('\n')
                  for stopword in open(file_name, encoding="utf_8")]
    return stop_words

def execute_text_rank(content, senNum):
    # nltk.download("punkt")  # one time execution
    contents_parsed = content.replace('\n', ' ').replace('\r', '')
    contents_parsed = " ".join(regex.split(
        "\s+", contents_parsed, flags=regex.UNICODE))
    origin_text = regex.split(
        r'(?<!\w\.\w.)(?<![A-Z][a-z])(?<=\.|\?|\;|\!)\s(?![a-z])', contents_parsed)
    # Xóa 1 câu nếu câu tương đồng với 1 câu khác trong content
    nlp = spacy.load('vi_spacy_model')
    # i = 0
    # while i < len(origin_text):
    #     doc1 = nlp(origin_text[i])
    #     j = i+1
    #     while j < len(origin_text):
    #         doc2 = nlp(origin_text[j])
    #         if (doc1.similarity(doc2) > 0.75):
    #             origin_text.pop(j)
    #         j += 1
    #     i += 1
    i=0
    while i < len(origin_text):
        if origin_text[i]!="":
            doc1=nlp(origin_text[i])
            j=i+1
            while j < len(origin_text):
                if origin_text[j]!="":
                    doc2=nlp(origin_text[j])
                    if (doc1.similarity(doc2)>0.75):
                        origin_text[j]=""
                j+=1
        i+=1
    origin_sentences = []
    for sen in origin_text:
        senLower = sen.lower()  # Biến đổi hết thành chữ thường
        origin_sentences.append(senLower)

    if int(senNum) >= len(origin_text):
        senNum = len(origin_text)

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