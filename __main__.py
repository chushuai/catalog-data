import json
import os
import regex as re
from core.utils.fileu import FileUtils as fu
from core.config.settings import DATA_PATH, TMP_PATH
from core.config.settings import logger
from core.parsers.ArticlePdfParser import ArticlePdfParser
from core.parsers.ArticleParser import ArticleParser
from core.parsers.PresentParser import PresentParser
from core.parsers.PaperParser import PaperParse
from core.parsers.EPaperParser import EPaperParser


class Main:

    @staticmethod
    def joiner():
        try:
            js1 = None
            fpf = os.path.join(TMP_PATH, "papers.json")
            fpef = os.path.join(TMP_PATH, "epapers.json")
            if fu.is_valid_file(fpf) and fu.is_valid_file(fpef):
                with open(fpf) as jp:
                    js1 = json.load(jp)
                    with open(fpef) as jpf:
                        js2 = json.load(jpf)
                        js1.extend(js2)

            if js1:
                fpn = os.path.join(DATA_PATH, "out/articles.json")
                fu.save_as_json(fpn, js1)

            fpf = os.path.join(TMP_PATH, "authors.json")
            fpef = os.path.join(TMP_PATH, "eauthors.json")
            if fu.is_valid_file(fpf) and fu.is_valid_file(fpef):
                with open(fpf) as jp:
                    js1 = json.load(jp)
                    with open(fpef) as jpf:
                        js2 = json.load(jpf)
                        js1.extend(js2)

            if js1:
                fpn = os.path.join(DATA_PATH, "out/authors.json")
                fu.save_as_json(fpn, js1)

        except Exception as exc:
            logger.error(exc)

    @staticmethod
    def splitting():
        logger.info("Start splitting files...")
        try:
            dirname = os.path.join(DATA_PATH, "out")
            files = fu.get_files(dirname, ext=".json")
            for file in files:
                try:
                    finfo = fu.get_file_info(file)
                    name = finfo["name"]
                    jsons = fu.read_file_json(file)
                    if jsons:
                        for item in jsons:
                            try:
                                if name == "authors":
                                    fid = str(item["person"]).replace("person:", "").lower()
                                else:
                                    fid = Main.build_clear_name(str(item["name"]).replace("name:", ""))

                                dest_dir = os.path.join(dirname, name)
                                dest_file = os.path.join(dest_dir, f"{fid}.json")
                                fu.save_as_json(dest_file, item)
                                logger.info(f"Saved: {dest_file}")
                            except Exception as exc:
                                logger.error(exc)

                except Exception as exc:
                    logger.error(exc)
        except Exception as exc:
            logger.error(exc, exc_info=True)
        logger.info("End.")

    @staticmethod
    def build_clear_name(text: str) -> str:
        result = text
        try:
            txt = re.sub(r"[\p{Punct}]+", "", result.strip(), flags=re.IGNORECASE)
            result = "_".join(re.split(r"(?:[\s]+)", txt)).lower()
        except Exception as exc:
            logger.error(exc)
        return result


if "__main__" == __name__:
    logger.info("Start ...")
    ArticleParser().process()
    PresentParser().process()
    Main.splitting()
    logger.info("End.")
