// command line arguments: 
// NAME: kroot
// SUMMARY: script for running python functions successively to begin with a document with a 'words' column with
//          orthographic forms, and produces an information theoretic analysis of the phonotactics of these words.
// INPUT ARGUMENTS: use command line arguments which produce the following values:
// args[0] - this file
// args[1] - python compiler, e.g. "~\\Python\\Python38-32\\python.exe"
// args[2] - folder which contains kroot.csv e.g. "~\\Chapters\\Minimal_Root\\it_data"
// args[3] - folder which contains py scripts, e.g. "~\\src\\py"
// HISTORY: Created 22-MAR-20 by Author. Refer to commits for further details.
use std::env;
use std::process;
use std::fs;

fn main() {
   let args: Vec<String> = env::args().collect();
   // confirm that there are three command line argument
    if args.len() != 4 {
        panic!("Wrong number of command line arguments!")
    }
    //create py_outputs dir if it does not exist
    let py_output_dir = args[2].to_string() + "\\py_outputs";
    fs::create_dir_all(&py_output_dir).expect("Error creating py_outputs directory!");

    //set relevant strings
    let orth_to_ipa_dir = args[3].to_string() + "\\orth_to_ipa.py";
    let kcomp_dir = args[3].to_string() + "\\produce_info_theory_docs.py";
    let seg_config_dir = args[3].to_string() + "\\produce_segmental_configurations_list.py";
    let test_dir = args[3].to_string() + "\\test.py";

    //run tests to check that script is working correctly
    let mut cmd_status = process::Command::new(&args[1])
    .args(&[&test_dir])
    .status()
    .expect("Python script could not be executed.");
    if !cmd_status.success() {
        println!("{:?}", cmd_status.code());
        panic!("python script test failed.")
    }
    //orth to ipa procedure
    let kroot_path = args[2].to_string() + "\\kroot.csv";
    let rule_path = args[2].to_string() + "\\rules.csv";

    cmd_status = process::Command::new(&args[1])
    .args(&[&orth_to_ipa_dir, &kroot_path, &rule_path])
    .status()
    .expect("Python script could not be executed.");
    if !cmd_status.success() {
        println!("{:?}", cmd_status.code());
        panic!("Python script did not exit with 0 status.")
    }
    // produce segmental configurations procedure
    let syl_dir = py_output_dir.to_string() + "\\phon_syls.txt";
    cmd_status = process::Command::new(&args[1])
    .args(&[&seg_config_dir, &syl_dir])
    .status()
    .expect("Python script could not be executed");
    if !cmd_status.success() {
        println!("{:?}", cmd_status.code());
        panic!("Python script did not exit with 0 status")
    }
    // finally, produce information theory docs. it takes phon_syls and phon_configs.txt as arguments
    let configs_dir = py_output_dir.to_string() + "\\phon_configs.txt";
    cmd_status = process::Command::new(&args[1])
    .args(&[&kcomp_dir, &syl_dir, &configs_dir])
    .status()
    .expect("Python script could not be executed");
    if !cmd_status.success() {
        println!("{:?}", cmd_status.code());
        panic!("Python script did not exit with 0 status")
    }
    println!("Doucments were produced successfully at {}", args[2]);
}