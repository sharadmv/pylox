from absl.testing import absltest

from pylox.parser import scanner

Token = scanner.Token
TokenType = scanner.TokenType
scan = scanner.scan


class ScannerTest(absltest.TestCase):
  def test_eof(self):
    assert list(scan('')) == [Token(TokenType.EOF, '', None, 1)]

if __name__ == '__main__':
  absltest.main()
