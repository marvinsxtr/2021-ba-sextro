use futures::StreamExt;
use std::error::Error;

#[tokio::main]
pub(crate) async fn analyze(repos: Vec<&str>) -> Result<(), Box<dyn Error>> {
    let repo_jobs = futures::stream::iter(repos.into_iter().map(|url| async move {
        analyze_repo(url).await;
    }))
    .buffer_unordered(8)
    .collect::<Vec<()>>();

    repo_jobs.await;

    Ok(())
}

async fn analyze_repo(url: &str) {
    crate::utils::clone_repo(url).await;
    crate::utils::run_tools(url).await.unwrap();
    crate::utils::delete_repo(url);
}
