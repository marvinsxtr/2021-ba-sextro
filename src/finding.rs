use serde::{ser::SerializeStruct, Serialize, Serializer};
use serde_json::Value;

use crate::{metrics::Metrics, tool::ToolName};

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

    pub fn get_metrics(&self) -> Option<Metrics> {
        self.data.map(|value| Metrics::from_value(&value))
    }

    pub fn is_inside(&self, other: &Self) -> bool {
        self.start_line >= other.start_line && self.end_line <= other.end_line
    }

    pub fn get_size_ratio(&self, other: &Self) -> f64 {
        let size_this: f64 = (self.end_line - self.start_line + 1) as f64;
        let size_other: f64 = (other.end_line - other.start_line + 1) as f64;
        size_this / size_other
    }
}

impl<'a> Serialize for Finding<'a> {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let data = &self.data.unwrap_or(&Value::Null);
        let mut s = serializer.serialize_struct("Finding", 5)?;
        s.serialize_field("tool", &self.tool_name.to_string())?;
        s.serialize_field("identifier", &self.identifier)?;
        s.serialize_field("start_line", &self.start_line)?;
        s.serialize_field("end_line", &self.end_line)?;
        s.serialize_field("data", data)?;
        s.end()
    }
}
