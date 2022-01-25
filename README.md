# `pylox`

`pylox` is an interpreter for the `lox` programming language introduced in [Crafting Interpreters](https://craftinginterpreters.com/). As the name suggests, `pylox` is implemented in Python.

Pylox exists for pedagogical purposes and closely mirrors the `jlox` interpreter from the textbook. It is not meant to be fast or feature-complete, but it is hopefully correct.

## Usage

We uses `poetry` for package management. To install dependencies, run:

```bash
$ poetry install
```
This should install the `pylox` binary and can be accessed via `poetry shell` or `poetry run pylox`.

Alternatively, for Nix users:
```bash
$ nix build
```
