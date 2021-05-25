use std::{ fs, error::Error };
use async_gitlib::RepoClone;
use futures::StreamExt;
use tokio;

#[tokio::main]
pub(crate) async fn analyze(repos: Vec<&str>) -> Result<(), Box<dyn Error>> {
    let fetches = futures::stream::iter(
        repos.into_iter().map(|path| {
            async move {
                println!("Cloning {:?} ...", path);
                
                let path_vec: Vec<&str> = path.split("/").collect::<Vec<&str>>();
                let repo_name: &str = path_vec.last().unwrap();
                let target = format!("./tmp/{}", repo_name);

                let mut task = RepoClone::default();

                match task.clone(path, &target).await {
                    Err(_) => {
                        task.set_branch("main");
                        match task.clone(path, &target).await {
                            Err(_) => eprintln!("{}", format!("Skipped {}", repo_name)),
                            _ => ()
                        }
                    },
                    _ => ()
                };
            }
        })
    ).buffer_unordered(10).collect::<Vec<()>>();
    
    fetches.await;

    let path = "./tmp";
    fs::remove_dir_all(path).unwrap();
    fs::create_dir(path).unwrap();

    Ok(())
}
