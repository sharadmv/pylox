import abc
import dataclasses
import time

from typing import Any, List

from pylox.interpreter import environment
from pylox.interpreter import visitor
from pylox.parser import ast

Value = Any
Interpreter = visitor.Interpreter
Environment = environment.Environment


class LoxCallable(metaclass=abc.ABCMeta):

  @abc.abstractmethod
  def arity(self) -> int:
    pass

  @abc.abstractmethod
  def call(self, interpreter: Interpreter, arguments: List[Value]) -> Value:
    pass


class Clock(LoxCallable):

  def arity(self):
    return 0

  def call(self, interpreter: Interpreter, arguments: List[Value]):
    del interpreter, arguments
    return time.time() * 1000

  def __str__(self):
    return '<native fn>'


@dataclasses.dataclass
class LoxFunction(LoxCallable):
  declaration: ast.FunctionDecl
  closure: environment.Environment
  is_initializer: bool

  def arity(self) -> int:
    return len(self.declaration.params)

  def call(self, interpreter: Interpreter, arguments: List[Value]) -> Value:
    env = environment.Environment(parent=self.closure)
    for arg, param in zip(arguments, self.declaration.params):
      env.define(param.lexeme, arg)
    try:
      interpreter.execute_block(self.declaration.body, env)
    except visitor.Return as e:
      return e.value
    if self.is_initializer:
      return self.closure.get_at(0, 'this')

  def bind(self, instance):
    env = Environment(self.closure)
    env.define('this', instance)
    return LoxFunction(self.declaration, env, self.is_initializer)

  def __str__(self):
    return f'<fn {self.declaration.name.lexeme}>'
