package main

import (
    "encoding/xml"
    "fmt"
"io"
    "net/http"
    "time"
)




type ESearchResult struct {
    Count int   `xml:"Count"`
    IDs   []int `xml:"IdList>Id"`
}


type PubmedArticleSet struct {
	Articles []PubmedArticle `xml:"PubmedArticle"`
}

type PubmedArticle struct {
	Abstract struct {
		AbstractTexts []AbstractText `xml:"AbstractText"`
	} `xml:"Abstract"`
}

type AbstractText struct {
	Label       string `xml:"Label,attr"`
	NlmCategory string `xml:"NlmCategory,attr"`
	Text        string `xml:",chardata"`
}


func main() {
    // Set up PubMed search query parameters
    endDate := time.Now().Format("2006/01/02")
    startDate := time.Now().AddDate(0, 0, -7).Format("2006/01/02") // One week ago
    query := "cancer" // Example search term

    // Construct the PubMed search URL
    url := fmt.Sprintf("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s&mindate=%s&maxdate=%s", query, startDate, endDate)

    // Send the HTTP request to PubMed
    resp, err := http.Get(url)
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    // Parse the XML response
    var searchResult ESearchResult
    if err := xml.NewDecoder(resp.Body).Decode(&searchResult); err != nil {
        panic(err)
    }

    // Print the parsed search results
    fmt.Printf("PubMed Article IDs: %v\n", searchResult.IDs)

    // Iterate over the article IDs and fetch the PubMed articles
    for _, id := range searchResult.IDs {
        fetchPubMedArticle(id)
	time.Sleep(2* time.Second)
    }
}

func fetchPubMedArticle(id int) {
    // Construct the PubMed article URL
	url := fmt.Sprintf("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?rettype=abstract&db=pubmed&id=%d", id)
    // Send the HTTP request to fetch the PubMed article
    resp, err := http.Get(url)
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()
	var pubmedArticleSet PubmedArticleSet
	xmlContent, err := io.ReadAll(resp.Body);
	fmt.Println(string(xmlContent))
	if err := xml.NewDecoder(resp.Body).Decode(&pubmedArticleSet); err != nil {
		fmt.Println("Error parsing XML:", err)
		return
	}
	if len(pubmedArticleSet.Articles) > 0 {
		article := pubmedArticleSet.Articles[0]
		for _, abstractText := range article.Abstract.AbstractTexts {
			fmt.Printf("[%s] %s\n", abstractText.Label, abstractText.Text)
		}
	} else {
		fmt.Println("No PubMed articles found.")
	}

}

