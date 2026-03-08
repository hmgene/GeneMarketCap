const fs = require("fs");
const fetch = require("node-fetch");
const xml2js = require("xml2js");
const path = require("path");

const g2pPath = path.join(__dirname, "_data/g2p.json");
let g2p = {};
if (fs.existsSync(g2pPath)) g2p = JSON.parse(fs.readFileSync(g2pPath));

const papersDir = path.join(__dirname,"papers");
//console.log(papersDir); process.exit()

const files = fs.readdirSync(papersDir).filter(f => f.endsWith(".md"));
//console.log(files); process.exit()

async function processPMCFile(file) {
  const content = fs.readFileSync(path.join(__dirname, file), "utf8");
  const pmcIdMatch = content.match(/pmcid:\s*(\S+)/);
  const genesMatch = content.match(/genes:\s*(.+)/);

  if (!pmcIdMatch || !genesMatch) return;

  const pmcId = pmcIdMatch[1].trim();
  const genes = genesMatch[1].split(",").map(g => g.trim());

  // 1. PMC XML fetch
  const url = `https://www.ebi.ac.uk/europepmc/webservices/rest/${pmcId}/fullTextXML`;
  const res = await fetch(url);
  const xml = await res.text();

  // 2. XML → JS Object
  const parser = new xml2js.Parser();
  const data = await parser.parseStringPromise(xml);

  // 3. Title + abstract 추출
  const article = data['article'] || {};
  const title = article['front']?.[0]['article-meta']?.[0]['title-group']?.[0]['article-title']?.[0] || pmcId;
  const abstract = article['front']?.[0]['article-meta']?.[0]['abstract']?.[0]?.['p']?.join(" ") || "";

  console.log(`Processed ${pmcId}: ${title}`);
  console.log(`Abstract: ${abstract.slice(0,200)}...`);

  // 4. g2p.json 업데이트
  genes.forEach(g => {
    if (!g2p[g]) g2p[g] = [];
    if (!g2p[g].includes(pmcId)) g2p[g].push(pmcId);
  });
}

(async () => {
  for (const f of files) {
    await processPMCFile(path.join("papers/",f));
  }
  fs.writeFileSync(g2pPath, JSON.stringify(g2p, null, 2));
})();
