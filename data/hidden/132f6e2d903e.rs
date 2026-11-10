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
fn members_are_returned_when_the_request_succeeds() {
    let mut server = mockito::Server::new();
    let body = serde_json::json!([
        {"id": "u1", "profile": {"name": "Ana Rojas", "mention_name": "ana"}},
        {"id": "u2", "profile": {"name": "Luis Soto", "mention_name": "luis"}}
    ]);
    let _m = server
        .mock("GET", "/members")
        .with_status(200)
        .with_header("content-type", "application/json")
        .with_body(body.to_string())
        .create();

    let members = client(&server).get_members().unwrap();
    let names: Vec<&str> = members.iter().map(|m| m.profile.name.as_str()).collect();
    assert_eq!(names, vec!["Ana Rojas", "Luis Soto"]);
}
