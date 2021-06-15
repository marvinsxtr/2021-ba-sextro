use serde_json::Value;
use std::path::Path;

use crate::{tool::ToolName, utils};

pub struct OutFile<'a> {
    value: Value,
    tool_name: &'a ToolName,
}

impl<'a> OutFile<'a> {
    pub fn new(path: &Path, tool_name: &'a ToolName) -> Self {
        let value = utils::read_json_from_file(path).unwrap_or_default();

        OutFile { value, tool_name }
    }

    pub fn extract_metrics(&self) {
        println!("{}{:?}", self.tool_name, self.value);
        todo!()
    }
}
