use super::*;
use std::path::{Path, PathBuf};
use std::process::Command as Git;

fn git(dir: &Path, args: &[&str]) {
    let ok = Git::new("git")
        .args(["-c", "user.name=T", "-c", "user.email=t@example.com"])
        .args(args)
        .current_dir(dir)
        .output()
        .unwrap()
        .status
        .success();
    assert!(ok, "git {args:?} failed");
}

/// Runs `f` with `dir` as the current directory, restoring the previous one.
fn inside<T>(dir: &Path, f: impl FnOnce() -> T) -> T {
    struct Back(PathBuf);
    impl Drop for Back {
        fn drop(&mut self) {
            let _ = std::env::set_current_dir(&self.0);
        }
    }
    let _back = Back(std::env::current_dir().unwrap());
    std::env::set_current_dir(dir).unwrap();
    f()
}

fn repo_with_commit() -> tempfile::TempDir {
    let dir = tempfile::tempdir().unwrap();
    git(dir.path(), &["init", "-q"]);
    git(dir.path(), &["commit", "-q", "--allow-empty", "-m", "first"]);
    dir
}

#[test]
fn a_clone_is_a_git_repo_and_a_plain_directory_is_not() {
    let repo = repo_with_commit();
    let ctx = inside(repo.path(), || GitContext::detect().unwrap());
    assert!(ctx.is_git_repo());

    let plain = tempfile::tempdir().unwrap();
    let ctx = inside(plain.path(), || GitContext::detect().unwrap());
    assert!(!ctx.is_git_repo());
}
