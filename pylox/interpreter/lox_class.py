import dataclasses

from typing import Any, Dict, List, Optional

from pylox import errors
from pylox.parser import scanner
from pylox.interpreter import callable
from pylox.interpreter import visitor

Interpreter = visitor.Interpreter


@dataclasses.dataclass
class LoxClass(callable.LoxCallable):
  name: str
  superclass: Optional['LoxClass']
  methods: Dict[str, callable.LoxFunction]

  def __str__(self):
    return self.name

  def arity(self) -> int:
    init = self.find_method('init')
    if init is None:
      return 0
    return init.arity()

  def call(self, interpreter: Interpreter, arguments: List[Any]):
    instance = LoxInstance(self)
    init = self.find_method('init')
    if init is not None:
      init.bind(instance).call(interpreter, arguments)
    return instance
  
  def find_method(self, name: str) -> Optional[callable.LoxFunction]:
    method = self.methods.get(name, None)
    if method:
      return method
    if self.superclass:
      return self.superclass.find_method(name)



@dataclasses.dataclass
class LoxInstance:
  klass: LoxClass

  def __post_init__(self):
    self.fields: Dict[str, Any] = {}

  def __str__(self):
    return f'{self.klass.name} instance'

  def get(self, name: scanner.Token) -> Any:
    if name.lexeme in self.fields:
      return self.fields[name.lexeme]
    method = self.klass.find_method(name.lexeme)
    if method is not None:
      return method.bind(self)
    raise errors.RuntimeError(name, f'Undefined property \'{name.lexeme}\'.')

  def set(self, name: scanner.Token, value: Any) -> Any:
    self.fields[name.lexeme] = value
