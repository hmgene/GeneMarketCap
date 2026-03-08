module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy("site/papers");

  eleventyConfig.addCollection("papers", function(collectionApi) {
    const fs = require("fs");
    const path = require("path");
    const papersDir = path.join(__dirname, "site", "papers");
    if (!fs.existsSync(papersDir)) return [];
    return fs.readdirSync(papersDir).filter(f => f.endsWith(".md"));
  });

  return {
    dir: {
      input: "site",
      output: "docs"
    }
  };
};
