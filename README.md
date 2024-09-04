# gINT-Extract

A command-line tool to extract gint files to a csv's and sqlite.

## Installation

Install the correct access driver:

gINT databases are in the 1997 Microsoft Access format, so the correct driver has to be downloaded.
As of 2024-09-03 the driver is no longer available in the normal channels.
But the [way back machine](https://web.archive.org/) has it.
Navigate to the [way back machine](https://web.archive.org/) and search through the history for this: "<http://www.microsoft.com/en-us/download/details.aspx?id=13255>".
Download and install the appropriate one for your machine.

Install the tool:

pip install git+<https://github.com/konnerhorton/gint-extract.git>

## Usage

```bash
gint-extract <file_path> [--dir <output_directory>] [--format <output_format>]
```

Defaults:

```bash
gint-extract <file_path> --dir csv --format csv
```

## Functionality

- Load a gint database
- Export to csv's in a specified directory

## TODO

- [ ] finish writing tests
- [ ] Output summary of the database
- [ ] make sure the methods to write to sqlite are correct
