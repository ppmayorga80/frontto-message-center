"""json line library
to handle read and write operations on local and cloud files
in both format: plain or compressed (gzip)
"""
import os
import logging
from multiprocessing import cpu_count, Pool
from itertools import count
from typing import Optional, Type, TypeVar, Union

import json
import smart_open


T = TypeVar("T")


def _jsonl_parse_one_line(args):
    """parse one line at a time"""
    line = args
    raw_document = json.loads(line)
    return raw_document


def _jsonl_dumps_one_object(args):
    """dumps one object at a time"""
    x = args
    line = json.dumps(x)
    return line


def _split_str(args):
    """split string"""
    text = args
    lines = text.split('\n') if text else []
    return lines


def _parse_documents(args):
    """split string"""
    lines = args
    documents = [json.loads(line) for line in lines]
    return documents


class Jsonl:
    """class that concentrates common json line operations"""

    @classmethod
    def count_lines(cls, path: str) -> int:
        """count the number of lines if the path provided

        :param path: the file path to be read
        :param tqdm_kwargs: if provided (at least {}) define a tqdm progress bar (default: None)
        :return: the number of lines in the file
        """
        # 1. compute tqdm_kwargs
        tqdm_kwargs = {
            **{
                "desc": f"count_lines('{path})'"
            },
            **tqdm_kwargs
        } if tqdm_kwargs is not None else tqdm_kwargs
        # 2. open the file
        with smart_open.open(path) as fp:
            # 2.1 count the number of lines
            n_lines = len([1 for _ in fp])
        return n_lines

    @classmethod
    def read(cls,
             path: str,
             offset: int = 0,
             limit: Optional[int] = None) -> list[T | dict]:
        """read a json line file
        if provided offset and/or limit, this method jumps the first `offset` lines
        and only return (at most) `limit` number of objects.

        :param path: path to the file to be read
        :param offset: skip the first `offset` lines (default: 0)
        :param limit: if provided, return at most `limit` objects (default: None)
        :return: the list of json objects
        """
        # 2. open the file
        with smart_open.open(path) as fp:
            # 2.1 skipping the first offset lines
            if offset:
                # define the iterator and skip those lines
                skip_iterator = range(offset)
                _ = [_ for _, _ in zip(skip_iterator, fp)]

            # 2.2 define the read iterator
            limit_iterator = count() if limit is None else range(limit)
            tqdm_limit_iterator = limit_iterator

            # 2.3 read the limit number of lines at most
            # 2.4 read the data and transforms to object
            data = [
                json.loads(line_k)
                for _, line_k in zip(tqdm_limit_iterator, fp)
            ]

        return data

    @classmethod
    def write(cls,
              path: str,
              data: list,
              append_mode: bool = False) -> int:
        """write a json line file
        converting every dict in data to a string and send it to the file.

        if append_mode is True and the path exists, the data will be appended to the end
        otherwise the file will be replaced with the content in data.
        In other words, if append_mode==False, then, the open function is called
        with mode="w"; if append_mode==True, then, is called with mode="a".
        NOTE: at the date to code this function nor GCP, nor AWS support append_mode.

        if provide tqdm_kwargs, a progress bar will be displayed.

        :param path: the file to be writen
        :param data: the list of dicts to be saved to the file
        :param append_mode: flag to set append mode (default: False)
        :return: the number of objects written
        """
        # 1. compute the number of objects
        n_data = len(data)
        # 2 *** create directory if necessary ***
        create_dir_fn = lambda x: os.makedirs(
            os.path.dirname(x), exist_ok=True) if os.path.abspath(
                path).startswith('/') else ""
        create_dir_fn(path)

        # 3. open the file if writing or append mode
        with smart_open.open(path, mode="w" if not append_mode else "a") as fp:
            # 3.1 define the iterator (tqdm(data) or data)
            data_iterator = data
            # 3.2  in writing mode new line prefix should be "", in append mode new line should be "\n"
            nl_prefix = "\n" if append_mode else ""
            # 3.3 iterate over all objects
            for obj in data_iterator:
                # parse object as a string
                line = nl_prefix + json.dumps(obj)
                # write a new line
                fp.write(line)
                # new line should be "\n"
                nl_prefix = "\n"

        # return the number of objects
        return n_data

    @classmethod
    def parallel_read(
            cls,
            path: str,
            offset: int = 0,
            limit: Optional[int] = None,
            workers: Optional[int] = None) -> Union[list[T], list[dict]]:
        """
        read a jsonl in parallel
        to optimize this process we divide it in two main steps:
        1. read the file line by line as a text (to not overload read process)
        2. parse content in parallel (parsing is the most expensive task)
        if workers is not defined will use the number of cpus in your computer
        :param path: the file to be read
        :param offset: read the file starting at this line (if defined)
        :param limit: read up to this number of lines
        :param workers: the number of parallel jobs
        :return: the list of documents parsed as dictionary
        """

        # define the number of workers to be used
        workers = workers if workers is not None else cpu_count()

        # 1. read the file in plain text
        with smart_open.open(path) as fp:
            # a. skip first `offset` lines
            _ = [_ for _, _ in zip(range(offset), fp)]
            # b. read up to `limit` lines
            limit_it = count() if limit is None else range(limit)
            zip_it = zip(limit_it, fp)

            lines = [line for _, line in zip_it]
            n = len(lines)

        # 2. parse each line in parallel
        # a. create the list of parameters
        with Pool(workers) as pool:
            # c. if pass tqdm kwargs use the imap function in conjunction with tqdm
            #    or use the traditional map function without tqdm
            list_of_documents = pool.map(_jsonl_parse_one_line, lines)

        # 3. return the list of documents
        return list_of_documents

    @classmethod
    def parallel_write(cls,
                       path: str,
                       data: list,
                       workers: Optional[int] = None) -> int:
        """write in parallel"""
        workers = workers if workers is not None else cpu_count()
        data = data if isinstance(data, list) else [data]
        n = len(data)

        with Pool(workers) as pool:
            # if pass tqdm kwargs use the imap function in conjunction with tqdm
            # or use the traditional map function without tqdm
            lines = pool.map(_jsonl_dumps_one_object, data)

            # *** create directory if necessary ***
            create_dir_fn = lambda x: os.makedirs(
                os.path.dirname(x), exist_ok=True) if os.path.abspath(
                    path).startswith('/') else ""
            create_dir_fn(path)

            msg = f"writting content to '{path}'"
            logging.info(msg)
            content = "\n".join(lines)
            with smart_open.open(path, "w") as fp:
                fp.write(content)

            return len(content)
