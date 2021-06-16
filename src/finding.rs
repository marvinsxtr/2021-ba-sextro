use serde_json::Value;

use crate::tool::ToolName;

#[derive(Debug)]
pub struct Finding<'a> {
    pub tool_name: ToolName,
    pub identifier: String,
    pub start_line: u64,
    pub end_line: u64,
    pub data: Option<&'a Value>,
}

impl<'a> Finding<'a> {
    pub fn new(
        tool_name: ToolName,
        identifier: String,
        start_line: u64,
        end_line: u64,
        data: Option<&'a Value>,
    ) -> Self {
        Self {
            tool_name,
            identifier,
            start_line,
            end_line,
            data,
        }
    }
}
