use serde_json::Value;
use std::path::{Path, PathBuf};

use crate::{tool::ToolName, utils};

#[derive(Clone)]
pub struct OutFile {
    pub path: PathBuf,
    value: Value,
    tool_name: ToolName,
}

impl OutFile {
    pub fn new(path: PathBuf, tool_name: ToolName) -> Self {
        let value = utils::read_json_from_file(&path).unwrap_or_default();

        OutFile {
            path,
            value,
            tool_name,
        }
    }

    pub fn extract_metrics(&self) {
        println!("{}", self.tool_name);
    }
}

pub struct SrcFile<'a> {
    path: &'a Path,
    out_files: &'a Vec<OutFile>,
}

impl<'a> SrcFile<'a> {
    pub fn new(path: &'a Path, out_files: &'a Vec<OutFile>) -> Self {
        return Self { path, out_files };
    }

    pub fn print(&self) {
        println!("{:?}", &self.path.to_str().unwrap());

        println!("Collected output files:");
        for out_file in self.out_files {
            out_file.extract_metrics();
        }
    }
}
