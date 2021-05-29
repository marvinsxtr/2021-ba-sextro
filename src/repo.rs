use async_gitlib::RepoClone;
use std::fs;

pub struct Repo<'a> {
    pub url: &'a str,
    pub path: String,
}

impl<'a> Repo<'a> {
    pub fn new(url: &'a str) -> Self {
        let path = Self::get_tmp_path(url);
        Self { url, path }
    }

    pub fn get_tmp_path(url: &str) -> String {
        let path_vec = url.split('/').collect::<Vec<&str>>();
        let names = path_vec.as_slice()[path_vec.len() - 2..].to_vec();
        let name = names.join("/");

        format!("./data/tmp/{}", name)
    }

    pub async fn clone(&self) {
        println!("Cloning {} ...", self.url);

        let mut task = RepoClone::default();

        if task.clone(self.url, &self.path).await.is_err() {
            task.set_branch("main");
            task.clone(self.url, &self.path)
                .await
                .unwrap_or_else(|err| {
                    eprintln!("Skipped {}: {}", self.path, err.message());
                });
        }
    }

    pub async fn analyze(&self) {
        for tool in crate::tool::all() {
            tool.run(self).await.unwrap_or_else(|err| {
                eprintln!("Failed to run tool {} on {}: {}", tool.name, self.url, err);
            });
        }
    }

    pub fn delete(&self) {
        let path_vec = self.path.split('/').collect::<Vec<&str>>();
        let names = path_vec.as_slice()[..path_vec.len() - 1].to_vec();
        let path = names.join("/");

        fs::remove_dir_all(&path).unwrap_or_else(|err| {
            eprintln!("{}", err);
        });

        println!("Deleted {}", path);
    }
}
