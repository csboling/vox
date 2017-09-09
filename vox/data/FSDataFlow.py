from abc import abstractmethod
from typing import Generator

import os

from tensorpack.dataflow import DataFlow


class FSDataFlow(DataFlow):
    def __init__(self, path):
        self.path = os.path.realpath(os.path.expanduser(path))

