import dataclasses

from typing import Any, Dict, Optional

from pylox import errors
from pylox.parser import scanner

Value = Any
Token = scanner.Token


@dataclasses.dataclass
class Environment:
  parent: Optional['Environment'] = None
  
  def __post_init__(self):
    self.values: Dict[str, Value] = {}

  def define(self, name: str, value: Value):
    self.values[name] = value

  def get(self, token: Token) -> Value:
    if token.lexeme in self.values:
      return self.values[token.lexeme]
    if self.parent:
      return self.parent.get(token)
    raise errors.RuntimeError(token, f'Undefined variable \'{token.lexeme}\'.')

  def assign(self, token: Token, value: Value) -> None:
    if token.lexeme not in self.values:
      if self.parent:
        return self.parent.assign(token, value)
      raise errors.RuntimeError(token, f'Undefined variable \'{token.lexeme}\'.')
    self.define(token.lexeme, value)
