from gensim.models import word2vec

from utils.logger import logger

logger.info(f"test start")
w2v_model = word2vec.Word2Vec.load("./temp/model_300_5.bin")
logger.info(f"model loaded")

logger.info(w2v_model.wv.most_similar("color"))
logger.info(w2v_model.wv.most_similar("anemia"))

sim = w2v_model.wv.similarity("anaemia", "anemia")
logger.info(f"{sim}")
sim = w2v_model.wv.similarity("afatinib", "alectinib")
logger.info(f"{sim}")
