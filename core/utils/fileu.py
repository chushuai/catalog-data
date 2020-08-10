# Global specific utils
import csv
import json
import logging
import os
from pathlib import Path
from typing import Dict, Iterable, Iterator

from core.config.settings import LOG_PATH


def getlogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    lfn = os.path.join(LOG_PATH, __name__)
    ch = logging.FileHandler(lfn)
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


logger = getlogger()


class FileUtils(object):

    @staticmethod
    def get_file_info(path: str) -> Dict:
        result = {"path": path, "parent": "", "base": "", "name": "", "ext": "",
                  "parts": list(), "parents": list(), "suffixes": list()}
        if FileUtils.is_valid_file(path):
            result["path"] = str(Path(path).absolute())
            result["parent"] = str(Path(path).parent)
            result["base"] = Path(path).name
            result["name"] = Path(path).stem
            result["ext"] = Path(path).suffix
            result["parts"] = list(Path(path).parts)
            result["parents"] = [str(ps) for ps in Path(path).parents]
            result['suffixes'] = [suf.strip(".") for suf in Path(path).suffixes]
        return result

    @staticmethod
    def is_valid_dir(source: str) -> bool:
        """
        Validate directory with source files.
        :param source: Directory name
        :return:   boolean
        """
        result = False
        try:
            if os.path.exists(source) and os.path.isdir(source)\
                    and os.access(source, os.R_OK) and os.listdir(source):
                result = True
            else:
                raise IOError("Bad directory <{}>".format(source))
        except IOError as e:
            logger.error(e)
        return result

    @staticmethod
    def is_valid_file(source: str) -> bool:
        """
        Validate file.
        :param source: file name
        :return:   boolean
        """
        return os.path.exists(source) and os.path.isfile(source) and os.access(source, os.R_OK)

    # Uploader speific utils
    @staticmethod
    def read_file_json(d: str) -> dict:
        result = {}
        try:
            with open(d) as f:
                result = json.load(f)
        except IOError as e:
            logger.error(e)
        return result

    @staticmethod
    def read_file_json_it(d: str) -> Iterable:
        result = {}
        try:
            with open(d) as f:
                for k, v in json.load(f).items():
                    yield k, v
        except IOError as e:
            logger.error(e)
        return result

    @staticmethod
    def read_file_json_gen(fn: str) -> Iterator[dict]:
        try:
            with open(fn) as f:
                _json = json.load(f)
                yield _json
        except IOError:
            raise StopIteration

    @staticmethod
    def read_file_jsonl_gen(d: str) -> Iterator[dict]:
        try:
            with open(d) as f:
                for line in f:
                    data = json.loads(line.strip())
                    yield data
        except IOError:
            raise StopIteration

    @staticmethod
    def read_file_jsonl(d: str) -> Iterator[dict]:
        result = []
        try:
            with open(d) as f:
                for line in f:
                    data = json.loads(line.strip())
                    result.append(data)
        except IOError:
            raise StopIteration
        return result

    @staticmethod
    def read_cvs(fn: str, delim="|"):
        try:
            if not FileUtils.is_valid_file(fn):
                raise FileNotFoundError
            with open(fn, encoding='utf-8') as csvfile:
                rows = csv.reader(csvfile, delimiter=delim)
                for row in rows:
                    if row:
                        yield row
        except ValueError as e:
            logger.error(e)

    @staticmethod
    def save_cvs(fn: str, rows, delim="|"):
        try:
            with open(fn, "w", encoding='utf-8') as csvfile:
                wr = csv.writer(csvfile, delimiter=delim)
                for row in rows:
                    wr.writerow(row)
        except FileNotFoundError as e:
            logger.error(e)

    @staticmethod
    def save_as_jsonl(data, fn, mode="w"):
        try:
            with open(fn, mode, encoding='utf8') as outfile:
                for d in data:
                    outfile.write(json.dumps(d))
                    outfile.write("\n")
        except Exception as e:
            logger.error(e)

    @staticmethod
    def save_dict_as_jsonl(data, fn, mode="w"):
        try:
            with open(fn, mode, encoding='utf8') as outfile:
                for k, v in data.items():
                    outfile.write(json.dumps({k: v}))
                    outfile.write("\n")
        except Exception as e:
            logger.error(e)

    @staticmethod
    def save_as_json(fn, data):
        try:
            dirpath = os.path.dirname(fn)
            if not FileUtils.is_valid_dir(dirpath):
                os.makedirs(dirpath)
            with open(fn, 'w+', encoding='utf8') as outfile:
                json.dump(data, outfile, indent=4)
        except IOError as e:
            logger.error(e)

    @staticmethod
    def get_files(dirname, ext=".txt", sort=False) -> Iterable[str]:
        """
        Extract files from current directory
        :param sort: Sort flag
        :param path: Directory path
        :return result: List of files
        """
        result = []
        try:
            if FileUtils.is_valid_dir(dirname):
                for item in os.scandir(dirname):
                    fn = os.path.join(dirname, item)
                    if os.path.isfile(fn):
                        stem = Path(fn).suffix
                        if stem == ext:
                            result.append(fn)
                if sort:
                    result = sorted(result)
        except Exception as exc:
            print(exc)
        return result

    @staticmethod
    def clear_dir(d: str):
        try:
            if FileUtils.is_valid_dir(d):
                with os.scandir(d) as entries:
                    for entry in entries:
                        if entry.is_file() or entry.is_symlink():
                            os.remove(entry.path)
        except IOError as e:
            logger.error(e)
