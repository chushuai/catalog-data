import multiprocessing
import os
import re
import requests
import pdfplumber
from enum import Enum
from io import BytesIO
from core.config.settings import DATA_PATH
from core.parsers.BaseParser import BaseParser
from core.utils.fileu import FileUtils as Fu
from concurrent.futures import ProcessPoolExecutor, as_completed


class Regexp(Enum):
    BLANK = re.compile(r"^$", re.IGNORECASE)
    LN = re.compile(r"([\n\s]+)", re.IGNORECASE)


class ArticlePdfParser(BaseParser):
    def __init__(self):
        self.fna = os.path.join(DATA_PATH, 'out', 'articles.json')
        self.fns = os.path.join(DATA_PATH, 'in', 'Softwares.json')
        self.dns = os.path.join(DATA_PATH, 'in', 'Datasets.json')

    def process(self):
        if Fu.is_valid_file(self.fna) and Fu.is_valid_file(self.fns):
            self.process_articles()

    @staticmethod
    def process_art(art, aliases):
        def get_pdf_from_resourse(url, softs) -> set:
            result = set()
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    with pdfplumber.load(BytesIO(r.content)) as pdf:
                        for soft in set(softs):
                            page_idx = -1
                            for page in pdf.pages:
                                page_idx += 1
                                text = page.extract_text()
                                if "references" in text.lower():
                                    break
                            if page_idx >= 0:
                                for page in pdf.pages[page_idx:]:
                                    text = page.extract_text()
                                    if soft[0].lower() in text.lower():
                                        result.add((url, soft))
                                        break
            except Exception as exc:
                print(exc)
            return result

        urls = []
        links = art["links"] if "links" in art else []
        for link in links:
            link_to = {"to": "", "lable": link}
            url = link if link.endswith(".pdf") else None
            if url is not None:
                names = get_pdf_from_resourse(url, aliases)
                for name in names:
                    el = {
                        "lable": "used",
                        "to": f"{name[1][1]}:{name[1][0]}"
                    }
                    urls.append(el)
            else:
                urls.append(link_to)
        art["links"] = urls
        return art

    def process_articles(self):
        result = []
        try:
            datasets = ArticlePdfParser._parse_datasets(self.dns)
            softwares = ArticlePdfParser._parse_softwares(self.fns)
            aliases = datasets + softwares
            arts = Fu.read_file_json(self.fna)

            futures = []
            with ProcessPoolExecutor(max_workers=6) as executor:
                for art in arts:
                    futures.append(executor.submit(self.process_art, art, aliases))

                for f in as_completed(futures):
                    result.append(f.result())

            fn = os.path.join(DATA_PATH, "out/publications.json")
            Fu.save_as_json(fn, result)

        except Exception as exc:
            print(exc)

    @staticmethod
    def get_pdf_from_resourse(url, softs) -> set:
        result = set()
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with pdfplumber.load(BytesIO(r.content)) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        for soft in softs:
                            if soft and text and soft.lower() in text.lower():
                                result.add((url, soft))
        except Exception as exc:
            print(exc)
        return result

    @staticmethod
    def _parse_datasets(fns) -> list:
        result = []
        try:
            js = Fu.read_file_json(fns)
            if js:
                for line in js:
                    name = line["name"] if "name" in line else None
                    if name:
                        result.append((name.strip(), "Dataset"))
        except Exception as exc:
            print(exc)
        return result

    @staticmethod
    def _parse_softwares(fns) -> list:
        result = []
        try:
            js = Fu.read_file_json(fns)
            if js:
                for line in js:
                    name = line["name"] if "name" in line else None
                    if name:
                        result.append((name.strip(), "Software"))
        except Exception as exc:
            print(exc)
        return result
