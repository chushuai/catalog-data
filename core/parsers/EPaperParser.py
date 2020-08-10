import os
import re
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
    LINE = re.compile(r"^(([\d]+?\|)(.+?))$", re.IGNORECASE)
    ABS = re.compile(r"^(BEGIN-ABSTRACT::)$", re.IGNORECASE)
    ABE = re.compile(r"^([\s\n]*?::END-ABSTRACT)$", re.IGNORECASE)


class EPaperParser(BaseParser):
    def __init__(self):
        self.fn = os.path.join(DATA_PATH, 'in', 'Non-CAIDA Publications using CAIDA Data.html')

    def process(self):
        if Fu.is_valid_file(self.fn):
            fn = self._parse_html(self.fn)
            if fn and Fu.is_valid_file(fn):
                pass

    @staticmethod
    def _parse_html(fn) -> Any:
        result = None
        try:
            lines = []
            with open(fn, "rt", encoding="UTF-8") as inf:
                data = inf.read()
                doc = BeautifulSoup(data, "lxml")
                table = doc.find("table", id="datapubfilter")
                if table:
                    tbody = table.find("tbody")
                    if tbody:
                        trows = tbody.find_all("tr")
                        if trows:
                            for tr in trows:
                                if tr:
                                    tds = tr.find_all("td")
                                    if tds:
                                        el = OrderedDict()
                                        name = tds[2].get_text() if 2 < len(tds) else ""
                                        el["_type"] = "Paper"
                                        el['id'] = "_".join(name.split(" "))
                                        el['name'] = name
                                        el["description"] = tds[3].get_text() if 3 < len(tds) else ""
                                        authors_ = tds[1] if 1 < len(tds) else ""
                                        el['authors'] = EPaperParser._get_authors(authors_)
                                        lines.append(el)

            if lines:
                EPaperParser.save(lines)
        except ParseError as exc:
            logger.error(exc, exc_info=True)
        return result

    @staticmethod
    def _get_authors(tag) -> Iterable:
        result = []
        try:
            for tag in tag.descendants:
                if isinstance(tag, NavigableString):
                    txt = tag.string
                    if txt:
                        txt = re.sub(r"[\s\t]+", "", txt)
                        result.append(txt)
        except ParseError as exc:
            logger.error(exc)
        return result

    @staticmethod
    def _split_authors(row) -> Iterable:
        result = []
        try:
            el = OrderedDict()
            el["_type"] = "Author"
            el["id"] = "Author:"
            el["nameFirst"] = ""
            el["nameLast"] = ""

            for name in row:
                a = re.split(r"(?:,[\s]*)", name)
                id_ = "Author:" + "_".join(a)
                firstname = a[1] if 1 < len(a) else ''
                lastname = a[0] if 0 < len(a) else ''
                el["id"] = id_
                el["nameFirst"] = firstname
                el["nameLast"] = lastname
                result.append(el)

        except Exception as exc:
            logger.error(exc)
        return result

    @staticmethod
    def save(rows):
        result = False
        try:
            if rows:
                fio = os.path.join(TMP_PATH, 'epapers.json')
                Fu.save_as_json(fio, rows)
                if fio and Fu.is_valid_file(fio):
                    logger.info("File {} sucessfully created.".format('epapers.json'))

                authors = []
                for r in rows:
                    astr = r['authors']
                    authors.extend(EPaperParser._split_authors(astr))

                if authors:
                    unic = set()
                    dedup = []
                    for e in authors:
                        key = e['id'].lower()
                        if key in unic:
                            continue
                        dedup.append(e)
                        unic.add(key)

                    fio = os.path.join(TMP_PATH, 'eauthors.json')
                    Fu.save_as_json(fio, dedup)
                    if fio and Fu.is_valid_file(fio):
                        logger.info("File {} sucessfully created.".format('eauthors.json'))
                result = True
        except IOError as exc:
            logger.error(exc, exc_info=True)
        return result
