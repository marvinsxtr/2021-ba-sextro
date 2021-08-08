from __future__ import annotations
from math import log2, pow
from typing import Any, Callable, Dict, Optional
import json


class Halstead:
    """
    This class represents the Halstead metric suite and offers a range of utility methods for 
    performing calculations on it.
    """

    def __init__(
        self,
        u_operators: float = 0.,
        operators: float = 0.,
        u_operands: float = 0.,
        operands: float = 0.
    ):
        # The number of Halstead metrics combined (used for average computation)
        self.n: int = int(sum([u_operators, operators, u_operands, operands]) > 0.)

        # `η1`, the number of distinct operators
        self.u_operators: float = u_operators
        # `N1`, the number of total operators
        self.operators: float = operators

        # `η2`, the number of distinct operands
        self.u_operands: float = u_operands
        # `N2`, the number of total operands
        self.operands: float = operands

    def try_calc(  # type: ignore
        func: Callable[..., Optional[float]]
    ) -> Callable[..., Optional[float]]:
        """Wrapper which catches errors that may occur during calculation (e.g. division by 0)."""
        def wrap(*args: Any, **kwargs: Any) -> Optional[float]:
            try:
                result = func(*args, **kwargs)
            except:
                result = None
            return result
        return wrap

    @try_calc
    def length(self) -> Optional[float]:
        """Returns the program length."""
        return self.operators + self.operands

    @try_calc
    def estimated_program_length(self) -> Optional[float]:
        """Returns the calculated estimated program length."""
        return self.u_operators * log2(self.u_operators) + self.u_operands * log2(self.u_operands)

    @try_calc
    def purity_ratio(self) -> Optional[float]:
        """Returns the purity ratio."""
        estimated_program_length = self.estimated_program_length()
        length = self.length()

        if estimated_program_length is None or length is None:
            raise TypeError

        return estimated_program_length / length

    @try_calc
    def vocabulary(self) -> Optional[float]:
        """Returns the program vocabulary."""
        return self.u_operators + self.u_operands

    @try_calc
    def volume(self) -> Optional[float]:
        """Returns the program volume (measured in bits)."""
        length = self.length()
        vocabulary = self.vocabulary()

        if length is None or vocabulary is None:
            raise TypeError

        # Assumes a uniform binary encoding for the vocabulary is used
        return length * log2(vocabulary)

    @try_calc
    def difficulty(self) -> Optional[float]:
        """Returns the estimated difficulty required to program."""
        return (self.u_operators / 2.) * (self.operands / self.u_operands)

    @try_calc
    def level(self) -> Optional[float]:
        """Returns the estimated level of difficulty required to program."""
        difficulty = self.difficulty()

        if difficulty is None:
            raise TypeError

        return 1. / difficulty

    @try_calc
    def effort(self) -> Optional[float]:
        """Returns the estimated effort required to program."""
        difficulty = self.difficulty()
        volume = self.volume()

        if difficulty is None or volume is None:
            raise TypeError

        return difficulty * volume

    @try_calc
    def time(self) -> Optional[float]:
        """
        Returns the estimated time required to program (measured in seconds).

        The floating point `18.` aims to describe the processing rate of the human brain. It is
        called Stoud number, S, and its unit of measurement is moments/seconds. A moment is the
        time required by the human brain to carry out the most elementary decision.
        5 <= S <= 20. Halstead uses 18.
        The value of S has been empirically developed from psychological reasoning, and its
        recommended value for programming applications is 18.

        Source: https://www.geeksforgeeks.org/software-engineering-halsteads-software-metrics/

        :return: Estimated time required to program
        """
        effort = self.effort()

        if effort is None:
            raise TypeError

        return effort / 18.

    @try_calc
    def bugs(self) -> Optional[float]:
        """
        Returns the estimated number of delivered bugs.

        This metric represents the average amount of work a programmer can do without introducing 
        an error. 

        The floating point `3000.` represents the number of elementary mental discriminations. A 
        mental discrimination, in psychology, is the ability to perceive and respond to differences 
        among stimuli.

        The value above is obtained starting from a constant that is different for every language 
        and assumes that natural language is the language of the brain. For programming languages, 
        the English language constant has been considered.

        After every 3000 mental discriminations a result is produced. This result, whether correct 
        or incorrect, is more than likely either used as an input for the next operation or is 
        output to the environment. If incorrect the error should become apparent. Thus, an 
        opportunity for error occurs every 3000 mental discriminations.

        Source: https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1145&context=cstech

        :return: Estimated number of delivered bugs
        """
        effort = self.effort()

        if effort is None:
            raise TypeError

        return pow(effort, 2. / 3.) / 3000.

    def __str__(self) -> str:
        """
        Prints the Halstead metrics.

        :return: Pretty printed JSON string
        """
        return json.dumps(self.as_dict(), indent=4)

    def __repr__(self) -> str:
        """Returns a string representation.

        :return: Pretty printed JSON string
        """
        return json.dumps(self.as_dict(), indent=4)

    def as_dict(self) -> Dict[str, Optional[float]]:
        """
        Returns a dict representation.

        :returns: Dict containing all Halstead metrics
        """
        return {
            "n": self.n,
            "n1": self.u_operators,
            "N1": self.operators,
            "n2": self.u_operands,
            "N2": self.operands,
            "length": self.length(),
            "estimated_program_length": self.estimated_program_length(),
            "purity_ratio": self.purity_ratio(),
            "vocabulary": self.vocabulary(),
            "volume": self.volume(),
            "difficulty": self.difficulty(),
            "level": self.level(),
            "effort": self.effort(),
            "time": self.time(),
            "bugs": self.bugs()
        }
