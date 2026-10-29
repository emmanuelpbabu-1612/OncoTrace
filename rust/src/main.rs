use std::collections::HashSet;
use std::env;
use std::error::Error;
use csv::ReaderBuilder;

fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: oncotrace_validator <path-to-csv>");
        std::process::exit(1);
    }
    let file_path = &args[1];

    let mut rdr = ReaderBuilder::new().from_path(file_path)?;
    let headers = rdr.headers()?.clone();

    // Map column indices dynamically
    let id_idx = headers.iter().position(|h| h == "patient_id")
        .ok_or("Schema Error: Missing patient_id")?;
    let os_months_idx = headers.iter().position(|h| h == "overall_survival_months")
        .ok_or("Schema Error: Missing overall_survival_months")?;
    let os_idx = headers.iter().position(|h| h == "overall_survival")
        .ok_or("Schema Error: Missing overall_survival")?;

    let mut seen_ids = HashSet::new();
    let mut errors = 0;

    for (i, result) in rdr.records().enumerate() {
        let record = result?;
        let row_num = i + 2; // +1 for 0-index, +1 for header

        // Rule 1: Patient ID must be present and globally unique
        let p_id = record.get(id_idx).unwrap_or("").trim();
        if p_id.is_empty() {
            eprintln!("Row {}: Missing patient_id", row_num);
            errors += 1;
        } else if !seen_ids.insert(p_id.to_string()) {
            eprintln!("Row {}: Duplicate patient_id '{}'", row_num, p_id);
            errors += 1;
        }

        // Rule 2: Survival time must be a valid float and non-negative
        let months_str = record.get(os_months_idx).unwrap_or("").trim();
        match months_str.parse::<f64>() {
            Ok(val) if val < 0.0 => {
                eprintln!("Row {}: Negative survival months '{}'", row_num, val);
                errors += 1;
            },
            Err(_) => {
                eprintln!("Row {}: Invalid survival months '{}'", row_num, months_str);
                errors += 1;
            },
            _ => {} // Valid and >= 0.0
        }

        // Rule 3: Survival indicator must be strictly binary representation
        let os_str = record.get(os_idx).unwrap_or("").trim();
        if os_str != "0" && os_str != "1" {
            eprintln!("Row {}: Invalid overall_survival '{}'. Must be '0' or '1'", row_num, os_str);
            errors += 1;
        }
    }

    if errors > 0 {
        eprintln!("Validation failed: {} errors found.", errors);
        std::process::exit(1);
    }

    println!("Validation passed: {} distinct records verified.", seen_ids.len());
    Ok(())
}
