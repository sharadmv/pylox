from absl.testing import absltest

from pylox.parser import ast
from pylox.parser import ast_printer
from pylox.parser import scanner

Token = scanner.Token
TokenType = scanner.TokenType

printer = ast_printer.AstPrinter()

class AstPrinterTest(absltest.TestCase):

  def test_print_expr(self):
    binary_expr = ast.Binary(
        ast.Unary(
          Token(TokenType.MINUS, '-', None, 1),
          ast.Literal(123)),
        Token(TokenType.STAR, '*', None, 1),
        ast.Grouping(ast.Literal(45.67)))
    expected_string = '(* (- 123) (group 45.67))'
    assert printer.print(binary_expr) == expected_string

if __name__ == '__main__':
  absltest.main()
