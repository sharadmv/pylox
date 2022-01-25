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

  def ancestor(self, distance: int) -> 'Environment':
    if distance <= 0:
      return self
    if self.parent is None:
      raise ValueError('Resolution error!')
    return self.parent.ancestor(distance - 1)

  def get_at(self, distance: int, name: str) -> Value:
    return self.ancestor(distance).values[name]

  def assign_at(self, distance: int, name: Token, value: Value) -> None:
    self.ancestor(distance).values[name.lexeme] = value

