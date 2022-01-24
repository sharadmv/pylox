from pylox.parser import ast


class AstPrinter(ast.NodeVisitor):
  
  def print(self, expr: ast.Expr) -> str:
    return expr.accept(self)

  def parenthesize(self, name: str, *exprs: ast.Expr) -> str:
    return f'({name} {" ".join(expr.accept(self) for expr in exprs)})'

  def visit_binary(self, expr: ast.Binary) -> str:
    return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

  def visit_grouping(self, expr: ast.Grouping):
    return self.parenthesize('group', expr.expression)

  def visit_literal(self, expr: ast.Literal):
    if expr.value is None:
      return 'nil'
    return str(expr.value)

  def visit_unary(self, expr: ast.Unary):
    return self.parenthesize(expr.operator.lexeme, expr.right)
