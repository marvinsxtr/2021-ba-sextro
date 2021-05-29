use std::{error::Error, fs};
use tokio::process::Command;

use crate::repo::Repo;

pub struct Tool<'a> {
    name: &'a str,
    cmd: &'a str
}

pub fn all() -> Vec<Tool<'static>> {
    vec![
        Tool {
            name: "rca", 
            cmd: "rust-code-analysis-cli -m -p ./* -I '*.rs' -O json -o ../../../."
        },
        Tool {
            name: "finder",
            cmd: "rust-code-analysis-cli -p ./* -f macro | sed 's/[[:cntrl:]]\\[[0-9]{1,3}m//g' >> ../../../."
        },
        Tool {
            name: "clippy",
            cmd: "cargo clippy --workspace --message-format=json >> ../../../.",
        },
    ]
}

impl<'a> Tool<'a> {
    pub fn get_out_path(&self, repo: &Repo<'_>) -> String{
        let path_vec = repo.url.split('/').collect::<Vec<&str>>();
        let names = path_vec.as_slice()[path_vec.len() - 2..].to_vec();
        let name = names.join("/");

        format!("./data/out/{}/{}", self.name, name)
    }

    pub async fn run(&self, repo: &Repo<'_>) -> Result<(), Box<dyn Error>> {
        let out_path: String = self.get_out_path(repo);

        let command = if self.name == "clippy" {
            format!("{}{}/clippy.json", self.cmd, out_path)
        } else if self.name == "rca" {
            format!("{}{}", self.cmd, out_path)
        } else {
            format!("{}{}/finder.txt", self.cmd, out_path)
        };

        fs::create_dir_all(&out_path).unwrap();

        let output = Command::new("sh")
            .arg("-c")
            .arg(command)
            .current_dir(&repo.path)
            .output();

        output.await?;

        Ok(())
    }
}