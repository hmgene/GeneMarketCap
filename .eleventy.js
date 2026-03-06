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
