#!/bin/bash
# seed.sh — Bootstrap Eleventy research knowledge base

set -e

echo "Creating project structure..."

mkdir -p \
human \
figures \
ontology \
scripts \
site/_data \
site/notes \
site/gene \
site/paper \
site/graph \
.github/workflows

########################################
# Example notes
########################################

cat <<'EOF' > human/2025-01_runx2.md
# RUNX2 enhancer activation

PMID: 38123456

RUNX2 interacts with DNMT3A.

Genes
- RUNX2
- DNMT3A
- TET2

![model](../figures/runx2_model.png)
EOF

cat <<'EOF' > human/2025-02_cnv_chipseq.md
# CNV HICHIP Notes

PMID: 37455321

CNV affects regulatory regions.

Genes
- HIC1
- RUNX2
EOF

touch figures/runx2_model.png

########################################
# Ontology seed
########################################

cat <<EOF > ontology/triples.tsv
subject	predicate	object	source
RUNX2	relates_to	HIC1	PMID37455321
EOF

########################################
# Empty data placeholders
########################################

echo '{}' > site/_data/gene_mentions.json
echo '{}' > site/_data/paper_mentions.json

########################################
# Notes index
########################################

cat <<'EOF' > site/notes/index.njk
<h1>Reading Notes</h1>

<ul>
{% for note in collections.notes %}
<li><a href="{{ note.url }}">{{ note.fileSlug }}</a></li>
{% endfor %}
</ul>
EOF

########################################
# Graph placeholder
########################################

cat <<'EOF' > site/graph/index.njk
<h1>Knowledge Graph</h1>
<div id="graph"></div>
<script src="/graph/graph.js"></script>
EOF

cat <<'EOF' > site/graph/graph.js
console.log("Graph placeholder");
EOF

########################################
# Placeholder scripts
########################################

touch scripts/extract_pmid.py
touch scripts/build_graph.py

########################################
# Eleventy configuration
########################################

cat <<'EOF' > .eleventy.js
const fs = require("fs");

module.exports = function(eleventyConfig) {

  eleventyConfig.addPassthroughCopy("figures");

  eleventyConfig.addCollection("notes", function(collectionApi) {
    return collectionApi.getFilteredByGlob("human/*.md");
  });

  function extractMentions() {

    const geneMentions = {};
    const paperMentions = {};

    if (!fs.existsSync("human")) return;

    const notes = fs.readdirSync("human").filter(f => f.endsWith(".md"));

    for (const note of notes) {

      const text = fs.readFileSync("human/" + note, "utf8");

      const pmids = [...text.matchAll(/PMID:\s*([0-9]+)/g)]
        .map(m => m[1]);

      const genes = [...new Set(
        [...text.matchAll(/\b[A-Z][A-Z0-9]{2,9}\b/g)]
        .map(m => m[0])
      )].filter(g => !["PMID","CNV","DNA","RNA"].includes(g));

      for (const g of genes) {

        if (!geneMentions[g]) geneMentions[g] = [];

        geneMentions[g].push(note);

        geneMentions[g] = [...new Set(geneMentions[g])];

      }

      for (const p of pmids) {

        if (!paperMentions[p]) paperMentions[p] = [];

        paperMentions[p].push(note);

        paperMentions[p] = [...new Set(paperMentions[p])];

      }

    }

    fs.writeFileSync(
      "site/_data/gene_mentions.json",
      JSON.stringify(geneMentions,null,2)
    );

    fs.writeFileSync(
      "site/_data/paper_mentions.json",
      JSON.stringify(paperMentions,null,2)
    );

  }

  extractMentions();

  return {
    dir: {
      input: "site",
      output: "docs"
    }
  };

};
EOF

########################################
# Gene template
########################################

cat <<'EOF' > site/gene/gene.njk
---
pagination:
  data: gene_mentions
  size: 1
  alias: gene
permalink: "{% if gene.key %}/gene/{{ gene.key | slug }}/{% else %}false{% endif %}"
---

<h1>{{ gene.key }}</h1>

<h2>Appears in notes</h2>

<ul>
{% for note in gene.value %}
<li>
<a href="/notes/{{ note | slug }}/">{{ note }}</a>
</li>
{% endfor %}
</ul>
EOF

########################################
# Paper template
########################################

cat <<'EOF' > site/paper/paper.njk
---
pagination:
  data: paper_mentions
  size: 1
  alias: paper
permalink: "{% if paper.key %}/paper/{{ paper.key }}/{% else %}false{% endif %}"
---

<h1>PMID {{ paper.key }}</h1>

<h2>Appears in notes</h2>

<ul>
{% for note in paper.value %}
<li>
<a href="/notes/{{ note | slug }}/">{{ note }}</a>
</li>
{% endfor %}
</ul>
EOF

########################################
# package.json
########################################

cat <<'EOF' > package.json
{
  "name": "reading-knowledge",
  "version": "1.0.0",
  "scripts": {
    "start": "npx @11ty/eleventy --serve",
    "build": "npx @11ty/eleventy"
  }
}
EOF

########################################
# GitHub Actions
########################################

cat <<'EOF' > .github/workflows/build-deploy.yml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:

  build:

    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '20'

      - run: npm install

      - run: npm run build

      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
EOF

echo ""
echo "Bootstrap complete."
echo ""
echo "Next steps:"
echo "npm install"
echo "npm run start"
