import os
import json
import regex as re
from enum import Enum
from parser import ParserError
from typing import Iterator, Any, Iterable
from core.config.settings import logger, DATA_PATH
from core.parsers.BaseParser import BaseParser
from core.utils.fileu import FileUtils as Fu


class ArticleParser(BaseParser):
    def __init__(self):
        self.fn = os.path.join(DATA_PATH, 'in', 'PANDA-Papers-json.pl.json')

    def process(self):
        logger.info("Start processing Papers...")
        if Fu.is_valid_file(self.fn):
            fn = self._parse(self.fn)
            if fn and Fu.is_valid_file(fn):
                self._parse(fn)
        logger.info("End.")

    @staticmethod
    def _parse(fn) -> Any:
        result = None
        try:
            articles = []
            authors = []
            with open(fn, "rt", encoding="UTF-8") as inf:
                items = json.load(inf)
            if items:
                for item in items:
                    venue = item['venue'].strip() if "venue" in item else ""
                    ven = re.sub(r"[\p{Punct}]+", "", venue, flags=re.IGNORECASE)
                    pid = "_".join(re.split(r"(?:[\s]+)", ven)).lower()
                    auts = ArticleParser.parse_authors(item["authors"] if "authors" in item else [])
                    el = {
                        "id": item["id"] if "id" in item else "",
                        "name": item["name"] if "name" in item else "",
                        "datePublished": item["datePublished"] if "datePublished" in item else "",
                        "description": item["description"] if "description" in item else "",
                        "tags": item["tags"] if "tags" in item else "",
                        "pubdb_id": item["pubdb_id"] if "pubdb_id" in item else "",
                        "venue": pid,
                        "authors": auts,
                        "links": item["links"] if "links" in item else [],
                        "bibtexFields": {
                            "type": item["type"] if "type" in item else "ARTICLE",
                            "booktitle": item["booktitle"] if "booktitle" in item else "",
                            "institution": item["institution"] if "institution" in item else "",
                            "bibtex": item["bibtex"] if "bibtex" in item else "",
                            "journal": item["journal"] if "journal" in item else "",
                            "volume": item["volume"] if "volume" in item else "",
                            "number": item["number"] if "number" in item else "",
                            "pages": item["pages"] if "pages" in item else "",
                            "linkedObjects": item["linkedObjects"] if "linkedObjects" in item else ""
                        }
                    }
                    articles.append(el)
                    authors.extend(auts)

            fn = os.path.join(DATA_PATH, "out/articles.json")
            Fu.save_as_json(fn, articles)

            fn = os.path.join(DATA_PATH, "out/authors.json")
            Fu.save_as_json(fn, authors)

        except ParserError as exc:
            logger.error(exc, exc_info=True)
        return result

    @staticmethod
    def parse_authors(authors) -> list:
        result = []
        try:
            for author in authors:
                el = {
                    "person": author["person"].lower() if "person" in author else "",
                    "organization": author["organization"] if "organization" in author else []
                }
                result.append(el)
        except Exception as exc:
            logger.error(exc)
        return result



