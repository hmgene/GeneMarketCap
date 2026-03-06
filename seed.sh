#!/bin/bash
set -e

# 1. Create package.json if missing
if [ ! -f package.json ]; then
  echo "Creating minimal package.json..."
  cat > package.json << 'EOF'
{
  "name": "minimal-11ty-gene",
  "version": "1.0.0",
  "description": "Minimal Eleventy setup reading gene_mentions.json",
  "scripts": {
    "build": "eleventy --input=site --output=docs",
    "start": "eleventy --input=site --output=docs --serve"
  },
  "devDependencies": {
    "@11ty/eleventy": "^3.1.2"
  },
  "author": "hyunmin",
  "license": "MIT"
}
EOF
fi

# 2. Install Eleventy locally
npm install

# 3. Create folder structure
mkdir -p site/_data docs

# 4. Create example gene_mentions.json
cat > site/_data/gene_mentions.json << 'EOF'
{
  "BRCA1": ["paper1.md", "paper2.md"],
  "TP53": ["paper3.md", "paper4.md"],
  "MYC": ["paper5.md"]
}
EOF

# 5. Create minimal index.njk template
cat > site/index.njk << 'EOF'
---
layout: null
title: Gene Mentions
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{ title }}</title>
</head>
<body>
  <h1>{{ title }}</h1>
  <ul>
    {% for gene, mentions in gene_mentions %}
      <li>{{ gene }} : {{ mentions | join(", ") }}</li>
    {% endfor %}
  </ul>
</body>
</html>
EOF

# 6. Build Eleventy
#npx eleventy --input=site --output=docs --quiet

echo "✅ Eleventy build complete. Open docs/index.html"
echo "Run 'npm start' to serve locally"
