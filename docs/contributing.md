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
@TODO @Arthur Add coding standards