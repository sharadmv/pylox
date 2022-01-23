import pyparsing as pp

BOOLEAN = (
    pp.Literal('true')
    | pp.Literal('false'))

NUMBER = (
    pp.Word(pp.nums))

DATA_TYPE = (
    BOOLEAN)
