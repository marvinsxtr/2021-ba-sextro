use serde::{ser::SerializeStruct, Serialize, Serializer};
use serde_json::Value;

use crate::tool::ToolName;

#[derive(Debug)]
pub struct Finding<'a> {
    pub tool_name: ToolName,
    pub kind: String,
    pub name: String,
    pub start_line: u64,
    pub end_line: u64,
    pub data: Option<&'a Value>,
}

impl<'a> Finding<'a> {
    pub fn new(
        tool_name: ToolName,
        kind: String,
        name: String,
        start_line: u64,
        end_line: u64,
        data: Option<&'a Value>,
    ) -> Self {
        Self {
            tool_name,
            name,
            kind,
            start_line,
            end_line,
            data,
        }
    }
}

impl<'a> Serialize for Finding<'a> {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let data = &self.data.unwrap_or(&Value::Null);

        let mut s = serializer.serialize_struct("Finding", 5)?;
        s.serialize_field("kind", &self.kind)?;
        s.serialize_field("name", &self.name)?;
        s.serialize_field("start_line", &self.start_line)?;
        s.serialize_field("end_line", &self.end_line)?;
        s.serialize_field("data", data)?;
        s.end()
    }
}
