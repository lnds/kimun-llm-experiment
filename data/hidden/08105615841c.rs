use super::*;

fn story(id: i64, state: i64, position: i64) -> api::Story {
    serde_json::from_value(serde_json::json!({
        "id": id, "name": format!("Story {id}"), "workflow_state_id": state, "app_url": "",
        "position": position, "created_at": "", "updated_at": ""
    }))
    .unwrap()
}

fn ids(app: &App, state: i64) -> Vec<i64> {
    app.stories_by_state.get(&state).map(|v| v.iter().map(|s| s.id).collect()).unwrap_or_default()
}

#[test]
fn moving_a_story_leaves_the_others_where_they_were() {
    let workflows: Vec<api::Workflow> = serde_json::from_value(serde_json::json!([{
        "id": 1, "name": "Dev", "states": [
            {"id": 10, "name": "To Do", "position": 1, "type": "unstarted"},
            {"id": 20, "name": "In Progress", "position": 2, "type": "started"}
        ]
    }]))
    .unwrap();
    let mut app = App::new(
        vec![story(1, 10, 1), story(2, 10, 2), story(3, 20, 3)],
        workflows,
        String::new(),
        None,
    );

    update_story_state(&mut app, 1, story(1, 20, 1));

    assert_eq!(ids(&app, 10), vec![2]);
    assert_eq!(ids(&app, 20), vec![3, 1]);
}
