use async_gitlib::RepoClone;
use tokio::process::Command;
use std::{
    fs,
    path::Path,
    error::Error
};

fn get_repo_path(url: &str, out: bool) -> String {
    let path_vec = url.split("/").collect::<Vec<&str>>();
    let names = path_vec.as_slice()[path_vec.len() - 2..].to_vec();
    let name = names.join("/");

    match out {
        true => format!("./data/out/{}", name),
        false => format!("./data/tmp/{}", name)
    }
}

pub(crate) async fn clone_repo(url: &str) {
    println!("Cloning {} ...", url);

    let target = &get_repo_path(url, false);

    let mut task = RepoClone::default();

    match task.clone(url, &target).await {
        Err(_) => {
            task.set_branch("main");
            task.clone(url, &target).await
                .unwrap_or_else(|err| {
                    eprintln!("Skipped {}: {}", target, err.message());
                });
        },
        Ok(_) => {}
    };
}

pub(crate) fn delete_repo(url: &str) {
    let repo_path = get_repo_path(url, false);
    let path_vec = repo_path.split("/").collect::<Vec<&str>>();
    let names = path_vec.as_slice()[..path_vec.len() - 1].to_vec();
    let path = names.join("/");

    fs::remove_dir_all(&path).unwrap_or_else(|err| {
        println!("{}", err);
    });

    println!("Deleted {}", path);
}

pub(crate) async fn run_tools(url: &str) -> Result<(), Box<dyn Error>> {
    let tmp_path_str: String = get_repo_path(url, false);
    let tmp_path = Path::new(&tmp_path_str);
    let out_path_str: String = get_repo_path(url, true);

    let command = format!("rust-code-analysis-cli -m -p ./* -O json -o ../../../.{}", out_path_str);

    fs::create_dir_all(&out_path_str).unwrap();

    let output = Command::new("sh")
        .arg("-c")
        .arg(command)
        .current_dir(tmp_path)
        .output();

    output.await?;

    Ok(())
}