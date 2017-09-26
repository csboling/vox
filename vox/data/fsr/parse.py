from abc import ABCMeta, abstractmethod
import logging
from typing import Iterable

from sympy.polys.polytools import poly_from_expr, trunc


class TapParsingError(Exception):
    pass


class TapParser(metaclass=ABCMeta):

    @abstractmethod
    def parse(self, s) -> Iterable[int]:
        pass

    @staticmethod
    def coeffs_to_taps(coeffs):
        taps = []
        poly_order = len(coeffs) - coeffs.index(1)
        for i, b in enumerate(coeffs):
            if b == 1:
                taps.append(poly_order - i)
        return taps


class PolynomialParser(TapParser):

    def parse(self, s):
        try:
            poly, meta = poly_from_expr(s)
        except SyntaxError:
            raise TapParsingError
        else:
            gf = trunc(poly, 2)
            self.screen_polys(gf, meta)
            logging.info('input poly [ℤ]: {}'.format(poly))
            return self.coeffs_to_taps(gf.all_coeffs()[:-1])

    @staticmethod
    def screen_polys(poly, meta):
        if len(meta['gens']) > 1:
            raise TapParsingError
        if poly.all_coeffs()[-1] != 1:
            raise TapParsingError('Zero coefficient must be 1.')
