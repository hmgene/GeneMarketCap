package main

import (
    "encoding/xml"
    "fmt"
)

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
    xmlData := `<PubmedArticleSet>
                    <PubmedArticle>
                        <Abstract>
                            <AbstractText Label="BACKGROUND" NlmCategory="UNASSIGNED">This study was designed to evaluate the effects of body mass index (BMI) and weight change on the risk of developing cancer overall and cancer at different sites.</AbstractText>
                            <AbstractText Label="METHODS" NlmCategory="UNASSIGNED">We searched PubMed and other databases up to July 2023 using the keywords related to 'risk', 'cancer', 'weight', 'overweight', and 'obesity'. We identified eligible studies, and the inclusion criteria encompassed cohort studies in English that focused on cancer diagnosis and included BMI or weight change as an exposure factor. Multiple authors performed data extraction and quality assessment, and statistical analyses were carried out using RevMan and R software. We used random- or fixed-effects models to calculate the pooled relative risk (RR) or hazard ratio along with 95% confidence intervals (CIs). We used the Newcastle-Ottawa Scale to assess study quality.</AbstractText>
                            <AbstractText Label="RESULTS" NlmCategory="UNASSIGNED">Analysis included 66 cohort studies. Compared to underweight or normal weight, overweight or obesity was associated with an increased risk of endometrial cancer, kidney cancer, and liver cancer but a decreased risk of prostate cancer and lung cancer. Being underweight was associated with an increased risk of gastric cancer and lung cancer but not that of postmenopausal breast cancer or female reproductive cancer. In addition, weight loss of more than five kg was protective against overall cancer risk.</AbstractText>
                            <AbstractText Label="CONCLUSIONS" NlmCategory="UNASSIGNED">Overweight and obesity increase the risk of most cancers, and weight loss of >5 kg reduces overall cancer risk. These findings provide insights for cancer prevention and help to elucidate the mechanisms underlying cancer development.</AbstractText>
                            <AbstractText Label="REGISTRATION" NlmCategory="UNASSIGNED">Reviewregistry1786.</AbstractText>
                        </Abstract>
                    </PubmedArticle>
                </PubmedArticleSet>`

    var pubmedArticleSet PubmedArticleSet
    if err := xml.Unmarshal([]byte(xmlData), &pubmedArticleSet); err != nil {
        fmt.Println("Error parsing XML:", err)
        return
    }

    // Access the parsed data
    for _, article := range pubmedArticleSet.Articles {
        for _, abstractText := range article.Abstract.AbstractTexts {
            fmt.Println("Label:", abstractText.Label)
            fmt.Println("NlmCategory:", abstractText.NlmCategory)
            fmt.Println("Text:", abstractText.Text)
            fmt.Println()
        }
    }
}

