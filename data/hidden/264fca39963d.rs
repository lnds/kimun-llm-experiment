use super::*;
use crate::api::{CurrentMember, Epic, Member, SearchStoriesResult, Story, Workflow};
use anyhow::Result;
use std::cell::Cell;

struct Api {
    moved: Cell<Option<(i64, i64)>>,
}

fn story(id: i64, state: i64) -> Story {
    serde_json::from_value(serde_json::json!({
        "id": id, "name": "s", "workflow_state_id": state, "app_url": "",
        "position": 0, "created_at": "", "updated_at": ""
    }))
    .unwrap()
}

impl ShortcutApi for Api {
    fn search_stories(&self, _: &str, _: Option<usize>) -> Result<Vec<Story>> { unimplemented!() }
    fn search_stories_page(&self, _: &str, _: Option<String>) -> Result<SearchStoriesResult> { unimplemented!() }
    fn get_workflows(&self) -> Result<Vec<Workflow>> { unimplemented!() }
    fn get_story(&self, _: i64) -> Result<Story> { unimplemented!() }
    fn update_story_state(&self, id: i64, state: i64) -> Result<Story> {
        self.moved.set(Some((id, state)));
        Ok(story(id, state))
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

#[test]
fn story_one_moves_to_in_progress() {
    let workflows: Vec<Workflow> = serde_json::from_value(serde_json::json!([{
        "id": 1, "name": "Dev", "states": [
            {"id": 10, "name": "To Do", "position": 1, "type": "unstarted"},
            {"id": 20, "name": "In Progress", "position": 2, "type": "started"}
        ]
    }]))
    .unwrap();
    let api = Api { moved: Cell::new(None) };
    let moved = move_story_to_in_progress(&api, 1, &workflows, false);
    assert_eq!(moved.map(|s| s.id), Some(1));
    assert_eq!(api.moved.get(), Some((1, 20)));
}
