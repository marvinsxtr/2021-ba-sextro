use futures::TryFutureExt;
use std::{
    error::Error,
    fmt, fs,
    path::{Path, PathBuf},
};
use tokio::process::Command;

use crate::repo::Repo;

#[derive(PartialEq, Clone, Copy, Debug)]
pub enum ToolName {
    Rca,
    Finder,
    Clippy,
}

impl fmt::Display for ToolName {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            ToolName::Rca => write!(f, "rca"),
            ToolName::Finder => write!(f, "finder"),
            ToolName::Clippy => write!(f, "clippy"),
        }
    }
}

pub struct Tool<'a> {
    pub name: ToolName,
    command: &'a str,
}

pub fn all() -> Vec<Tool<'static>> {
    vec![
        Tool {
            name: ToolName::Rca,
            command: "rust-code-analysis-cli -m -p ./* -I '*.rs' -X '/target' --pr -O json -o ",
        },
        Tool {
            name: ToolName::Finder,
            command:
                "rust-code-analysis-cli -p ./* -I '*.rs' -X '/target' -f macro_definition --pr -O json -o ",
        },
        Tool {
            name: ToolName::Clippy,
            command:
                "cargo clippy --workspace --message-format=json | sed '1s/^/[/;$!s/$/,/;$s/$/]/' > ",
        },
    ]
}

impl<'a> Tool<'a> {
    pub fn get_cmd_out_path(&self, repo_out_path: &Path) -> PathBuf {
        let mut cmd_out_path = PathBuf::from("../../../..");
        cmd_out_path.push(repo_out_path);

        if self.name == ToolName::Clippy {
            cmd_out_path.push(self.name.to_string());
            cmd_out_path.set_extension("json");
        }

        cmd_out_path
    }

    pub async fn run(&mut self, repo: &Repo<'_>) -> Result<(), Box<dyn Error>> {
        let repo_out_path: &PathBuf = &repo.get_out_path(&self.name);
        let cmd_out_path = self.get_cmd_out_path(repo_out_path);
        let cmd_out_path = cmd_out_path.to_str().unwrap();

        fs::create_dir_all(&repo_out_path).unwrap_or_else(|err| {
            eprintln!(
                "Could not create output folders {}: {}",
                repo_out_path.to_str().unwrap(),
                err
            );
        });

        Command::new("sh")
            .arg("-c")
            .arg(format!("{}{}", self.command, cmd_out_path))
            .current_dir(&repo.tmp_path)
            .output()
            .unwrap_or_else(|err| {
                eprintln!("Could not run command: {}", err);
                panic!();
            })
            .await;

        Ok(())
    }
}
