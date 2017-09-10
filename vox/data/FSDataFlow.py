from abc import abstractmethod
from typing import Generator

import os

from tensorpack.dataflow import DataFlow


class FSDataFlow(DataFlow):
    @staticmethod
    def resolve_path(path):
        return os.path.realpath(os.path.expanduser(path))

    def __init__(self, path):
        self.path = self.resolve_path(path)

