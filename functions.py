"""
functions.py
"""
import numpy as np
from sympy import lambdify, abc, latex, diff, integrate
from sympy.parsing.sympy_parser import parse_expr
from sympy.core import basic
from typing import Dict


class VariableNotFoundError(Exception):
    """Variable not found error.
    """
    def __str__(self) -> None:
        """Print this exception.
        """
        return "Variable not found"


def rect(x: np.ndarray) -> np.ndarray:
    """
    Rectangle function.
    """
    return np.array(
        [
            1.0 if (x_i < 0.5 and x_i > -0.5) else 0.
            for x_i in x
        ]
        )


def noise(x: np.ndarray) -> np.ndarray:
    """
    This is the noise function.
    """
    return np.array([2.0*np.random.rand() - 1.0 for _ in range(len(x))])


def multiplies_var(main_var: basic.Basic, arb_var: basic.Basic,
                   expr: basic.Basic) -> bool:
    """
    This function takes in the following parameters:
    main_var [sympy.core.basic.Basic]: the main variable
    arb_var [sympy.core.basic.Basic]: an arbitrary variable
    expr [sympy.core.basic.Basic]: an algebraic expression
    Check to see if an arbitrary variable multiplies
    a sub expression that contains the main variable.
    If it does, return True else False.

    The following examples should clarify what this function does:

    >>> expr = parse_expr("a*sinh(k*x) + c")
    >>> multiplies_var(abc.x, abc.a, expr)
    True
    >>> multiplies_var(abc.x, abc.k, expr)
    True
    >>> multiplies_var(abc.x, abc.b, expr)
    False

    >>> expr = parse_expr("w*a**pi*sin(k**10*tan(y*x)*z) + d + e**10*tan(f)")
    >>> multiplies_var(abc.x, abc.w, expr)
    True
    >>> multiplies_var(abc.x, abc.a, expr)
    True
    >>> multiplies_var(abc.x, abc.k, expr)
    True
    >>> multiplies_var(abc.x, abc.z, expr)
    True
    >>> multiplies_var(abc.x, abc.y, expr)
    True
    >>> multiplies_var(abc.x, abc.d, expr)
    False
    >>> multiplies_var(abc.x, abc.e, expr)
    False
    >>> multiplies_var(abc.x, abc.f, expr)
    False
    """
    arg_list = []
    for arg1 in expr.args:
        if arg1.has(main_var):
            arg_list.append(arg1)
            for arg2 in expr.args:
                if ((arg2 is arb_var or (arg2.is_Pow and arg2.has(arb_var)))
                   and expr.has(arg1*arg2)):
                    return True
    return any([multiplies_var(main_var, arb_var, arg)
                for arg in arg_list if
                (arg is not main_var)])


class Functionx:
    """
    A callable function class that is a function of x,
    as well as any number of parameters

    Attributes:
    latex_repr [str]: The function as a LaTeX string.
    symbols [sympy.Symbol]: All variables used in this function.
    parameters [sympy.Symbol]: All variables used in this function,
                               except for x.
    """

    # Private Attributes:
    # _symbolic_func [sympy.basic.Basic]: symbol function
    # _lambda_func [sympy.Function]: lamba function

    def __init__(self, function_name: str) -> None:
        """
        The initializer. The parameter must be a
        string representation of a function, and it needs to
        be a function of x.
        """
        # Dictionary of modules and user defined functions.
        # Used for lambdify from sympy to parse input.
        module_list = ["numpy", {"rect": rect, "noise": noise}]
        self._symbolic_func = parse_expr(function_name)
        symbol_set = self._symbolic_func.free_symbols
        symbol_list = list(symbol_set)
        if abc.x not in symbol_list:
            raise VariableNotFoundError("x not found - the"
                                        "function inputed must "
                                        "be a function of x.")
        self.latex_repr = latex(self._symbolic_func)
        symbol_list.remove(abc.x)
        self.parameters = symbol_list
        x_list = [abc.x]
        x_list.extend(symbol_list)
        self.symbols = x_list
        self._lambda_func = lambdify(
            self.symbols, self._symbolic_func, modules=module_list)

    def __call__(self, x: np.array, *args: float) -> np.array:
        """
        Call this class as if it were a function.
        """
        return self._lambda_func(x, *args)

    def derivative(self) -> None:
        """
        Mutate this function into its derivative.
        """
        self._symbolic_func = diff(self._symbolic_func,
                                   abc.x)
        self._reset_samesymbols()

    def antiderivative(self) -> None:
        """
        Mutate this function into its antiderivative.
        """
        self._symbolic_func = integrate(self._symbolic_func,
                                        abc.x)
        self._reset_samesymbols()

    def _reset_samesymbols(self) -> None:
        """
        Set to a new function, assuming the same variables.
        """
        self.latex_repr = latex(self._symbolic_func)
        self._lambda_func = lambdify(
            self.symbols, self._symbolic_func)

    def get_default_values(self) -> Dict[basic.Basic, float]:
        """
        Get a dict of the suggested default values for each parameter
        used in this function.
        """
        return {s:
                float(multiplies_var(self.symbols[0], s, self._symbolic_func))
                for s in self.parameters}


if __name__ == "__main__":
    import doctest
    from time import perf_counter
    t1 = perf_counter()
    doctest.testmod()
    t2 = perf_counter()
    print(t2 - t1)
    f = Functionx("a*sin(k*x) + d")
    print(f.get_default_values())
    f.antiderivative()
    print(f.latex_repr)
    print(f._symbolic_func)
