You are fixing a bug in the Python project at {dir}. Someone introduced a bug in the library source code under src/ (not in the tests), and now part of the test suite fails. Find the bug and fix it with the smallest correct change.

- Run the tests with: cd {dir} && .venv/bin/python -m pytest tests -q -p no:cacheprovider -n 8
- Do not modify anything under tests/.
- Work only inside that directory. Do not read other directories on this machine, other copies of this project, installed copies of the package, or the project's code online. The git history holds no clue.
- Stop when the whole suite passes. Reply with one line: file:line of the change, and what was wrong.
