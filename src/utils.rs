use async_gitlib::RepoClone;
use std::{
    fs, 
    io, 
    io::Write, 
    process::Command, 
    path::Path, 
    env
};

fn get_repo_path(url: &str, last: usize) -> String {
    let path_vec = url.split("/").collect::<Vec<&str>>();
    let names = path_vec.as_slice()[path_vec.len() - last..].to_vec();
    let path_str = format!("./tmp/{}", names.join("/"));

    path_str
}

pub(crate) async fn clone_repo(url: &str) {
    println!("Cloning {} ...", url);

    let target = &get_repo_path(url, 2);

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
    let path = get_repo_path(url, 1);
    println!("Deleted {}", path);

    fs::remove_dir_all(&path).unwrap();
}

pub(crate) fn run_tools(url: &str) {
    let path_str: String = get_repo_path(url, 1).clone();
    let path = Path::new(&path_str);
    let current_dir = env::current_dir().unwrap();
    
    env::set_current_dir(&path).unwrap();
    
    let output = Command::new("sh")
            .arg("-c")
            .arg("echo Running process")
            .output()
            .expect("Failed to execute process");

    io::stdout().write_all(&output.stdout).unwrap();

    env::set_current_dir(current_dir).unwrap();
}