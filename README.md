# Resume Generator

Reads semantical data from a directory of TOML files, render jinja templates into a single HTML page.

## Installation

### Requirements
- Make sure you have `uv` installed
- Clone project from Github
- sync `uv`

## Input data

Input data is a directory of toml files in the following architecture:
```
data
├── about.toml
├── languages.toml
├── skills.toml
├── training
│   ├── larue.toml
│   └── poudlard.toml
└── work
    ├── 2011 - Kitchen Aid.toml
    ├── 2018 - Scientific Diver.toml
    └── 2019 - Museum Thief.toml
```

## Configuration

Edit `settings.toml`

## Usage

Use `invoke` command runner.

`invoke --list` to see available commands.

Tasks are grouped into `data.*`, `html.*`, and `pdf.*` collections.

`invoke html.build` : build the HTML resume
`invoke pdf.build` : build the PDF resume
`invoke html.autobuild` : rebuild everytime something changes in the data directory, or the template directory.
`invoke html.serve` : autoreloading local web server of the resume