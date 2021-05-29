use futures::StreamExt;
use std::error::Error;

use crate::repo::Repo;

#[tokio::main]
pub(crate) async fn analyze(repos: Vec<&str>) -> Result<(), Box<dyn Error>> {
    let repo_jobs = futures::stream::iter(repos.into_iter().map(|url| async move {
        let repo = Repo::new(url);

        repo.clone().await;
        repo.analyze().await;
        repo.delete();
    }))
    .buffer_unordered(8)
    .collect::<Vec<()>>();

    repo_jobs.await;

    Ok(())
}
