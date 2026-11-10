use super::*;
use std::io::Write;
use std::process::{Command, Stdio};

const MODE: &str = "HIDDEN_CHECK_PROMPTS";

/// The description `from_prompts` reads from `input`, typed into a child's stdin.
fn description_typed(input: &str) -> String {
    let mut child = Command::new(std::env::current_exe().unwrap())
        .args(["story_creator::hidden_check::two_blank_lines_end_the_description", "--exact", "--nocapture", "--test-threads=1"])
        .env(MODE, "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    child.stdin.take().unwrap().write_all(input.as_bytes()).unwrap();
    let out = child.wait_with_output().unwrap();
    let out = String::from_utf8_lossy(&out.stdout);
    let start = out.find("<<DESC").expect("no description printed") + 6;
    let end = out.find("DESC>>").unwrap();
    out[start..end].to_string()
}

#[test]
fn two_blank_lines_end_the_description() {
    if std::env::var(MODE).is_ok() {
        let story = StoryCreator::from_prompts(
            "me".into(), 1, Some("A story".into()), Some("feature".into()),
        )
        .unwrap();
        println!("<<DESC{}DESC>>", story.description);
        return;
    }
    assert_eq!(description_typed("First\n\n\nLater\n\n\n"), "First");
}
