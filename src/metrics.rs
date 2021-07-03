use serde_json::{Map, Value};
use std::ops::AddAssign;

#[derive(Debug, Default, Copy, Clone)]
pub struct Metrics {
    n: f64,
    nargs: f64,
    nexits: f64,
    cognitive: f64,
    cyclomatic: f64,
    halstead_n1: f64,
    halstead_capital_n1: f64,
    halstead_n2: f64,
    halstead_capital_n2: f64,
    halstead_length: f64,
    halstead_estimated_program_length: f64,
    halstead_purity_ratio: f64,
    halstead_vocabulary: f64,
    halstead_volume: f64,
    halstead_difficulty: f64,
    halstead_level: f64,
    halstead_effort: f64,
    halstead_time: f64,
    halstead_bugs: f64,
    sloc: f64,
    ploc: f64,
    lloc: f64,
    cloc: f64,
    blank: f64,
    functions: f64,
    closures: f64,
    mi_original: f64,
    mi_sei: f64,
    mi_visual_studio: f64,
}

impl Metrics {
    fn get_metric(metrics: &Map<String, Value>, key1: &str, key2: &str) -> f64 {
        metrics[key1].as_object().unwrap()[key2]
            .as_f64()
            .unwrap_or_default()
    }

    pub fn from_value(value: &Value) -> Self {
        let metrics = value.as_object().unwrap();
        Metrics {
            n: 0.0,
            nargs: Self::get_metric(metrics, "nargs", "sum"),
            nexits: Self::get_metric(metrics, "nexits", "sum"),
            cognitive: Self::get_metric(metrics, "cognitive", "sum"),
            cyclomatic: Self::get_metric(metrics, "cyclomatic", "sum"),
            halstead_n1: Self::get_metric(metrics, "halstead", "n1"),
            halstead_capital_n1: Self::get_metric(metrics, "halstead", "N1"),
            halstead_n2: Self::get_metric(metrics, "halstead", "n2"),
            halstead_capital_n2: Self::get_metric(metrics, "halstead", "N2"),
            halstead_length: Self::get_metric(metrics, "halstead", "length"),
            halstead_estimated_program_length: Self::get_metric(
                metrics,
                "halstead",
                "estimated_program_length",
            ),
            halstead_purity_ratio: Self::get_metric(metrics, "halstead", "purity_ratio"),
            halstead_vocabulary: Self::get_metric(metrics, "halstead", "vocabulary"),
            halstead_volume: Self::get_metric(metrics, "halstead", "volume"),
            halstead_difficulty: Self::get_metric(metrics, "halstead", "difficulty"),
            halstead_level: Self::get_metric(metrics, "halstead", "level"),
            halstead_effort: Self::get_metric(metrics, "halstead", "effort"),
            halstead_time: Self::get_metric(metrics, "halstead", "time"),
            halstead_bugs: Self::get_metric(metrics, "halstead", "bugs"),
            sloc: Self::get_metric(metrics, "loc", "sloc"),
            ploc: Self::get_metric(metrics, "loc", "ploc"),
            lloc: Self::get_metric(metrics, "loc", "lloc"),
            cloc: Self::get_metric(metrics, "loc", "cloc"),
            blank: Self::get_metric(metrics, "loc", "blank"),
            functions: Self::get_metric(metrics, "nom", "functions"),
            closures: Self::get_metric(metrics, "nom", "closures"),
            mi_original: Self::get_metric(metrics, "mi", "mi_original"),
            mi_sei: Self::get_metric(metrics, "mi", "mi_sei"),
            mi_visual_studio: Self::get_metric(metrics, "mi", "mi_visual_studio"),
        }
    }

    pub fn avg(&self) -> Self {
        Metrics {
            n: 0.,
            nargs: self.nargs / self.n,
            nexits: self.nexits / self.n,
            cognitive: self.cognitive / self.n,
            cyclomatic: self.cyclomatic / self.n,
            halstead_n1: self.halstead_n1 / self.n,
            halstead_capital_n1: self.halstead_capital_n1 / self.n,
            halstead_n2: self.halstead_n2 / self.n,
            halstead_capital_n2: self.halstead_capital_n2 / self.n,
            halstead_length: self.halstead_length / self.n,
            halstead_estimated_program_length: self.halstead_estimated_program_length / self.n,
            halstead_purity_ratio: self.halstead_purity_ratio / self.n,
            halstead_vocabulary: self.halstead_vocabulary / self.n,
            halstead_volume: self.halstead_volume / self.n,
            halstead_difficulty: self.halstead_difficulty / self.n,
            halstead_level: self.halstead_level / self.n,
            halstead_effort: self.halstead_effort / self.n,
            halstead_time: self.halstead_time / self.n,
            halstead_bugs: self.halstead_bugs / self.n,
            sloc: self.sloc / self.n,
            ploc: self.ploc / self.n,
            lloc: self.lloc / self.n,
            cloc: self.cloc / self.n,
            blank: self.blank / self.n,
            functions: self.functions / self.n,
            closures: self.closures / self.n,
            mi_original: self.mi_original / self.n,
            mi_sei: self.mi_sei / self.n,
            mi_visual_studio: self.mi_visual_studio / self.n,
        }
    }

    pub fn weigh(&self, weight: f64) -> Self {
        Metrics {
            n: self.n,
            nargs: self.nargs,
            nexits: self.nexits,
            cognitive: self.cognitive * weight,
            cyclomatic: self.cyclomatic * weight,
            halstead_n1: self.halstead_n1 * weight,
            halstead_capital_n1: self.halstead_capital_n1 * weight,
            halstead_n2: self.halstead_n2 * weight,
            halstead_capital_n2: self.halstead_capital_n2 * weight,
            halstead_length: self.halstead_length * weight,
            halstead_estimated_program_length: self.halstead_estimated_program_length * weight,
            halstead_purity_ratio: self.halstead_purity_ratio * weight,
            halstead_vocabulary: self.halstead_vocabulary * weight,
            halstead_volume: self.halstead_volume * weight,
            halstead_difficulty: self.halstead_difficulty * weight,
            halstead_level: self.halstead_level * weight,
            halstead_effort: self.halstead_effort * weight,
            halstead_time: self.halstead_time * weight,
            halstead_bugs: self.halstead_bugs * weight,
            sloc: self.sloc,
            ploc: self.ploc,
            lloc: self.lloc,
            cloc: self.cloc,
            blank: self.blank,
            functions: self.functions,
            closures: self.closures,
            mi_original: self.mi_original * weight,
            mi_sei: self.mi_sei * weight,
            mi_visual_studio: self.mi_visual_studio * weight,
        }
    }
}

impl AddAssign for Metrics {
    fn add_assign(&mut self, other: Self) {
        self.n += 1.0;
        self.nargs += other.nargs;
        self.nexits += other.nexits;
        self.cognitive += other.cognitive;
        self.cyclomatic += other.cyclomatic;
        self.halstead_n1 += other.halstead_n1;
        self.halstead_capital_n1 += other.halstead_capital_n1;
        self.halstead_n2 += other.halstead_n2;
        self.halstead_capital_n2 += other.halstead_capital_n2;
        self.halstead_length += other.halstead_length;
        self.halstead_estimated_program_length += other.halstead_estimated_program_length;
        self.halstead_purity_ratio += other.halstead_purity_ratio;
        self.halstead_vocabulary += other.halstead_vocabulary;
        self.halstead_volume += other.halstead_volume;
        self.halstead_difficulty += other.halstead_difficulty;
        self.halstead_level += other.halstead_level;
        self.halstead_effort += other.halstead_effort;
        self.halstead_time += other.halstead_time;
        self.halstead_bugs += other.halstead_bugs;
        self.sloc += other.sloc;
        self.ploc += other.ploc;
        self.lloc += other.lloc;
        self.cloc += other.cloc;
        self.blank += other.blank;
        self.functions += other.functions;
        self.closures += other.closures;
        self.mi_original += other.mi_original;
        self.mi_sei += other.mi_sei;
        self.mi_visual_studio += other.mi_visual_studio;
    }
}
