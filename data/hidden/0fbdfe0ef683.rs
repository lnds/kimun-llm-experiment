use super::*;

fn client(server: &mockito::Server) -> ShortcutClient {
    ShortcutClient {
        client: reqwest::blocking::Client::new(),
        api_token: "t".to_string(),
        base_url: server.url(),
        debug: false,
    }
}

#[test]
fn successful_state_change_returns_the_moved_story() {
    let mut server = mockito::Server::new();
    let body = serde_json::json!({
        "id": 42, "name": "s", "workflow_state_id": 20, "app_url": "",
        "position": 0, "created_at": "", "updated_at": ""
    });
    let _m = server
        .mock("PUT", "/stories/42")
        .with_status(200)
        .with_header("content-type", "application/json")
        .with_body(body.to_string())
        .create();

    let story = client(&server).update_story_state(42, 20).unwrap();
    assert_eq!((story.id, story.workflow_state_id), (42, 20));
}
