#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');
const xml2js = require('xml2js');

// Search through papers directories for pmid/pmcid patterns
function extractPMIDsFromPapers() {
  const results = [];
  const papersDir = path.resolve(__dirname, '../..');

  // Search in both site and docs directories
  const searchDirs = [
    path.join(papersDir, 'site/papers'),
    path.join(papersDir, 'docs/papers')
  ];

  searchDirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      console.log(`Directory not found: ${dir}`);
      return;
    }

    const files = fs.readdirSync(dir).filter(file => file.endsWith('.md'));

    files.forEach(file => {
      const filePath = path.join(dir, file);
      try {
        const content = fs.readFileSync(filePath, 'utf-8');

        // Search for pmid: <number> or pmcid: <id>
        const pmidMatch = content.match(/pmid:\s*(\d+)/i);
        const pmcidMatch = content.match(/pmcid:\s*(PMC\d+)/i);

        if (pmidMatch || pmcidMatch) {
          results.push({
            filename: file,
            filepath: filePath,
            pmid: pmidMatch ? pmidMatch[1] : null,
            pmcid: pmcidMatch ? pmcidMatch[1] : null
          });
        }
      } catch (error) {
        console.error(`Error reading file ${filePath}:`, error.message);
      }
    });
  });

  return results;
}

// Group papers by their unique identifier (PMID or PMCID)
function groupPapersByIdentifier(papers) {
  const grouped = new Map();

  papers.forEach(paper => {
    const key = paper.pmid || paper.pmcid;
    if (!grouped.has(key)) {
      grouped.set(key, {
        pmid: paper.pmid,
        pmcid: paper.pmcid,
        filenames: new Set(),
        filepaths: new Set(),
        title: null,
        abstract: null
      });
    }

    const group = grouped.get(key);
    group.filenames.add(paper.filename);
    group.filepaths.add(paper.filepath);
  });

  // Convert Sets to Arrays for JSON serialization
  return Array.from(grouped.values()).map(group => ({
    ...group,
    filenames: Array.from(group.filenames),
    filepaths: Array.from(group.filepaths)
  }));
}

// Fetch abstract from PubMed using PMID or PMCID
async function fetchAbstractFromPubMed(pmid, pmcid) {
  try {
    const id = pmid || pmcid.replace('PMC', '');
    const db = pmcid ? 'pmc' : 'pubmed';
    const url = `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=${db}&id=${id}&rettype=xml&retmode=xml`;

    console.log(`  Fetching from PubMed: ${id}...`);
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const xmlData = await response.text();
    const parser = new xml2js.Parser();
    const jsonData = await parser.parseStringPromise(xmlData);

    let title = 'Not found';
    let abstract = 'No abstract available';

    // Handle PubMed response
    if (jsonData.PubmedArticleSet?.PubmedArticle?.[0]) {
      const article = jsonData.PubmedArticleSet.PubmedArticle[0];
      const articleData = article.MedlineCitation?.[0]?.Article?.[0];

      if (articleData) {
        title = articleData.ArticleTitle?.[0] || 'Not found';

        if (articleData.Abstract?.[0]?.AbstractText) {
          const abstractText = articleData.Abstract[0].AbstractText;
          if (Array.isArray(abstractText)) {
            abstract = abstractText.map(text => {
              if (typeof text === 'object' && text._) return text._;
              return String(text);
            }).join(' ');
          } else {
            abstract = String(abstractText);
          }
        }
      }
    }

    return { title, abstract };
  } catch (error) {
    console.error(`  Error fetching from PubMed: ${error.message}`);
    return { title: 'Error fetching', abstract: 'Error fetching' };
  }
}

// lightweight LLM helper: extract gene/TF names from text using an OpenAI model
async function extractGenesFromText(text) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY environment variable is required');
  }

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: 'You are a concise assistant that reads biomedical text and returns only a JSON array of gene or transcription factor symbols mentioned therein.'
        },
        { role: 'user', content: text }
      ],
      temperature: 0.0
    })
  });

  const data = await response.json();
  let result = data.choices?.[0]?.message?.content?.trim() || '';
  try {
    return JSON.parse(result);
  } catch (_err) {
    return result.split(/[\s,]+/).filter(Boolean);
  }
}

// Main
async function main() {
  const rawPapers = extractPMIDsFromPapers();
  const groupedPapers = groupPapersByIdentifier(rawPapers);

  console.log(`Found ${rawPapers.length} paper files, grouped into ${groupedPapers.length} unique papers\n`);

  // Fetch abstracts for each unique paper
  for (let i = 0; i < groupedPapers.length; i++) {
    const paper = groupedPapers[i];
    console.log(`[${i + 1}/${groupedPapers.length}] Processing ${paper.filenames.join(', ')}`);

    const { title, abstract } = await fetchAbstractFromPubMed(paper.pmid, paper.pmcid);
    paper.title = title;
    paper.abstract = abstract;

    // use light LLM to extract gene names from title+abstract
    try {
      paper.genes = await extractGenesFromText(`${title}\n\n${abstract}`);
    } catch (err) {
      console.error('  gene extraction error:', err.message);
      paper.genes = [];
    }

    // Small delay to avoid overwhelming the API
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  // Output as JSON
  const output = {
    total_count: groupedPapers.length,
    papers: groupedPapers
  };
  console.log('\n' + JSON.stringify(output, null, 2));

  // Save to site/_data/papers.json
  const outputPath = path.resolve(__dirname, '../_data/papers.json');
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  console.error(`\n✅ Results saved to ${outputPath}`);
}

main().catch(console.error);