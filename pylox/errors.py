__all__ = [
    'ScanningError',
    'ParsingError',
    'RuntimeError',
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
  
  def __init__(self, token, message: str):
    super().__init__(token, message)
    self.message = message
    self.token = token
