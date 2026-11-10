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
fn enter_on_description_creates_an_epic_with_a_name() {
    let mut app = App::new(vec![story(1, 10, 1, None)], workflows(), String::new(), None);

    press(&mut app, KeyCode::Char('E'));
    assert!(app.show_create_epic_popup);
    for c in "Billing".chars() {
        press(&mut app, KeyCode::Char(c));
    }
    press(&mut app, KeyCode::Enter); // to Description
    press(&mut app, KeyCode::Enter); // submit
    assert!(app.create_epic_requested, "an epic with a name should be requested");
    assert!(!app.show_create_epic_popup);
}

#[test]
fn enter_on_description_without_a_name_keeps_the_popup_open() {
    let mut app = App::new(vec![story(1, 10, 1, None)], workflows(), String::new(), None);

    press(&mut app, KeyCode::Char('E'));
    press(&mut app, KeyCode::Enter);
    press(&mut app, KeyCode::Enter);
    assert!(!app.create_epic_requested);
    assert!(app.show_create_epic_popup);
}
