use serde_json::Value;
use std::{error::Error, fs::File, io::BufReader, path::Path};

pub fn read_json_from_file<P: AsRef<Path>>(path: P) -> Result<Value, Box<dyn Error>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let v: Value = serde_json::from_reader(reader)?;

    Ok(v)
}
