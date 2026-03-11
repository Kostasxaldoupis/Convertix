# Convertix

A lightweight Python tool for converting files between multiple formats using either a **Command Line Interface (CLI)** or a **Graphical User Interface (GUI)**.

## Features

* Convert images (PNG, JPG)
* Convert images to PDF
* Convert CSV to JSON
* Simple CLI interface
* Clean Tkinter GUI
* Easy to extend with new converters

## Installation

Clone the repository:

```
git clone https://github.com/Kostasxaldoupis/Convertix.git
cd Convertix
```

Install dependencies:

```
pip install -r requirements.txt
```

## CLI Usage

Run conversions directly from the terminal:

```
python cli.py input_file output_file
```

Example:

```
python cli.py image.png image.jpg
python cli.py image.jpg image.pdf
python cli.py data.csv data.json
```

## GUI Usage

Launch the graphical interface:

```
python gui.py
```

Then select an input file and choose an output format.

## Project Structure

```
Convertix
│
├── cli.py
├── gui.py
├── README.md
├── requirements.txt
│
└── converters
    ├── image_converter.py
    ├── pdf_converter.py
    └── data_converter.py
```

## Future Improvements

* Drag and drop file support
* More file format conversions
* Dark mode GUI
* Batch file conversions

## License

This project is licensed under the MIT License.
