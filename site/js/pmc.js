document.getElementById("pmcForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const url = document.getElementById("pmcLink").value;
  const pmcIdMatch = url.match(/PMC(\d+)/i);
  if (!pmcIdMatch) return alert("Invalid PMC URL");

  const pmcId = pmcIdMatch[1];

  // 1. Fetch article text
  const apiUrl = `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:PMC${pmcId}&format=json`;
  const res = await fetch(apiUrl);
  const data = await res.json();

  if (!data.resultList?.result?.length) return alert("PMC article not found");

  const article = data.resultList.result[0];
  const title = article.title;
  const abstract = article.abstractText;

  // 2. Extract gene names (간단 regex, 필요시 NLP로 강화)
  const geneRegex = /\b(TMPRSS2-ERG|PTEN|NOTCH1)\b/g; // 예시: 나중에 list 확장
  const genes = [...new Set([...title.matchAll(geneRegex), ...abstract.matchAll(geneRegex)].map(m => m[0]))];

  // Preview
  const preview = document.getElementById("preview");
  preview.innerHTML = `
    <h3>PMC${pmcId}</h3>
    <strong>Title:</strong> ${title}<br>
    <strong>Abstract:</strong> ${abstract}<br>
    <strong>Genes:</strong> ${genes.join(", ")}
  `;

  // 3. 안내
  if (confirm("Looks correct? Ready to commit via Action.")) {
    alert(`Next step: push PMC${pmcId} info to GitHub or trigger Action to update g2p.json.`);
  }
});
