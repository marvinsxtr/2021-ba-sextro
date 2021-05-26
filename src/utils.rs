use async_gitlib::RepoClone;
use tokio::process::Command;
use std::{
    fs,
    error::Error
};

fn get_repo_path(url: &str, tool: Option<&str>) -> String {
    let path_vec = url.split("/").collect::<Vec<&str>>();
    let names = path_vec.as_slice()[path_vec.len() - 2..].to_vec();
    let name = names.join("/");

    if let Some(tool) = tool {
        format!("./data/out/{}/{}", tool, name)
    } else {
        format!("./data/tmp/{}", name)
    }
}

pub(crate) async fn clone_repo(url: &str) {
    println!("Cloning {} ...", url);

    let target = &get_repo_path(url, None);

    let mut task = RepoClone::default();

    if let Err(_) = task.clone(url, &target).await {
        task.set_branch("main");
        task.clone(url, &target).await.unwrap_or_else(|err| {
            eprintln!("Skipped {}: {}", target, err.message());
        });
    }
}

pub(crate) fn delete_repo(url: &str) {
    let repo_path = get_repo_path(url, None);
    let path_vec = repo_path.split("/").collect::<Vec<&str>>();
    let names = path_vec.as_slice()[..path_vec.len() - 1].to_vec();
    let path = names.join("/");

    fs::remove_dir_all(&path).unwrap_or_else(|err| {
        println!("{}", err);
    });

    println!("Deleted {}", path);
}

pub(crate) async fn run_tools(url: &str) -> Result<(), Box<dyn Error>> {
    let tools: Vec<(&str, &str)> = vec![
        ("rca", "rust-code-analysis-cli -m -p ./* -O json -o ../../../."),
        ("clippy", "cargo clippy --message-format=json >> ../../../.")
    ];

    for (tool, cmd) in tools {
        run_tool(url, tool, cmd).await.unwrap();
    }

    Ok(())
}

pub(crate) async fn run_tool(url: &str, tool: &str, cmd: &str) -> Result<(), Box<dyn Error>> {
    let tmp_path: String = get_repo_path(url, None);
    let out_path: String = get_repo_path(url, Some(tool));

    let command = if tool == "clippy" {
        format!("{}{}/clippy.json", cmd, out_path)
    } else {
        format!("{}{}", cmd, out_path)
    };

    fs::create_dir_all(&out_path).unwrap();

    let output = Command::new("sh")
        .arg("-c")
        .arg(command)
        .current_dir(tmp_path)
        .output();

    output.await?;

    Ok(())
}