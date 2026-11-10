use super::*;
use crossterm::event::{KeyEvent, KeyModifiers};

fn story(id: i64, state: i64, position: i64, epic: Option<i64>) -> Story {
    serde_json::from_value(serde_json::json!({
        "id": id, "name": format!("Story {id}"), "workflow_state_id": state, "app_url": "",
        "position": position, "created_at": "", "updated_at": "", "epic_id": epic
    }))
    .unwrap()
}

fn workflows() -> Vec<Workflow> {
    serde_json::from_value(serde_json::json!([{
        "id": 1, "name": "Dev", "states": [
            {"id": 10, "name": "To Do", "position": 1, "type": "unstarted"},
            {"id": 20, "name": "In Progress", "position": 2, "type": "started"}
        ]
    }]))
    .unwrap()
}

fn epic(id: i64, name: &str) -> Epic {
    serde_json::from_value(serde_json::json!({
        "id": id, "name": name, "app_url": "", "created_at": "", "updated_at": ""
    }))
    .unwrap()
}

fn press(app: &mut App, code: KeyCode) {
    app.handle_key_event(KeyEvent::new(code, KeyModifiers::NONE)).unwrap();
}

#[test]
fn up_moves_the_selection_within_a_column() {
    let stories = vec![story(1, 10, 1, None), story(2, 10, 2, None), story(3, 10, 3, None)];
    let mut app = App::new(stories, workflows(), String::new(), None);
    assert_eq!(app.get_selected_story().map(|s| s.id), Some(1));

    press(&mut app, KeyCode::Down);
    press(&mut app, KeyCode::Down);
    assert_eq!(app.get_selected_story().map(|s| s.id), Some(3));
    press(&mut app, KeyCode::Up);
    assert_eq!(app.get_selected_story().map(|s| s.id), Some(2));
    press(&mut app, KeyCode::Char('k'));
    press(&mut app, KeyCode::Char('k'));
    assert_eq!(app.get_selected_story().map(|s| s.id), Some(3), "Up from the top wraps to the bottom");
}
