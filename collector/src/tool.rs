use std::{
    error::Error,
    fmt, fs,
    path::{Path, PathBuf},
};
use tokio::process::Command;

use crate::repo::Repo;

/// Enum containing all names of the used tools.
#[derive(PartialEq, Clone, Copy, Debug)]
pub enum ToolName {
    Rca,
    Node,
    Finder,
    Clippy,
}

impl fmt::Display for ToolName {
    /// Prints the `ToolName`.
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            ToolName::Rca => write!(f, "rca"),
            ToolName::Node => write!(f, "node"),
            ToolName::Finder => write!(f, "finder"),
            ToolName::Clippy => write!(f, "clippy"),
        }
    }
}

/// This struct represents a single tool with a name and a command.
pub struct Tool {
    pub name: ToolName,
    command: String,
}

/// Returns all tools used to collect metrics.
pub fn all_tools() -> Vec<Tool> {
    vec![
        Tool {
            name: ToolName::Rca,
            command: "rust-code-analysis-cli -m -p ./* -I '*.rs' -X '/target' --pr -O json -o "
                .to_string(),
        },
        Tool {
            name: ToolName::Node,
            command: "NODE_MODE=true rust-code-analysis-cli -m -p ./* -I '*.rs' -X '/target' --pr \
                      -O json -o "
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
            command: "cargo clippy --workspace --message-format=json | sed \
                      '1s/^/[/;$!s/$/,/;$s/$/]/' > "
                .to_string(),
        },
    ]
}

/// Returns all features of interest for the `Finder` tool.
pub fn all_features() -> Vec<&'static str> {
    vec![
        "lifetime",
        "for_lifetimes",
        "for_lifetimes_repeat1",
        "macro_definition",
        "macro_rule",
        "macro_rules!",
        "macro_definition_repeat1",
        "macro_invocation",
        "trait_bounds",
        "trait_bounds_repeat1",
        "higher_ranked_trait_bound",
        "removed_trait_bound",
        "where",
        "where_clause",
        "where_clause_repeat1",
        "where_predicate",
        "async",
        "async_block",
        "await",
        "await_expression",
        "unsafe",
        "unsafe_block",
        "trait",
        "trait_item",
        "closure_parameters_repeat1",
        "closure_expression",
        "closure_parameters",
        "line_comment",
    ]
}

impl Tool {
    /// Returns the output path of the tool in the `out` directory.
    pub fn get_cmd_out_path(&self, repo_out_path: &Path) -> PathBuf {
        let mut cmd_out_path = PathBuf::from("../../..");
        cmd_out_path.push(repo_out_path);

        if self.name == ToolName::Clippy {
            cmd_out_path.push(self.name.to_string());
            cmd_out_path.set_extension("json");
        }

        cmd_out_path
    }

    /// Runs this tool on the given repository and saves the outputs.
    pub async fn run<'a>(&mut self, repo: &Repo<'a>) -> Result<(), Box<dyn Error>> {
        let repo_out_path: PathBuf = Repo::get_path(repo.url, Some(&self.name), "out");
        let cmd_out_path = self.get_cmd_out_path(&repo_out_path);
        let cmd_out_path = cmd_out_path.to_str().unwrap();

        fs::create_dir_all(&repo_out_path).unwrap_or_else(|err| {
            eprintln!(
                "Could not create output folders {}: {}",
                repo_out_path.to_str().unwrap(),
                err
            );
        });

        let output = Command::new("sh")
            .arg("-c")
            .arg(format!("{}{}", self.command, cmd_out_path))
            .current_dir(&repo.tmp_path)
            .output()
            .await;

        match output {
            Ok(_) => Ok(()),
            Err(e) => Err(Box::new(e)),
        }
    }
}
