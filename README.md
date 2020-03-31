# kroot_anonymous

## Description
Source code for kroot project. This code produces documents for an information theoretic analysis from Kaytetye orthographic word forms.

## Installation
Compile by running **cargo build** at the project directory.

## Usage
An example usage of the command line argument format
```bash
C:\\kroot\\kroot.exe C:\\py3\\python.exe C:\foo\bar\output C:\\kroot\src\py
```

## Project Structure and Summary of Scripts
src\main.rs **Calls python functions in this project.**

src\py\orth_to_ipa.py **Receives a set of Kaytetye orthographic word forms and produces IPA form (\phon.txt) and IPA syllabified forms (\phon_syl.txt).**

src\py\produce_segmental_configurations_list.py **Produces a list of all possible segmental configurations in each syllable position (onset, nucleus, coda).**

src\py\get_configurations.py **Contains the get_configurations function for produce_segmental_configurations_list.py. This function was isolated to allow for easy testing.**

src\py\produce_info_theory_docs.py **Takes syllabified phonological forms and produces various documents relating to surprisals and entropy for each phonotactic position.**

src\py\info_theory_functions.py **Functions for produce_info_theory_docs.py.**

src\py\lex_io.py **Document reading and writing functions for produce_info_theory_docs.py.**

src\py\test.py **Test document.**

src\r\produce_entropy_plots.r **Produces plots and tables for information theory analysis.**

## License
[MIT](https://choosealicense.com/licenses/mit/). Relevant attributions are stated in the source files.
