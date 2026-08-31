// Draft CV template, mirrors the outline of templates/resume.html.jinja:
// header -> about -> links -> work -> training.
// Reads resume.json, produced by export.py from the same parse.py data.
// Not trimmed to one page yet.

#let data = json("resume.json")
#let about = data.about

#set document(title: about.name + " Resume", author: about.name)
#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set par(justify: true)

#let section-title(title) = block(above: 1em, below: 0.6em)[
  #text(size: 14pt, weight: "bold")[#title]
  #line(length: 100%, stroke: 0.5pt)
]

#let tag(body, color) = box(
  stroke: 1pt + color,
  radius: 1em,
  inset: (x: 0.5em, y: 0.25em),
)[#text(size: 8pt)[#body]]

#let tags(period) = {
  let items = (
    period.at("skills", default: ()).map(s => tag(s, aqua))
      + period.at("tech", default: ()).map(t => tag(t, purple))
  )
  if items.len() > 0 {
    block(above: 0.4em)[#items.join(h(0.4em))]
  }
}

#let timerange(period) = text(size: 10pt, fill: gray.darken(20%))[
  #period.at("delta", default: "") -- #period.at("year_span", default: "")
]

// ------------------------ HEADER ------------------------

#align(center)[
  #text(size: 22pt, weight: "bold")[#about.name]
  #v(0.2em)
  #text(size: 14pt)[#about.title]
]

// ------------------------ ABOUT ------------------------

#section-title("About me")
#about.intro

// ------------------------ LINKS ------------------------

#section-title("Links")
- Email: #link("mailto:" + about.email)[#about.email]
- Web: #link(about.web)[#about.web]
- Github: #link(about.github)[#about.github]
- Linkedin: #link(about.linkedin)[#about.linkedin]

// ------------------------ WORK ------------------------

#section-title("Work")

#for period in data.work.values().sorted(key: p => p.begin).rev() [
  #block(above: 1em, below: 0.6em)[
    #text(size: 12pt, weight: "bold")[#period.title]
    #v(0.1em)
    #grid(
      columns: (1fr, auto),
      text(size: 11pt, style: "italic")[#period.company, #period.location],
      timerange(period),
    )
    #v(0.3em)
    #period.description
    #tags(period)
  ]
  #line(length: 100%, stroke: 0.3pt + gray)
]

// ------------------------ TRAINING ------------------------

#section-title("Training")

#for period in data.training.values().sorted(key: p => p.begin).rev() [
  #block(above: 1em, below: 0.6em)[
    #text(size: 12pt, weight: "bold")[#period.path]
    #v(0.1em)
    #grid(
      columns: (1fr, auto),
      text(size: 11pt, style: "italic")[#period.institution],
      timerange(period),
    )
    #v(0.3em)
    #period.description
  ]
  #line(length: 100%, stroke: 0.3pt + gray)
]
