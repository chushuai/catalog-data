import os
import re
from collections import OrderedDict
from enum import Enum
from typing import Iterator
from bs4 import BeautifulSoup, Tag
from lxml import html, etree
from lxml.etree import ParseError
from lxml.html import HtmlElement
from core.config.settings import logger, DATA_PATH, TMP_PATH
from core.parsers.BaseParser import BaseParser
from core.parsers.ParserErrors import ParsingError, SplitError
from core.utils.fileu import FileUtils as Fu


class Regexp(Enum):
    BLANK = re.compile(r"^$", re.IGNORECASE)
    LINE = re.compile(r"^(([\d]+?\|)(.+?))$", re.IGNORECASE)
    ABS = re.compile(r"^(BEGIN-ABSTRACT::)$", re.IGNORECASE)
    ABE = re.compile(r"^([\s\n]*?::END-ABSTRACT)$", re.IGNORECASE)


class States(Enum):
    WAIT = 0
    CAPTURE = 1


class PaperParse(BaseParser):
    def __init__(self):
        self.fn = os.path.join(DATA_PATH, 'in', 'Papers Listing Dump - PublicationsDB.html')

    def process(self):
        try:
            if Fu.is_valid_file(self.fn):
                fn = self._parse_html(self.fn)
                if fn and Fu.is_valid_file(fn):
                    rows = self._parse(fn)
                    PaperParse.save(rows)

        except Exception as exc:
            logger.error(exc, exc_info=True)

    @staticmethod
    def _parse_html(fn):
        result = None
        try:
            lines = []
            with open(fn, "rt", encoding="UTF-8") as inf:
                data = inf.read()
                doc = BeautifulSoup(data, "lxml")
                content = doc.find("div", id="content")
                for nbs in content.strings:
                    ln = str(nbs)
                    ln = re.sub(r'[\n\f]+', '\n', ln)
                    ln = re.sub(r'[\s]+', " ", ln)
                    idc = ln.find("BEGIN-ABSTRACT::", re.IGNORECASE)
                    if idc > 0:
                        ln = ln[0:idc] + "\n" + ln[idc:]
                    lines.append(ln)

            if lines:
                finfo = Fu.get_file_info(fn)
                dfo = os.path.join(TMP_PATH, finfo.get("name")+".txt")
                with open(dfo, "wt") as of:
                    for line in lines:
                        of.write(line)
                        of.write("\n")
                result = dfo
        except ParseError as exc:
            logger.error(exc, exc_info=True)
        return result

    @staticmethod
    def _parse(fn):
        rows = []
        try:
            with open(fn, "rt") as fri:
                el = PaperParse._reset_element()
                it = iter(fri)
                while True:
                    try:
                        ln = next(it)
                        ln = ln.strip()
                        try:
                            if ln and Regexp.BLANK.value.match(ln):
                                next(it)

                            elif ln and Regexp.LINE.value.match(ln):
                                PaperParse._extract_other(ln, el)

                            elif ln and Regexp.ABS.value.match(ln):
                                PaperParse._extract_abstract(it, el)
                                rows.append(el)
                                el = PaperParse._reset_element()
                            else:
                                continue

                        except ParsingError as exc:
                            logger.error(exc)

                    except StopIteration as e:
                        break
        except IOError as exc:
            logger.error(exc, exc_info=True)

        return rows

    @staticmethod
    def _extract_abstract(it: Iterator, el: dict):
        result = ""
        try:
            while True:
                ln = next(it)
                ln = ln.strip()
                if Regexp.ABE.value.match(ln) or Regexp.LINE.value.match(ln):
                    break
                else:
                    result += ln
            el["description"] = result
        except StopIteration:
            pass

    @staticmethod
    def _extract_other(ln, el: dict):
        result = None
        try:
            cols = re.split(r"(?:\|+)", ln)
            if cols:
                url = cols[4] if 4 < len(cols) else ""
                el['links'].append(url)

                name = cols[3] if 3 < len(cols) else ""
                el["name"] = name

                tags_ = cols[7] if 7 < len(cols) else ""
                tags = PaperParse._get_tags(tags_)
                el['tags'] = tags

                authors_ = cols[2] if 2 < len(cols) else ""
                authors = PaperParse._get_authors(authors_)
                el['authors'] = authors

                el['id'] = "_".join(name.split(" "))

        except ParsingError as exc:
            logger.error(exc)
        return result

    @staticmethod
    def _get_tags(tags):
        result = []
        try:
            tags_ = re.split("(?:[/]+)", tags)
            for t in tags_:
                et = t.strip()
                if et:
                    result.append(et)
        except SplitError as e:
            pass
        return result

    @staticmethod
    def _get_authors(tags):
        result = []
        try:
            tags_ = re.split("(?:[/]+)", tags)
            for t in tags_:
                et = t.strip()
                if et:
                    result.append(et)
        except SplitError as e:
            pass
        return result

    @staticmethod
    def _reset_element():
        result = OrderedDict()
        result["_type"] = "Paper"
        result["id"] = ""
        result["name"] = ""
        result["description"] = ""
        result["tags"] = []
        result["authors"] = []
        result["links"] = []
        return result

    @staticmethod
    def _split_authors(row):
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

        except ParsingError as exc:
            logger.error(exc)
        return result

    @staticmethod
    def save(rows):
        try:
            if rows:
                fio = os.path.join(TMP_PATH, 'papers.json')
                Fu.save_as_json(fio, rows)
                if fio and Fu.is_valid_file(fio):
                    logger.info("File {} sucessfully created.".format('papers.json'))

                authors = []
                for r in rows:
                    astr = r['authors']
                    authors.extend(PaperParse._split_authors(astr))

                if authors:
                    unic = set()
                    dedup = []
                    for e in authors:
                        key = e['id'].lower()
                        if key in unic:
                            continue
                        dedup.append(e)
                        unic.add(key)

                    fio = os.path.join(TMP_PATH, 'authors.json')
                    Fu.save_as_json(fio, dedup)
                    if fio and Fu.is_valid_file(fio):
                        logger.info("File {} sucessfully created.".format('authors.json'))

        except IOError as exc:
            logger.error(exc, exc_info=True)
