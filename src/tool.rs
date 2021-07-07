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

pub struct Tool {
    pub name: ToolName,
    command: String,
}

pub fn all_tools() -> Vec<Tool> {
    vec![
        Tool {
            name: ToolName::Rca,
            command: "rust-code-analysis-cli -m -p ./* -I '*.rs' -X '/target' --pr -O json -o "
                .to_string(),
        },
        Tool {
            name: ToolName::Finder,
            command: format!(
                "rust-code-analysis-cli -p ./* -I '*.rs' -X '/target' -f {} --pr -O json -o ",
                all_features().join(",")
            ),
        },
        Tool {
            name: ToolName::Clippy,
            command:
                "cargo clippy --workspace --message-format=json | sed '1s/^/[/;$!s/$/,/;$s/$/]/' > "
                    .to_string(),
        },
    ]
}

pub fn all_features() -> Vec<&'static str> {
    vec![
        "for_lifetimes",
        "for_lifetimes_repeat1",
        "lifetime",
        "reference_type",
        "reference_expression",
        "macro_definition",
        "variadic_parameter",
        "macro_rules!",
        "macro_rule",
        "macro_definition_repeat1",
        "macro_invocation",
        "where_clause",
        "where_predicate",
        "higher_ranked_trait_bound",
        "trait_bounds_repeat1",
        "removed_trait_bound",
        "where",
        "trait_bounds",
        "async_block",
        "await",
        "await_expression",
        "async",
        "unsafe_block",
        "unsafe",
        "line_comment",
    ]
}

impl Tool {
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
        let repo_out_path: &PathBuf = &repo.get_path(Some(&self.name), "out");
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
