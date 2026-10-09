#let data = json("resume.json")
#let about = data.about

#set document(title: about.name + " Resume", author: about.name)
#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set par(justify: true)

#let section-title(title) = block(above: 1em, below: 0.6em)[
  #text(size: 14pt, weight: "bold")[#title]
]
#show line: set align(center)

#let separator(length: 100%, stroke: .5pt, space: 1em) = block(
  above: space,
  below: space,
  width: 100%,
  line(length: length, stroke: stroke),
)

#let section-separator = separator()
#let subsection-separator = separator(length: 60%, stroke: .5pt + gray)


#let tag(body) = box()[#text(size: 8pt)[#body]]

#let tags(period) = {
  let items = (
    period.at("skills", default: ()).map(s => tag(s)) + period.at("tech", default: ()).map(t => tag(t))
  )
  if items.len() > 0 {
    // block(above: 0.4em, width: 100%, align(center, items.join(h(0.8em))))
    block(above: 1em, items.join(h(0.8em)))
  }
}

#let timerange(period) = text(size: 10pt, fill: gray.darken(80%))[
  #period.at("delta", default: "") -- #period.at("year_span", default: "")
]

// ------------------------ HEADER ------------------------

#align(center)[#grid(
    rows: (auto, auto),
    inset: 5pt,
    text(size: 25pt, weight: "bold")[#about.name],
    text(size: 15pt)[#about.title],
  )

]

// ------------------------ ABOUT ------------------------

#section-title("About me")
#about.intro

// ------------------------ LINKS ------------------------
#section-separator
#section-title("Links")
#grid(
  rows: (auto, auto),
  columns: (1fr, 1fr),
  inset: 3pt,
  text[Email: #link("mailto:" + about.email)[#about.email]], text[Web: #link(about.web)[#about.web]],
  text[Github: #link(about.github)[#about.github]], text[Linkedin: #link(about.linkedin)[#about.linkedin]],
)

// ------------------------ WORK ------------------------

#section-separator
#section-title("Work")

#data.work.values().sorted(key: p => p.begin).rev().map(period => block(above: 1em, below: 0.6em, breakable: false)[
    #text(size: 12pt, weight: "bold")[#period.title]
    #v(0.1em)
    #grid(
      columns: (1fr, auto),
      text(size: 11pt)[#period.company, #period.location], timerange(period),
    )
    #v(0.3em)
    #period.description
    #tags(period)
  ]).join(subsection-separator)

// ------------------------ TRAINING ------------------------
#section-separator
#section-title("Training")

#data.training.values().sorted(key: p => p.begin).rev().map(period => block(above: 1em, below: 0.6em)[
    #text(size: 12pt, weight: "bold")[#period.institution]
    #v(0.1em)
    #grid(
      columns: (1fr, auto),
      text(size: 11pt, style: "italic")[#period.path], timerange(period),
    )
    #v(0.1em)
    #period.description
  ]).join(subsection-separator)
