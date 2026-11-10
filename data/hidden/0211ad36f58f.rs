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
fn up_in_edit_popup_moves_to_the_epic_before_the_current_one() {
    let mut app = App::new(vec![story(1, 10, 1, Some(200))], workflows(), String::new(), None);
    app.epics = vec![epic(100, "Alpha"), epic(200, "Beta"), epic(300, "Gamma")];

    press(&mut app, KeyCode::Char('e'));
    assert!(app.show_edit_popup);
    assert_eq!(app.edit_popup_state.epic_id, Some(200));
    for _ in 0..3 {
        press(&mut app, KeyCode::Tab);
    }
    assert_eq!(app.edit_popup_state.selected_field, EditField::Epic);

    press(&mut app, KeyCode::Up);
    assert_eq!(app.edit_popup_state.epic_id, Some(100), "Up from Beta should select Alpha");
}
