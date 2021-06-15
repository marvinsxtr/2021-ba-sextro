use async_gitlib::RepoClone;
use std::{fs, path::PathBuf};
use url::Url;

use crate::{file::OutFile, tool::ToolName};

pub struct Repo<'a> {
    pub url: &'a Url,
    pub tmp_path: String,
}

impl<'a> Repo<'a> {
    pub fn new(url: &'a Url) -> Self {
        let tmp_path = Self::get_tmp_path(url);
        Self { url, tmp_path }
    }

    pub fn get_tmp_path(url: &Url) -> String {
        let repo_name = url.path().strip_prefix("/").unwrap();
        let mut tmp_path = PathBuf::from("./data/tmp");

        tmp_path.push(repo_name);
        tmp_path.to_str().unwrap().to_string()
    }

    pub fn get_out_path(&self, tool_name: &ToolName) -> PathBuf {
        let repo_name = self.url.path().strip_prefix("/").unwrap();
        let mut out_path = PathBuf::from("./data/out");

        out_path.push(tool_name.to_string());
        out_path.push(repo_name);
        out_path
    }

    pub async fn clone(&self) {
        println!("Cloning {} ...", self.url);

        let mut task = RepoClone::default();

        if task.clone(self.url.as_str(), &self.tmp_path).await.is_err() {
            task.set_branch("main");
            task.clone(self.url.as_str(), &self.tmp_path)
                .await
                .unwrap_or_else(|err| {
                    eprintln!("Skipped {}: {}", self.tmp_path, err.message());
                });
        }
    }

    pub async fn metrics(&self) {
        for mut tool in crate::tool::all() {
            tool.run(self).await.unwrap_or_else(|err| {
                eprintln!("Failed to run tool {} on {}: {}", tool.name, self.url, err);
            });
        }
    }

    pub async fn analyze(&self) {
        for tool in crate::tool::all() {
            let out_path = &self.get_out_path(&tool.name);
            let paths = fs::read_dir(&out_path).unwrap();

            for path in paths {
                let path = path.unwrap().path();
                let file = OutFile::new(&path, &tool.name);

                file.extract_metrics();
            }
        }
    }

    pub fn delete(&self) {
        let mut tmp_path = PathBuf::from(&self.tmp_path);
        tmp_path.pop();

        let tmp_path = tmp_path.to_str().unwrap();

        fs::remove_dir_all(&tmp_path).unwrap_or_else(|err| {
            eprintln!("Failed to delete tmp folder {}: {}", tmp_path, err);
        });

        println!("Deleted {}", tmp_path);
    }
}
