"""
混合检索模块：BM25 + TF-IDF

BM25 对关键词精确匹配更友好；TF-IDF (char n-gram) 对中文无需分词。
两者归一化后加权融合，取 top-k。
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 混合权重
BM25_WEIGHT = 0.6
TFIDF_WEIGHT = 0.4
DEFAULT_TOP_K = 4


# ── BM25Okapi (纯 numpy 实现，不依赖额外包) ─────────────────
class BM25Okapi:
    """简单 BM25 实现，使用 char bigram 作为 token（中文友好）。"""

    def __init__(self, corpus, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        # char bigram 分词
        self.tokenized = [self._tokenize(doc) for doc in corpus]
        self.doc_len = np.array([len(t) for t in self.tokenized])
        self.avgdl = self.doc_len.mean() if len(self.doc_len) > 0 else 0

        # 构建 term frequency + df
        self.tf = []
        self.df = {}
        for tokens in self.tokenized:
            freq = {}
            for t in tokens:
                freq[t] = freq.get(t, 0) + 1
            self.tf.append(freq)
            for t in freq:
                self.df[t] = self.df.get(t, 0) + 1

        self.N = len(corpus)
        # IDF: log((N - df + 0.5) / (df + 0.5) + 1)
        self.idf = {
            t: np.log((self.N - df + 0.5) / (df + 0.5) + 1)
            for t, df in self.df.items()
        }

    @staticmethod
    def _tokenize(text):
        """char bigram 分词，适配中文（无需分词器）。"""
        text = text.lower().strip()
        if len(text) < 2:
            return [text] if text else []
        return [text[i : i + 2] for i in range(len(text) - 1)]

    def get_scores(self, query):
        """返回 query 与每篇文档的 BM25 分数数组。"""
        q_tokens = self._tokenize(query)
        scores = np.zeros(self.N)
        for i in range(self.N):
            if self.doc_len[i] == 0:
                continue
            score = 0.0
            for qt in q_tokens:
                if qt not in self.idf:
                    continue
                tf_i = self.tf[i].get(qt, 0)
                if tf_i == 0:
                    continue
                idf = self.idf[qt]
                denom = tf_i + self.k1 * (
                    1 - self.b + self.b * self.doc_len[i] / self.avgdl
                )
                score += idf * tf_i * (self.k1 + 1) / denom
            scores[i] = score
        return scores


class HybridRetriever:
    """BM25 + TF-IDF 混合检索器。"""

    def __init__(self, chunks, top_k=DEFAULT_TOP_K):
        self.chunks = chunks
        self.top_k = top_k
        corpus = [c["text"] for c in chunks]

        # BM25
        self.bm25 = BM25Okapi(corpus)

        # TF-IDF (char n-gram, 中文友好)
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(1, 2),
            lowercase=True,
            min_df=1,
        )
        self.matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, question):
        """返回 [(chunk, score), ...] 按 score 降序，最多 top_k 条。"""
        # BM25 分数
        bm25_scores = self.bm25.get_scores(question)
        if bm25_scores.max() > 0:
            bm25_norm = bm25_scores / bm25_scores.max()
        else:
            bm25_norm = bm25_scores

        # TF-IDF 余弦相似度
        q_vec = self.vectorizer.transform([question])
        tfidf_scores = cosine_similarity(q_vec, self.matrix).flatten()
        if tfidf_scores.max() > 0:
            tfidf_norm = tfidf_scores / tfidf_scores.max()
        else:
            tfidf_norm = tfidf_scores

        # 加权融合
        hybrid = BM25_WEIGHT * bm25_norm + TFIDF_WEIGHT * tfidf_norm

        # 取 top_k
        order = np.argsort(hybrid)[::-1]
        results = []
        for idx in order[: self.top_k]:
            if hybrid[idx] <= 0:
                continue
            results.append((self.chunks[idx], float(hybrid[idx])))
        return results
