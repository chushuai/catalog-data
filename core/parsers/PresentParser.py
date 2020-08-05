import json
import os
import regex as re
from collections import OrderedDict
from enum import Enum
from typing import Iterator, Any, Iterable
from bs4 import BeautifulSoup, Tag, NavigableString
from lxml import html, etree
from lxml.etree import ParseError
from lxml.html import HtmlElement
from core.config.settings import logger, DATA_PATH, TMP_PATH
from core.parsers.BaseParser import BaseParser
from core.parsers.ParserErrors import ParsingSplitError
from core.utils.fileu import FileUtils as Fu


class Regexp(Enum):
    BLANK = re.compile(r"^$", re.IGNORECASE)
    LN = re.compile(r"([\n\s]+)", re.IGNORECASE)
    QT = re.compile(r"(\"[']+)", re.IGNORECASE)
    NSQT = re.compile(r"((?:\s*\"\s*)([^ \"]+)(?:\s*\"\s*))")


class PresentParser(BaseParser):
    def __init__(self):
        self.fn = os.path.join(DATA_PATH, 'in', 'PANDA-Presentations-json.pl.json')

    def process(self):
        logger.info("Start processing Presentations...")
        if Fu.is_valid_file(self.fn):
            fn = self._parse(self.fn)
            if fn and Fu.is_valid_file(fn):
                self._parse(fn)
        logger.info("End.")

    @staticmethod
    def _parse(fn) -> Any:
        result = None
        try:
            venues = []
            presents = []
            with open(fn, "rt", encoding="UTF-8") as inf:
                lines = json.load(inf)
            if lines:
                for line in lines:
                    pvs = PresentParser.build_venues(line)
                    links = PresentParser.build_links_venues(line)
                    present = {
                        "id": line["id"] if "id" in line else "",
                        "name": line["name"] if "name" in line else "",
                        "tags": line["tags"] if "tags" in line else [],
                        "venues": [{"presenter": v["presenter"], "venue": v["venue"], "date": v["date"]} for v in pvs],
                        "links": links
                    }
                    presents.append(present)
                    venues.extend([{"id": v["id"],
                                    "name": v["name"],
                                    "description": v["description"],
                                    "dates": v["dates"],
                                    "tags": v["tags"]} for v in pvs])

            fn = os.path.join(DATA_PATH, "out/media.json")
            Fu.save_as_json(fn, presents)

            fn = os.path.join(DATA_PATH, "out/venues.json")
            Fu.save_as_json(fn, venues)

            result = True
        except ParseError as exc:
            logger.error(exc, exc_info=True)
        return result

    @staticmethod
    def build_links_venues(item: dict) -> list:
        result = []
        try:
            links = item["links"] if "links" in item else []
            for link in links:
                url = link["to"] if "to" in link else ""
                result.append(url)
        except Exception as exc:
            print(exc)
        return result

    @staticmethod
    def build_venues(item: dict) -> list:
        result = []
        try:
            presenters = item['presenters'] if "presenters" in item else None
            if presenters is not None:
                for i, v in enumerate(presenters):
                    venue = v["venue"].strip() if "venue" in v else ""
                    vit = re.sub(r"[\p{Punct}]+", "", venue, flags=re.IGNORECASE)
                    pid = "_".join(re.split(r"(?:[\s]+)", vit)).strip().lower() if "venue" in v else ""
                    name = ", ".join([v.capitalize() for v in re.split(r"(?:[_]+)", v["name"].strip())]) if "name" in v else ""
                    el = {
                        "id": pid,
                        "presenter": "Author: " + name,
                        "name": vit,
                        "venue": pid,
                        "date": v["date"],
                        "description": "",
                        "dates": {
                            "date": v["date"],
                            "url": v["url"],
                        },
                        "tags": []
                    }
                    result.append(el)
        except Exception as exc:
            print(exc)
        return result
