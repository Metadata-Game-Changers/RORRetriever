# ROR Retriever
The [Research Organizatiopn Registry](https://ror.org) provides access to a growing collection of unique and persistent identifiers (RORs) for research organizations and a [web interface](https://ror.org) and [API](https://ror.readme.io/docs/rest-api) for searching the collection with an organization name or a affiliation string. The web interface and API work well if you have a small number of affiliation strings that need identifiers, but what if you have several hundred organization names or thousands of affiliation strings. This is the daunting problem that repositories face when they are trying to populate their existing records with identifiers. ROR Retriever is a tool developed to help address this problem.

# Usage
**Use python RORRetriever.py -h to see this usage description.**

```
usage: RORRetriever [-h] [-a [AFFILIATIONLIST [AFFILIATIONLIST ...]]] [-af AFFILIATIONFILENAME] [-ad AFFILIATIONDATA] [--noacronyms] [--max] [--details] [-o OUTPUTINTERVAL] [--loglevel {debug,info,warning}]
                    [--logto FILE]

search organization names and affiliations for RORs using the ROR Affiliation Strategy

optional arguments:
  -h, --help            show this help message and exit
  -a [AFFILIATIONLIST [AFFILIATIONLIST ...]], --affiliationList [AFFILIATIONLIST [AFFILIATIONLIST ...]]
                        a list of "affiliations in quotes"
  -af AFFILIATIONFILENAME, --affiliationFilename AFFILIATIONFILENAME
                        a file with one affiliation per line in current working directory
  -ad AFFILIATIONDATA, --affiliationData AFFILIATIONDATA
                        datafile (tsv, csv) with affiliations in cwd)
  --noacronyms          Exclude Acronym matches (default=False)
  --max                 Accept max score if no result chosen by ROR algorithm (more results and noise)
  --details             Show detailed response data (automatic for one ROR)
  -o OUTPUTINTERVAL, --outputInterval OUTPUTINTERVAL
                        For batch processing output results update interval default:20
  --loglevel {debug,info,warning}
                        Logging level
  --logto FILE          Log file (will overwrite if exists)
```

# Environment
ROR Reteriever imports the following python modules: requests, json, pandas, urllib.parse, sys, datetime, argparse, datetime, logging, os, re. The file RORRetriever.yml can be used to create the environment using the command **conda env create -f RORRetriever.yml**

# Outputs - ROR Search Results
The results of the search are provided in a tab-delimited file called **AffiliationAPI\_RORData\_\_TIMESTAMP.tsv**. This file has at least one row for every input affiliation but can have more if more than one ROR is identified for a single affiliation. In many cases when multiple RORs are found, some are incorrect and curation is required to select the correct one.

The columns in this file are:

| Name  | Definition |
|:--- |:---|
| affiliation      | the complete affiliation being searched |
|searchString_Affiliation|Complete affiliations are split into substrings during the search. This is the substring that foind the match.|
|ROR_Affiliation|The ROR identifier found using the substring.|
|organizationLookupName_Affiliation|The name of the organization with the found ROR.|
|country_Affiliation|The country the found organization is in.|
|match_Affiliation|The kind of match that was found (provided by algorithm)|
|chosen_Affiliation|TRUE if the algorithm chose this organization.|
|score|The algorithm score for this organization (0 - 1). If chosen is TRUE, score is 1.|
|numberOfResults_Affiliation|The number of results returned from the search.|
|VALID|A column for recording validity during curation (always TRUE prior to curation).|

# Outputs - Search Details
Some details of the ROR algorithm response can be displayed using the **--verbose** flag. This is automatic if only one affiliation is being searched. if **--verbose** is set, a table of the search results is shown with the following fields:

| Name  | Definition |
|:--- |:---|
|substring|Search string (can be substring of complete affiliation)
|score|Match score between 0 and 1 (1 is the best match chosen by algorithm)
|matchingType|Method that found the match (provided by algorithm)
|chosen|True for chosen ROR False for others
|organization|Name of organization for ROR (should match substring)
|country|Country of organization

# Example
As an example of some of the capabilities of this tool consider this list of affiliations:
The University of Alabama Libraries
Arizona State University Library
UC Berkeley Library
MIT Libraries

These strings are affiliations because they contain the names of research organizations that house various libraries. These are simple affiliations as they include university names with the words library or libraries. Despite this simplicity, they demonstrate some interesting characteristics of the ROR Affiliation search. These affiliations 

The command **RORRetriever -af OrganizationNamesTest.txt** uses the ROR affiliation API to search for RORs for these affiliations and gives this output to the terminal:

```
RORRetriever -af OrganizationNamesTest.txt           
2022-06-27 11:25:00:INFO:RORRetriever: Searching OrganizationNamesTest.txt for affiliations with Affiliation Strategy
2022-06-27 11:25:00:INFO:RORRetriever: 4 Input Affiliations
2022-06-27 11:25:03:INFO:RORRetriever: 3 new RORs written to AffiliationAPI_RORData__20220627_11.tsv
2022-06-27 11:25:03:INFO:RORRetriever: AffiliationAPI_RORData__20220627_11.tsv 3 RORs Found
```
More details are written to a tab-separated file (converted to a table here):

|affiliation|searchString_Affiliation|ROR_Affiliation|organizationLookupName_Affiliation|country_Affiliation|match_Affiliation|chosen_Affiliation|score|numberOfResults_Affiliation|valid
|:--- |:---|:--- |:---|:--- |:---|:--- |:---|:--- |:---
|The University of Alabama Libraries|University of Alabama|https://ror.org/03xrrjk67|University of Alabama|United States|HEURISTICS|True|1.0|9|True
|Arizona State University Library	|||||No Match|||4|False
|UC Berkeley Library|UC Berkeley Library|https://ror.org/01bndk311|Berkeley Public Library| United States|COMMON TERMS|True|0.9|10|True
MIT Libraries|MIT|https://ror.org/047m6hg73|Management Intelligenter Technologien (Germany)| Germany|ACRONYM|True|0.9|18|True

The output data shows that between 4 and 18 results were found for each of these affiliations and that RORs were identified for three. The organizationLookupName_Affiliation column gives the name associated with the ROR. In the first row, this name clearly matches the organization name in the input affiliation (The University of Alabama Libraries). In the other cases, the names suggest that either no match was chosen or the wrong match was chosen. 

There are two ways to find out what happened. First, the **--details** option can be used to show details for all searches at once, i.e. **RORRetriever -af OrganizationNamesTest.txt --details** or we can run each affiliation one at a time which automatically shows details.

The command **RORRetriever -a "Arizona State University Library"** gives the following results:

```   
2022-06-27 11:39:19:INFO:RORRetriever: 1 Input Affiliations
                       substring  score matching_type  chosen                       ror                                       organization       country
Arizona State University Library   0.86  COMMON TERMS   False https://ror.org/03efmqc40                           Arizona State University United States
Arizona State University Library   0.65  COMMON TERMS   False https://ror.org/03y1zyv86            Oklahoma State University Oklahoma City United States
Arizona State University Library   0.54  COMMON TERMS   False https://ror.org/00g3q3z36                               Arizona State Museum United States
Arizona State University Library   0.54  COMMON TERMS   False https://ror.org/01wwqrh75 Arizona State Library, Archives and Public Records United States
2022-06-27 11:39:20:INFO:RORRetriever: 0 new RORs written to AffiliationAPI_RORData__20220627_11.tsv
2022-06-27 11:39:20:INFO:RORRetriever: AffiliationAPI_RORData__20220627_11.tsv 0 RORs Found
```
The table shows the 4 results that were found and that the chosen column is False for all four, even though the right answer has the highest score of all four (0.86). The algorithm considers a number of factors in making a choice and, in this case, the correct answer did not pass the test.

The **--max** option can be used to choose the best answer even if the algorithm does not, so the command **RORRetriever -a "Arizona State University Library" --max** gives the results:

```
2022-06-27 11:45:15:INFO:RORRetriever: 1 Input Affiliations
2022-06-27 11:45:15:INFO:RORRetriever: ************** Best match is being found (may not be chosen by algorithm, score < 1.0)
                       substring  score matching_type  chosen                       ror                                       organization       country
Arizona State University Library   0.86  COMMON TERMS   False https://ror.org/03efmqc40                           Arizona State University United States
Arizona State University Library   0.65  COMMON TERMS   False https://ror.org/03y1zyv86            Oklahoma State University Oklahoma City United States
Arizona State University Library   0.54  COMMON TERMS   False https://ror.org/00g3q3z36                               Arizona State Museum United States
Arizona State University Library   0.54  COMMON TERMS   False https://ror.org/01wwqrh75 Arizona State Library, Archives and Public Records United States
2022-06-27 11:45:16:INFO:RORRetriever: 1 new RORs written to AffiliationAPI_RORData__20220627_11.tsv
2022-06-27 11:45:16:INFO:RORRetriever: AffiliationAPI_RORData__20220627_11.tsv 1 RORs Found
```
and the correct ROR is found. Note that the terminal output warns that this flag is set to make sure the user is aware that, while some results may improve, as in this example, there is also more noise introduced into the results. Also note that the results file contains a column named chosen which will be True for RORs selected by the algorithm and False for those not selected by the algorithm.

The details for the affiliation "UC Berkelely Library" can be seen using the command **RORRetriever -a "UC Berkelely Library"** with the results:

```
2022-06-27 11:54:23:INFO:RORRetriever: 1 Input Affiliations
          substring  score matching_type  chosen                       ror                               organization       country
UC Berkeley Library   0.90  COMMON TERMS    True https://ror.org/01bndk311                    Berkeley Public Library United States
UC Berkeley Library   0.79  COMMON TERMS   False https://ror.org/02jbv0t02      Lawrence Berkeley National Laboratory United States
UC Berkeley Library   0.58  COMMON TERMS   False https://ror.org/01an7q238         University of California, Berkeley United States
UC Berkeley Library   0.57  COMMON TERMS   False https://ror.org/02xewxa75                           Berkeley College United States
UC Berkeley Library   0.52  COMMON TERMS   False https://ror.org/01n7gem85                Deutsche Nationalbibliothek       Germany
UC Berkeley Library   0.50  COMMON TERMS   False https://ror.org/00b6wzg36 Acupuncture & Integrative Medicine College United States
UC Berkeley Library   0.46  COMMON TERMS   False https://ror.org/03fgher32                           UC Irvine Health United States
UC Berkeley Library   0.44  COMMON TERMS   False https://ror.org/048vdhs48                    Verbundzentrale des GBV       Germany
UC Berkeley Library   0.34  COMMON TERMS   False https://ror.org/05ehe8t08               UC Davis Children's Hospital United States
UC Berkeley Library   0.32  COMMON TERMS   False https://ror.org/04wvygn49                         Fundación Copec UC         Chile
```

In this case, the algorithm choses the ROR for "Berkeley Public Library" which has the maximum score (0.90) but is incorrect. The correct answer, University of California, Berkeley is in the results with a score of 0.58. This example is included here to remind us that there is an algorithm involved in these searches and we should help it as much as possible when we are providing affiliations to journals or libraries. In this case the acronym UC is a problem. The algorithm cannot guess that it stands for University of California. Help it out by writing the affiliation as University of California Berkeley Library and the algorithm gets thr gihht answer (**RORRetriever -a "University of California Berkeley Library"**).

The final example (MIT Libraries) illustrated another problem case, using an acronym in an affiliation rather than spelling it out. In this case, the command *RORRetriever -a "MIT Libraries"* shows the 7 organizations with the acronym MIT:

```
RORRetriever % RORRetriever -a "MIT Libraries"
2022-06-27 12:03:48:INFO:RORRetriever: 1 Input Affiliations
    substring  score matching_type  chosen                       ror                                    organization         country
          MIT   0.90       ACRONYM   False https://ror.org/002r67t24                 Manukau Institute of Technology     New Zealand
          MIT   0.90       ACRONYM   False https://ror.org/02mb6z761                   Myanmar Institute of Theology         Myanmar
          MIT   0.90       ACRONYM   False https://ror.org/02qk9nj07       Ministry of Infrastructures and Transport           Italy
          MIT   0.90       ACRONYM   False https://ror.org/02yyma482                 International Tourism Institute        Slovenia
          MIT   0.90       ACRONYM   False https://ror.org/042nb2s44           Massachusetts Institute of Technology   United States
          MIT   0.90       ACRONYM    True https://ror.org/047m6hg73 Management Intelligenter Technologien (Germany)         Germany
          MIT   0.90       ACRONYM   False https://ror.org/04mtcj695                 University of Southern Mindanao     Philippines
MIT Libraries   0.77  COMMON TERMS   False https://ror.org/00n3xk635                              Libraries Tasmania       Australia
MIT Libraries   0.76  COMMON TERMS   False https://ror.org/05mgwy297                           Smithsonian Libraries   United States
MIT Libraries   0.59         FUZZY   False https://ror.org/03qa42z85                                  Librairie Droz     Switzerland
MIT Libraries   0.58  COMMON TERMS   False https://ror.org/00w2b1v71                              Hesburgh Libraries   United States
MIT Libraries   0.57  COMMON TERMS   False https://ror.org/022z6jk58                          MIT Lincoln Laboratory   United States
MIT Libraries   0.56  COMMON TERMS   False https://ror.org/0239rpj17                             ImagineIF Libraries   United States
MIT Libraries   0.55  COMMON TERMS   False https://ror.org/00k8bhh21                        Polar Libraries Colloquy          Canada
MIT Libraries   0.50  COMMON TERMS   False https://ror.org/00rj4dg52                         Cambridge–MIT Institute  United Kingdom
MIT Libraries   0.46  COMMON TERMS   False https://ror.org/03fg5ns40                                   MIT Sea Grant   United States
MIT Libraries   0.44  COMMON TERMS   False https://ror.org/00v140q16                                  MIT University North Macedonia
MIT Libraries   0.22         FUZZY   False https://ror.org/05nfbnp91              Academy of Cryptography Techniques         Vietnam
```

The flag --noacronyms can prevent RORs based on acronyms from being selected. In this case, that misses the correct ROR but, in cases where RORs are selected on the basis of abbreviations in many affiliations, this can be helpful. Try **RORRetriever -a "Metadata LLC USA"** for an interesting example.

# Affiliation Best Practices
Keep in mind that ROR uses an algorithm to try to find RORs for affiliation strings and, as is always true, the algorithm is designed to work well in most cases. RORRetriever can help find RORs in batch mode if you have many affiliations or organization names to search. I find it very helpful, but always treat the results with care. See the [ROR API Documentation](https://ror.readme.io/docs/match-organization-names-to-ror-ids) for more tips and tricks. 

**Most important - write clear affilaitions when submitting data and publications!**
 
 
---
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" href="http://purl.org/dc/dcmitype/Text" property="dct:title" rel="dct:type">DataCiteFacets</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="metadatagamechangers.com" property="cc:attributionName" rel="cc:attributionURL">Ted Habermann</a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.