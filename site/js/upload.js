document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const file = document.getElementById("mdFile").files[0];
  if (!file) return alert("Please select a file!");

  const text = await file.text();

  // 간단한 정규식으로 PMID / Gene 추출
  const pmidMatches = [...text.matchAll(/PMID:\s*(\d+)/gi)];
  const geneMatches = [...text.matchAll(/Gene:\s*(\w+)/gi)];

  const pmids = pmidMatches.map(m => m[1]);
  const genes = geneMatches.map(m => m[1]);

  // Preview
  const previewDiv = document.getElementById("preview");
  previewDiv.innerHTML = `
    <strong>Extracted Genes:</strong> ${genes.join(", ")}<br>
    <strong>Extracted PMIDs:</strong> ${pmids.join(", ")}
  `;

  // 사용자에게 확인 요청
  if (confirm("Looks good? Ready to commit via GitHub Action.")) {
    alert("Next step: push the md file to 'uploads/' folder to trigger Action.");
  }
});
