You are fixing a bug in the Rust project at {dir}. Someone introduced a bug in the source code under src/ (not in the tests), and now part of the test suite fails. Find the bug and fix it with the smallest correct change.

- Run the tests with: cd {dir} && cargo test --no-fail-fast -q
- Do not modify any test: nothing under tests/, no test module under src/ (files named tests.rs or under a tests/ directory) and no #[cfg(test)] block.
- Work only inside that directory. Do not read other directories on this machine, other copies of this project, or the project's code online. The git history holds no clue, and target/ holds only build output.
- Stop when the whole suite passes. Reply with one line: file:line of the change, and what was wrong.
