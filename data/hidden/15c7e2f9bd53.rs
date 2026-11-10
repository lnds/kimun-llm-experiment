use super::*;

fn story(id: i64, name: &str, position: i64) -> api::Story {
    serde_json::from_value(serde_json::json!({
        "id": id, "name": name, "workflow_state_id": 10, "app_url": "",
        "position": position, "created_at": "", "updated_at": ""
    }))
    .unwrap()
}

#[test]
fn editing_a_story_changes_only_that_story() {
    let workflows: Vec<api::Workflow> = serde_json::from_value(serde_json::json!([{
        "id": 1, "name": "Dev", "states": [
            {"id": 10, "name": "To Do", "position": 1, "type": "unstarted"},
            {"id": 20, "name": "In Progress", "position": 2, "type": "started"}
        ]
    }]))
    .unwrap();
    let mut app = App::new(
        vec![story(1, "First", 1), story(2, "Second", 2)],
        workflows,
        String::new(),
        None,
    );

    update_story_details(&mut app, 2, story(2, "Second, renamed", 2));

    let column: Vec<(i64, String)> =
        app.stories_by_state[&10].iter().map(|s| (s.id, s.name.clone())).collect();
    assert_eq!(
        column,
        vec![(1, "First".to_string()), (2, "Second, renamed".to_string())]
    );
}
