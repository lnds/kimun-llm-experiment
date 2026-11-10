You are working on the Rust project at {dir}, a command-line and terminal client for Shortcut. A user reported this problem:

> {report}

Find the cause in the source code under src/ and fix it with the smallest correct change.

- The test suite passes today: no test reproduces the problem. Run it with: cd {dir} && HOME={dir}/.home cargo test --no-fail-fast -q (that HOME keeps the tests away from any real configuration).
- You may add tests of your own, but do not change or delete the existing ones.
- There is no network access and no Shortcut token here: do not run the program against the real service.
- Work only inside that directory. Do not read other directories on this machine, other copies of this project, or the project's code online. The git history holds no clue, and target/ holds only build output.
- Stop when you have fixed the problem and the suite passes. Reply with one line: file:line of the change, and what was wrong.
