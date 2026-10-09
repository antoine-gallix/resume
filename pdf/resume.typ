#let data = json("resume.json")
#let about = data.about

#set document(title: about.name + " Resume", author: about.name)
#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt, font: "Carlito")
#set par(justify: true)

#let generic-title(title, space: 0, size: 1em) = block(above: space, below: space)[
  #text(size: size, weight: "bold", title)
]
#let section-title(title) = generic-title(title, space: 1.5em, size: 14pt)

#let subsection-title(title) = generic-title(title, space: .5em, size: 12pt)

#show line: set align(center)

#let separator(length: 100%, stroke: .5pt, space: 1.5em) = block(
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

#(
  data
    .work
    .values()
    .sorted(key: p => p.begin)
    .rev()
    .map(period => block(above: 1em, below: 0.6em, breakable: false)[
      #subsection-title[#period.title]
      #v(0.1em)
      #grid(
        columns: (1fr, auto),
        text(size: 11pt)[#period.company, #period.location], timerange(period),
      )
      #v(0.3em)
      #period.description
      #tags(period)
    ])
    .join(subsection-separator)
)

// ------------------------ TRAINING ------------------------
#section-separator
#section-title("Training")

#(
  data
    .training
    .values()
    .sorted(key: p => p.begin)
    .rev()
    .map(period => block(above: 1em, below: 0.6em)[
      #subsection-title(period.institution)
      #grid(
        columns: (1fr, auto),
        text(size: 11pt, style: "italic")[#period.path], timerange(period),
      )
      #v(0.1em)
      #period.description
    ])
    .join(subsection-separator)
)
// ------------------------ LANGUAGES ------------------------
#section-separator
#section-title("Languages")
#grid(
  columns: (1fr, 1fr, 1fr), row-gutter: 0.6em,
  ..data.languages.pairs().map(pair => pair.join(" : "))
)
