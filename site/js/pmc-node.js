const fs = require("fs");
const fetch = require("node-fetch");
const xml2js = require("xml2js");

const g2pPath = "./site/_data/g2p.json";
let g2p = {};
if (fs.existsSync(g2pPath)) g2p = JSON.parse(fs.readFileSync(g2pPath));

async function processPMC(pmcId, genes) {
  // 1. PMC XML 가져오기
  const url = `https://www.ebi.ac.uk/europepmc/webservices/rest/${pmcId}/fullTextXML`;
  const res = await fetch(url);
  const xml = await res.text();

  // 2. XML → JS Object
  const parser = new xml2js.Parser();
  const data = await parser.parseStringPromise(xml);

  // 3. Title & abstract 추출
  const article = data['article'] || {};
  const title = article['front']?.[0]['article-meta']?.[0]['title-group']?.[0]['article-title']?.[0] || pmcId;
  const abstract = article['front']?.[0]['article-meta']?.[0]['abstract']?.[0]?.['p']?.join(" ") || "";

  // 4. g2p 업데이트
  genes.forEach(g => {
    if (!g2p[g]) g2p[g] = [];
    if (!g2p[g].includes(pmcId)) g2p[g].push(pmcId);
  });

  // 5. 파일 저장
  fs.writeFileSync(g2pPath, JSON.stringify(g2p, null, 2));
  console.log(`Processed ${pmcId}: ${title}`);
  console.log(`Abstract: ${abstract.slice(0, 200)}...`);
}

// 예시 실행
processPMC("PMC5094965", ["TMPRSS2-ERG","PTEN"]);
