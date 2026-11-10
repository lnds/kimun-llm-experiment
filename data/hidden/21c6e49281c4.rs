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
fn missing_story_is_reported_as_not_found() {
    let mut server = mockito::Server::new();
    let _m = server.mock("GET", "/stories/42").with_status(404).with_body("{}").create();

    let err = client(&server).get_story(42).unwrap_err();
    assert_eq!(err.to_string(), "Story #42 not found");
}

#[test]
fn server_error_is_not_reported_as_not_found() {
    let mut server = mockito::Server::new();
    let _m = server.mock("GET", "/stories/42").with_status(500).with_body("boom").create();

    let err = client(&server).get_story(42).unwrap_err().to_string();
    assert!(err.contains("500"), "{err}");
    assert!(!err.contains("not found"), "{err}");
}
