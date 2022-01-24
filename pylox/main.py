import dataclasses
import pathlib
import sys

import click
import rich.console
import rich.prompt


from pylox import errors
from pylox import interpreter
from pylox import parser
from pylox.parser import scanner
from pylox.parser import ast_printer


error_console = rich.console.Console(stderr=True)


class ReplPrompt(rich.prompt.Prompt):
  prompt_suffix: str = ' '


@dataclasses.dataclass
class Lox:

  def __post_init__(self):
    self._repl_prompt = ReplPrompt('>>')
    self.has_error = False
    self.has_runtime_error = False
    self.interpreter = interpreter.Interpreter(self)

  def token_error(self, token: scanner.Token, message: str):
    if token.type == scanner.TokenType.EOF:
      return self.report(token.line, ' at end', message)
    return self.report(token.line, f' at \'{token.lexeme}\'', message)

  def error(self, line: int, message: str):
    return self.report(line, '', message)

  def runtime_error(self, error: errors.RuntimeError):
    error_console.print(f'{error.message}\n[Line {error.token.line}]')
    self.has_runtime_error = True

  def report(self, line: int, where: str, message: str):
    error_console.print(f'[Line {line}] Error{where}: {message}')
    self.has_error = True

  def run_file(self, path: pathlib.Path):
    with path.open('r') as fp:
      source = fp.read()
    self.run(source)
    if self.has_error:
      sys.exit(65)
    if self.has_runtime_error:
      sys.exit(70)

  def run(self, source: str):
    statements = parser.parse(self, source)
    if self.has_error:
      return
    self.interpreter.interpret(statements)

  def repl(self):
    while True:
      try:
        line = self._repl_prompt()
        self.run(line)
        self.has_error = False
      except KeyboardInterrupt:
        print()
        print('Keyboard Interrupt')
        continue


@click.command()
@click.argument('file', nargs=-1, type=click.Path())
def main(file):
  lox = Lox()
  if not file:
    lox.repl()
  return lox.run_file(pathlib.Path(file[0]))


if __name__ == '__main__':
  main()
