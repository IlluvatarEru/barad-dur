# Contributing

## Git
On the standards of using `git` in this repo.

### Creating a new branch
Before considering doing any work in this repository, create an issue describing what you want to achieve.

Once you have an issue, copy paste its title (including the issue number) and create a new branch off master by using the below command:

```
bash scripts/create_new_branch "copy_pasted_issue"
```

For example:
```
bash scripts/create_new_branch.sh "Init repo#1"
```

### Committing
Before committing, make sure to optimize imports (`CTRL + ALT + O` in PyCharm) and to inline the file (`CTRL + ALT + L` in Pycharm).

Then, commit using the below command to have a commit with the issue's title in it:
```
bash scripts/commit.sh
```
or the below to commit and push:
```
bash scripts/commit_and_push.sh
```

In general, your commit should follow the below format:
```
git commit -sm"feat: my feature"
```
or if it's a fix:
```
git commit -sm"fix: my fix"
```
i.e. have a standard commit message and sign it.

## Coding Standards

### Variable and Functions Naming
Always give meaningful names to your function:

`def square(x):` is better than `def f(x):`

but do not unnecessarily lengthen them:
`def square(x):` is better than `def get_square_of_number(x):`.

The same reasoning applies to variables, unless your function is very short and simple, do not use one letter variable names like `x` or `a`.

Obviously, respect [PEP-8](https://realpython.com/python-pep8/).

### DocStrings
When adding docstrings to document functions, follow the below format:
```
def my_func(arg1, arg2):
    """
    Description of my_func
    
    :param arg1: type, description
    :param arg2: type, description
    :return: type, description
    """
```
For example:
```
def square_number(x):
    """
    Get the square value of a number
    
    :param x: float, the number to get square of
    :return: float, the squared value of x
    """
    return x * x
```

