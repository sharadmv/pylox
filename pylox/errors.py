from pylox.parser import scanner

__all__ = [
    'ScanningError',
    'ParsingError',
]


class ScanningError(Exception):
  
  def __init__(self, line: int, message: str):
    super().__init__(line, message)
    self.message = message
    self.line = line


class ParsingError(Exception):
  
  def __init__(self, line: int, message: str):
    super().__init__(line, message)
    self.message = message
    self.line = line


class RuntimeError(Exception):
  
  def __init__(self, token: scanner.Token, message: str):
    super().__init__(token, message)
    self.message = message
    self.token = token


