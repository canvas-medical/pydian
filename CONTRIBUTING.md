# Contribution Guide

## Running Tests
First: `poetry install && poetry shell`

Then at the top level dir: `pytest`, or `pytest --cov` to view code coverage

## Opening a PR
Use this convention when creating a new branch: `{your_abbrv_name}/{issue#-contribution_description}`

E.g. `yname/general_update` or `yname/1-fix_first_issue` if it's linked to an issue. 

Thank you for contributing and working to keep things organized!

## Complimentary Libraries
Pydian leverages [python-benedict](https://github.com/fabiocaccamo/python-benedict) internally, and `benedict` objects can be used to facilitate mapping as well. Internally, Pydian uses the `DictWrapper` class which inherits from `benedict` and leverages some of its preexisting indexing functionality. Since `DictWrapper` and `benedict` are subclasses of `dict`, they can be substituted accordingly in mapping functions at essentially no extra cost.

In addition to the standard library [itertools](https://docs.python.org/3/library/itertools.html), functional tools like [funcy](https://github.com/Suor/funcy) and [more-itertools](https://github.com/more-itertools/more-itertools) can improve development and make data transforms more consistent and elegant.
