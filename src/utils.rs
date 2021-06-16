use serde_json::{Map, Value};
use std::{error::Error, fs::File, io::BufReader, path::Path};
use walkdir::WalkDir;

pub fn read_json_from_file<P: AsRef<Path>>(path: P) -> Result<Value, Box<dyn Error>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let v: Value = serde_json::from_reader(reader)?;

    Ok(v)
}

pub fn get_rust_files(path: &Path) -> Vec<String> {
    WalkDir::new(path)
        .follow_links(false)
        .into_iter()
        .filter(|e| {
            let e = e.as_ref().unwrap();
            let file_name = e.file_name().to_string_lossy();
            let path = e.path().to_str().unwrap();

            file_name.ends_with(".rs") && !path.contains("/target/")
        })
        .map(|e| e.unwrap().path().to_owned())
        .map(|e| e.to_string_lossy().to_string())
        .collect()
}

pub fn get_spaces(value: &Value) -> Vec<&Map<String, Value>> {
    let mut result = Vec::new();
    let mut spaces = Vec::new();

    let first_space = value.as_object().unwrap();

    spaces.push(first_space);

    while !spaces.is_empty() {
        let space = spaces.pop().unwrap();

        result.push(space);

        let new_spaces = space["spaces"].as_array().unwrap();

        for new_space in new_spaces {
            let new_space = new_space.as_object().unwrap();
            spaces.push(new_space);
        }
    }

    result
}
