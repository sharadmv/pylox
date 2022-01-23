import click

from pylox import parser

@click.command()
@click.argument('file')
def main(file):
  return parser.parse()

if __name__ == '__main__':
  main()
