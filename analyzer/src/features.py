from typing import Dict, List, Optional
from enum import Enum


class Features(Enum):
    """
    This class contains a mapping of so called features to their respective AST node token names.
    """
    LIFETIMES = ("lifetime", "for_lifetimes", "for_lifetimes_repeat1")
    MACROS = ("macro_definition", "macro_rule", "macro_rules!",
              "macro_definition_repeat1", "macro_invocation")
    TRAIT_BOUNDS = ("trait_bounds", "trait_bounds_repeat1", "higher_ranked_trait_bound",
                    "removed_trait_bound", "where", "where_clause", "where_clause_repeat1", "where_predicate")
    ASYNC = ("async", "async_block", "await", "await_expression")
    UNSAFE = ("unsafe", "unsafe_block")
    TRAITS = ("trait", "trait_item")
    CLOSURES = ("closure_parameters_repeat1", "closure_expression", "closure_parameters")

    @staticmethod
    def as_dict() -> Dict[str, List[str]]:
        """
        Returns a dict representation of all features.

        :return: Dict mapping the features to a list of tokens
        """
        return dict(map(lambda x: (x.name.lower(), x.value), Features))

    @staticmethod
    def get_feature_by_token(token: str) -> Optional[str]:
        """
        Finds the feature for a given token.

        :param token: Name of the token to search
        :return: Name of the feature if the token is valid
        """
        for feature, tokens in Features.as_dict().items():
            if token in tokens:
                return feature.lower()
        return None
