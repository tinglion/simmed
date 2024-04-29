import os
import re
import sys
import tarfile

import requests

sys.path.append(".")
from utils import file_utils
from utils.logger import logger

DATA_DIR = r"F:/data/ai/med/pubmed"


def run(url="https://ftp.ncbi.nlm.nih.gov/pub/pmc/manuscript/xml/"):
    fn = f"{DATA_DIR}/list.html"
    file_utils.download_file(url, fn)

    with open(fn, "r", encoding="utf8") as fp:
        html_text = fp.read()

        # 使用正则表达式提取所有 URL
        fn_list = re.findall(r'href="(.*?)"', html_text)
        for fn_file in fn_list:
            if fn_file.find(".tar.gz") > 0:
                url_file = f"{url}/{fn_file}"
                fn_dst = f"{DATA_DIR}/{fn_file}"
                logger.info(f"try url={url_file} fn={fn_dst}")

                if not os.path.exists(fn_dst):
                    file_utils.download_file(url_file, fn_dst)
                    logger.info(f"downloaded url={url_file} fn={fn_dst}")

                    # .tar.gz 解压缩
                    if fn_file.find(".tar.gz") > 0:
                        with tarfile.open(fn_dst, "r:gz") as fp_tgz:
                            fp_tgz.extractall(path=DATA_DIR)
                            logger.info(f"tar -xzf fn={fn_dst}")


if __name__ == "__main__":
    run()
