use futures::StreamExt;
use std::error::Error;
use url::Url;

use crate::{repo::Repo, Cli};

#[tokio::main]
pub(crate) async fn analyze(repos: Vec<&str>, args: &Cli) -> Result<(), Box<dyn Error>> {
    let repo_jobs = futures::stream::iter(repos.into_iter().map(|url| async move {
        let url = Url::parse(url).unwrap_or_else(|err| {
            eprintln!("Could not parse url {}: {}", url, err);
            panic!();
        });

        let repo = Repo::new(&url);

        if args.clone {
            println!("Cloning {}", repo.url);
            repo.clone().await;
        }
        if args.metrics {
            println!("Collecting metrics on {}", repo.url);
            repo.metrics().await;
        }
        if args.filter {
            println!("Filtering metrics on {}", repo.url);
            repo.filter().await;
        }
        if args.analyze {
            println!("Analyzing metrics on {}", repo.url);
            repo.analyze().await;
        }
        if args.delete {
            println!("Deleting tmp of {}", repo.url);
            repo.delete();
        }
    }))
    .buffer_unordered(8)
    .collect::<Vec<()>>();

    repo_jobs.await;

    Ok(())
}
