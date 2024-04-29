import json
import os
import re
import string

import ijson
import nltk
from gensim.models import word2vec
from gensim.models.word2vec import LineSentence
from nltk.corpus import stopwords

from utils.logger import logger

stop_words = stopwords.words(r"E:\nltk_data\corpora\stopwords\data\stopwords\english")
stop_words.extend(
    [".", "journal", "meshMajor", "year", "abstractText", "pmid", "title"]
)
stop_words_set = set(stop_words)
punctuation = set(string.punctuation)


MIN_COUNT = 8
CPU_NUM = 10  # 需要预先安装 Cython 以支持并行
VEC_SIZE = 1000
CONTEXT_WINDOW = 5  # 提取目标词上下文距离最长5个词

BATCH_SIZE = 100 * 1000
START_FROM = 0
STOP_SIZE = 0  # 50 * 1000


# 用生成器的方式读取文件里的句子
# 适合读取大容量文件，而不用加载到内存
class MySentences(object):
    def __init__(self, fname):
        self.fname = fname

    def __iter__(self):
        for line in open(self.fname, "r"):
            yield line.split()


# 定义过滤函数
def filter_words(sentence):
    return [
        word
        for word in sentence
        if word.lower() not in stop_words_set and word.lower() not in punctuation
    ]


def run(datafile, modelfile):
    logger.info(f"try to train {datafile}")
    if os.path.exists(modelfile):
        w2v_model = word2vec.Word2Vec.load(modelfile)
    else:
        w2v_model = word2vec.Word2Vec(
            min_count=MIN_COUNT,
            workers=CPU_NUM,
            vector_size=VEC_SIZE,
            window=CONTEXT_WINDOW,
        )
        w2v_model.build_vocab([["medicine", "amaemia", "afatinib", "nilaparib"]])

    # sentences = MySentences(datafile)
    # sentences = list(MySentences(DataDir + f_input))
    # for idx, sentence in enumerate(sentences):
    #     sentence = [w for w in sentence if w not in StopWords]
    #     sentences[idx] = sentence

    # sentences = LineSentence(datafile)

    with open(datafile, "r", encoding="latin-1") as f:
        i = 0
        lines_batch = []
        for line in f:
            i += 1
            if i <= START_FROM:
                continue

            # 分词并过滤 stopwords
            line = line.strip()
            line = re.sub(r",\s*$", "", line)
            try:
                line_json = json.loads(line)

                txt = line_json.get("abstractText", "")
                txt = txt.replace(".", "").replace(",", "")

                words = txt.split()
                filtered_words = filter_words(words)
                lines_batch.append(filtered_words)
                if i % BATCH_SIZE == 0:
                    w2v_model.build_vocab(lines_batch, update=i > BATCH_SIZE)
                    w2v_model.train(lines_batch, total_examples=1, epochs=1)
                    w2v_model.save(modelfile)

                    lines_batch = []
                    logger.info(f"trained {i}")
                    if STOP_SIZE > 0 and i >= STOP_SIZE:
                        break
            except json.decoder.JSONDecodeError as e:
                logger.error(f"{i} {e}")

    # sentences = word2vec.Text8Corpus(abstractText_file)
    # w2v_model = word2vec.Word2Vec.load(ModelDir + model_output)
    # w2v_model = word2vec.Word2Vec(
    #     sentences,
    #     min_count=MIN_COUNT,
    #     workers=CPU_NUM,
    #     vector_size=VEC_SIZE,
    #     window=CONTEXT_WINDOW,
    # )
    w2v_model.save(modelfile)


# 名词、动词、词组、entity
if __name__ == "__main__":
    run("./data/bioCorpus_5000.txt", "./temp/model.bin")
