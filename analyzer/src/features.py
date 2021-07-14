from typing import Dict
from enum import Enum


class Features(tuple, Enum):
  LIFETIMES = ("for_lifetimes", "for_lifetimes_repeat1", "lifetime")
  MACROS = ("macro_definition", "macro_rules!", "macro_rule", 
    "macro_definition_repeat1", "macro_invocation")
  TRAIT_BOUNDS = ("where_clause", "where_predicate", "where_clause_repeat1", 
    "higher_ranked_trait_bound", "trait_bounds_repeat1", "removed_trait_bound", "where", "trait_bounds")
  ASYNC = ("async_block", "await", "await_expression", "async")
  UNSAFE = ("unsafe_block", "unsafe")
  TRAITS = ("trait", "trait_item")
  LINE_COMMENTS = ("line_comment")

  @staticmethod
  def as_dict() -> Dict:
    return dict(map(lambda x: (x.name.lower(), x.value), Features))

  @staticmethod
  def get_feature_by_token(token) -> str:
    for feature, tokens in Features.as_dict().items():
      if token in tokens:
        return feature.lower()
