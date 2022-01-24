import abc
import dataclasses

from typing import Any, List, Optional

from pylox.parser import scanner

Token = scanner.Token


class Node(metaclass=abc.ABCMeta):
  
  @abc.abstractmethod
  def accept(self, visitor: 'NodeVisitor') -> Any:
    pass

class Expr(Node):
  pass
  

@dataclasses.dataclass
class Assign(Expr):
  name: Token
  value: Expr

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_assign(self)


@dataclasses.dataclass
class Binary(Expr):
  left: Expr
  operator: Token
  right: Expr

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_binary(self)

@dataclasses.dataclass
class Call(Expr):
  callee: Expr
  paren: Token
  arguments: List[Expr]

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_call(self)


@dataclasses.dataclass
class Grouping(Expr):
  expression: Expr

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_grouping(self)

@dataclasses.dataclass
class Literal(Expr):
  value: scanner.Literal

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_literal(self)


@dataclasses.dataclass
class Logical(Expr):
  left: Expr
  operator: Token
  right: Expr

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_logical(self)


@dataclasses.dataclass
class Unary(Expr):
  operator: Token
  right: Expr

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_unary(self)


@dataclasses.dataclass
class Variable(Expr):
  name: Token

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_variable(self)


class Stmt(Node):
  pass


@dataclasses.dataclass
class ExpressionStmt(Stmt):
  expression: Expr

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_expression_stmt(self)


@dataclasses.dataclass
class FunctionDecl(Stmt):
  name: Token
  params: List[Token]
  body: List[Stmt]

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_function_decl(self)


@dataclasses.dataclass
class If(Stmt):
  condition: Expr
  then_branch: Stmt
  else_branch: Optional[Stmt]

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_if(self)


@dataclasses.dataclass
class PrintStmt(Stmt):
  expression: Expr

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_print_stmt(self)


@dataclasses.dataclass
class ReturnStmt(Stmt):
  keyword: Token
  value: Optional[Expr]

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_return_stmt(self)

@dataclasses.dataclass
class While(Stmt):
  condition: Expr
  body: Stmt

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_while(self)

@dataclasses.dataclass
class Block(Stmt):
  statements: List[Stmt]

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_block(self)


@dataclasses.dataclass
class VarDecl(Stmt):
  name: Token
  initializer: Optional[Expr]

  def accept(self, visitor: 'NodeVisitor'):
    return visitor.visit_var_decl(self)


class NodeVisitor(metaclass=abc.ABCMeta):
  
  @abc.abstractmethod
  def visit_assign(self, expr: Assign) -> Any:
    pass

  @abc.abstractmethod
  def visit_call(self, expr: Call) -> Any:
    pass

  @abc.abstractmethod
  def visit_binary(self, expr: Binary) -> Any:
    pass

  @abc.abstractmethod
  def visit_grouping(self, expr: Grouping) -> Any:
    pass

  @abc.abstractmethod
  def visit_literal(self, expr: Literal) -> Any:
    pass

  @abc.abstractmethod
  def visit_logical(self, expr: Logical) -> Any:
    pass

  @abc.abstractmethod
  def visit_unary(self, expr: Unary) -> Any:
    pass

  @abc.abstractmethod
  def visit_variable(self, expr: Variable) -> Any:
    pass

  @abc.abstractmethod
  def visit_function_decl(self, stmt: If) -> Any:
    pass

  @abc.abstractmethod
  def visit_if(self, stmt: If) -> Any:
    pass

  @abc.abstractmethod
  def visit_expression_stmt(self, stmt: ExpressionStmt) -> Any:
    pass

  @abc.abstractmethod
  def visit_print_stmt(self, stmt: PrintStmt) -> Any:
    pass

  @abc.abstractmethod
  def visit_return_stmt(self, stmt: ReturnStmt) -> Any:
    pass

  @abc.abstractmethod
  def visit_while(self, stmt: While) -> Any:
    pass

  @abc.abstractmethod
  def visit_block(self, stmt: Block) -> Any:
    pass

  @abc.abstractmethod
  def visit_var_decl(self, stmt: VarDecl) -> Any:
    pass

