# Contributing to Kor

Thanks for your interest in contributing to Kor!

If you have ideas or features you would like to see implemented feel free to
open an issue and let me know.

PRs are welcome, but before spending a lot of time on the code, feel free
to either file an issue or a draft PR to discuss the implementation etc.

Be aware that I may comandeer the PRs and refactor them a bit.

## Setting up for development

The package uses [poetry](https://python-poetry.org/) together with
[poethepoet](https://github.com/nat-n/poethepoet).

### Install dependencies

```shell

poetry install --with dev,test,docs
```

### List tasks

```shell
poe
```

### autoformat

```shell
poe autoformat
```

### test

```shell
poe test
```
