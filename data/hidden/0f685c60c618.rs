use super::*;
use crate::api::{CurrentMember, Epic, Member, SearchStoriesResult};
use anyhow::Result;
use std::process::{Command, Stdio};

struct Api;

impl ShortcutApi for Api {
    fn search_stories(&self, _: &str, _: Option<usize>) -> Result<Vec<Story>> { unimplemented!() }
    fn search_stories_page(&self, _: &str, _: Option<String>) -> Result<SearchStoriesResult> { unimplemented!() }
    fn get_workflows(&self) -> Result<Vec<Workflow>> { unimplemented!() }
    fn get_story(&self, _: i64) -> Result<Story> { unimplemented!() }
    fn update_story_state(&self, id: i64, state: i64) -> Result<Story> {
        Ok(serde_json::from_value(serde_json::json!({
            "id": id, "name": "s", "workflow_state_id": state, "app_url": "",
            "position": 0, "created_at": "", "updated_at": ""
        }))?)
    }
    fn get_current_member(&self) -> Result<CurrentMember> { unimplemented!() }
    fn update_story(&self, _: i64, _: Vec<String>) -> Result<Story> { unimplemented!() }
    fn update_story_details(&self, _: i64, _: String, _: String, _: String, _: Option<i64>) -> Result<Story> { unimplemented!() }
    fn get_members(&self) -> Result<Vec<Member>> { unimplemented!() }
    fn create_story(&self, _: String, _: String, _: String, _: String, _: i64, _: Option<i64>) -> Result<Story> { unimplemented!() }
    fn get_epics(&self) -> Result<Vec<Epic>> { unimplemented!() }
    fn create_epic(&self, _: String, _: String) -> Result<Epic> { unimplemented!() }
    fn add_comment(&self, _: i64, _: &str) -> Result<()> { unimplemented!() }
}

const MODE: &str = "HIDDEN_CHECK_DEBUG";

/// What moving story 7 writes on stderr, run in a child so it is not captured.
fn stderr_of_move(debug: bool) -> String {
    let out = Command::new(std::env::current_exe().unwrap())
        .args(["git::operations::hidden_check::moving_a_story_reports_only_in_debug", "--exact", "--nocapture", "--test-threads=1"])
        .env(MODE, if debug { "1" } else { "0" })
        .stdin(Stdio::null())
        .output()
        .unwrap();
    assert!(out.status.success());
    String::from_utf8_lossy(&out.stderr).into_owned()
}

#[test]
fn moving_a_story_reports_only_in_debug() {
    if let Ok(mode) = std::env::var(MODE) {
        let workflows: Vec<Workflow> = serde_json::from_value(serde_json::json!([{
            "id": 1, "name": "Dev", "states": [
                {"id": 20, "name": "In Progress", "position": 1, "type": "started"}
            ]
        }]))
        .unwrap();
        assert!(move_story_to_in_progress(&Api, 7, &workflows, mode == "1").is_some());
        return;
    }
    assert!(!stderr_of_move(false).contains("Moved story 7"));
    assert!(stderr_of_move(true).contains("Moved story 7 to In Progress state"));
}
