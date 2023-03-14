# Contributing to Kor

Thanks for your interest in contributing to Kor!

At the moment, I'm only gauging interest from the community in this package.

If you have ideas or features you would like please open an issue and let me
know!

Feel free to submit PRs with new features, just be aware that at the moment
I'll commander them to figure out how to consolidate things into something
coherent (or at least resembling something coherent).

## Setting up for development

The package uses [poetry](https://python-poetry.org/) together with
[poethepoet](https://github.com/nat-n/poethepoet).

### Install dependencies

```shell

poetry install --with dev,test,doc
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
