#!/usr/bin/env python3
"""
Fetch latest addiction medicine & psychology research papers from PubMed E-utilities API.
Targets top addiction journals (Q1-Q2) and covers substance use, behavioral addictions,
clinical psychology, and public health topics.
"""

import json
import sys
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import quote_plus

PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

JOURNALS = [
    "Addiction",
    "Addictive Behaviors",
    "Drug Alcohol Depend",
    "Psychol Addict Behav",
    "J Behav Addict",
    "J Addict Med",
    "Am J Addict",
    "Addict Res Theory",
    "Int J Ment Health Addict",
    "Nicotine Tob Res",
    "J Stud Alcohol Drugs",
    "Subst Use Misuse",
    "Addict Biol",
    "Eur Addict Res",
    "Alcohol Alcohol",
    "Am J Drug Alcohol Abuse",
    "Drug Alcohol Rev",
    "Sexual Abuse",
    "Arch Sex Behav",
    "J Sex Marital Ther",
]

TOPICS = [
    "addiction",
    "substance use disorder",
    "alcohol use disorder",
    "alcohol dependence",
    "alcohol misuse",
    "binge drinking",
    "opioid use disorder",
    "behavioral addiction",
    "gambling disorder",
    "problem gambling",
    "pathological gambling",
    "gaming disorder",
    "internet addiction",
    "smartphone addiction",
    "compulsive sexual behavior",
    "hypersexuality",
    "sexual addiction",
    "problematic sexual behavior",
    "problematic pornography use",
    "voyeuristic disorder",
    "voyeurism",
    "pedophilic disorder",
    "pedophilia",
    "image-based sexual abuse",
    "non-consensual recording",
    "technology-facilitated sexual violence",
    "nicotine dependence",
    "cannabis use disorder",
    "cannabis dependence",
    "ketamine misuse",
    "ketamine dependence",
    "ketamine use disorder",
    "GHB misuse",
    "GHB dependence",
    "gamma-hydroxybutyrate",
    "etomidate misuse",
    "etomidate dependence",
    "fentanyl misuse",
    "fentanyl use disorder",
    "fentanyl dependence",
    "fentanyl overdose",
    "opioid overdose",
    "naloxone",
    "craving",
    "withdrawal",
    "relapse prevention",
    "harm reduction",
    "buprenorphine",
    "naltrexone",
    "methadone",
    "acamprosate",
    "motivational interviewing",
    "contingency management",
    "dual diagnosis",
    "impulsivity",
    "compulsivity",
    "reward processing",
    "emotion regulation",
    "trauma",
    "dissociation",
    "suicidality",
    "forensic psychiatry",
    "risk assessment",
    "recidivism",
    "screening",
    "brief intervention",
    "CBT",
    "mindfulness",
    "ACT",
    "pharmacotherapy",
]

EXTRA_SEARCH_TEMPLATES = [
    '("compulsive sexual behavior"[tiab] OR "sexual addiction"[tiab] OR hypersexuality[tiab] OR "problematic sexual behavior"[tiab]) AND (treatment[tiab] OR prevalence[tiab] OR comorbidity[tiab])',
    '("compulsive sexual behavior"[tiab] OR hypersexuality[tiab] OR "sexual addiction"[tiab]) AND (trauma[tiab] OR PTSD[tiab] OR dissociation[tiab] OR "childhood adversity"[tiab] OR shame[tiab] OR "emotion regulation"[tiab])',
    '("compulsive sexual behavior"[tiab] OR "sexual addiction"[tiab] OR hypersexuality[tiab]) AND (pornography[tiab] OR "problematic pornography use"[tiab] OR "online sexual behavior"[tiab] OR cybersex[tiab])',
    '("gambling disorder"[tiab] OR "problem gambling"[tiab] OR "pathological gambling"[tiab]) AND (screening[tiab] OR treatment[tiab] OR prevalence[tiab] OR comorbidity[tiab] OR intervention[tiab])',
    '("gambling disorder"[tiab] OR "problem gambling"[tiab] OR "pathological gambling"[tiab]) AND (depression[tiab] OR anxiety[tiab] OR suicid*[tiab] OR "substance use"[tiab] OR alcohol[tiab] OR ADHD[tiab])',
    '("gambling disorder"[tiab] OR "problem gambling"[tiab]) AND (screening[tiab] OR "brief screening"[tiab] OR questionnaire[tiab]) AND ("mental health"[tiab] OR psychiatry[tiab] OR "primary care"[tiab])',
    '("voyeuristic disorder"[tiab] OR voyeurism[tiab] OR "voyeuristic behavior"[tiab]) AND (assessment[tiab] OR treatment[tiab] OR forensic[tiab] OR psychiatry[tiab] OR comorbidity[tiab] OR risk[tiab])',
    '(voyeurism[tiab] OR "voyeuristic disorder"[tiab] OR "sexual offending"[tiab]) AND (recidivism[tiab] OR "risk assessment"[tiab] OR forensic[tiab] OR treatment[tiab] OR criminology[tiab])',
    '("pedophilic disorder"[tiab] OR pedophilia[tiab] OR "minor-attracted persons"[tiab]) AND (assessment[tiab] OR treatment[tiab] OR prevention[tiab] OR psychotherapy[tiab] OR neurobiology[tiab] OR forensic[tiab])',
    '("pedophilic disorder"[tiab] OR pedophilia[tiab] OR "minor-attracted persons"[tiab]) AND ("child sexual abuse material"[tiab] OR "child sexual exploitation material"[tiab] OR CSAM[tiab] OR "child pornography"[tiab]) AND (forensic[tiab] OR treatment[tiab] OR risk[tiab] OR prevention[tiab])',
    '("pedophilic disorder"[tiab] OR pedophilia[tiab]) AND (cognition[tiab] OR "executive function"[tiab] OR empathy[tiab] OR impulsivity[tiab] OR neuroimaging[tiab] OR "risk assessment"[tiab])',
    '("image-based sexual abuse"[tiab] OR "non-consensual intimate image"[tiab] OR "non-consensual recording"[tiab] OR "covert recording"[tiab] OR "illicit filming"[tiab] OR "surreptitious recording"[tiab] OR "technology-facilitated sexual violence"[tiab]) AND (forensic[tiab] OR psychiatry[tiab] OR victimization[tiab] OR offender*[tiab] OR prevention[tiab] OR legal[tiab])',
    '(voyeurism[tiab] OR "voyeuristic disorder"[tiab] OR "image-based sexual abuse"[tiab] OR "non-consensual recording"[tiab]) AND (digital[tiab] OR online[tiab] OR filming[tiab] OR recording[tiab] OR smartphone[tiab])',
    '("alcohol use disorder"[tiab] OR "alcohol dependence"[tiab] OR "alcohol misuse"[tiab] OR alcoholism[tiab]) AND (treatment[tiab] OR pharmacotherapy[tiab] OR psychotherapy[tiab] OR relapse[tiab] OR withdrawal[tiab])',
    '("alcohol use disorder"[tiab] OR "alcohol dependence"[tiab]) AND (depression[tiab] OR anxiety[tiab] OR PTSD[tiab] OR suicid*[tiab] OR insomnia[tiab] OR "psychiatric comorbidity"[tiab])',
    '(ketamine[tiab]) AND ("alcohol use disorder"[tiab] OR "alcohol dependence"[tiab] OR alcoholism[tiab]) AND (craving[tiab] OR abstinence[tiab] OR relapse[tiab] OR treatment[tiab])',
    '("gamma-hydroxybutyrate"[tiab] OR "gamma hydroxybutyrate"[tiab] OR GHB[tiab] OR GBL[tiab] OR "1,4-butanediol"[tiab]) AND (misuse[tiab] OR dependence[tiab] OR withdrawal[tiab] OR intoxication[tiab] OR overdose[tiab] OR treatment[tiab])',
    '("gamma-hydroxybutyrate"[tiab] OR GHB[tiab] OR GBL[tiab]) AND (withdrawal[tiab] OR detoxification[tiab] OR benzodiazepine*[tiab] OR baclofen[tiab] OR ICU[tiab] OR delirium[tiab])',
    '("cannabis use disorder"[tiab] OR "marijuana use disorder"[tiab] OR "cannabis dependence"[tiab] OR "heavy cannabis use"[tiab]) AND (treatment[tiab] OR withdrawal[tiab] OR comorbidity[tiab] OR cognition[tiab] OR psychosis[tiab])',
    '("cannabis use disorder"[tiab] OR "cannabis dependence"[tiab]) AND (anxiety[tiab] OR depression[tiab] OR psychosis[tiab] OR bipolar[tiab] OR ADHD[tiab] OR sleep[tiab])',
    '(ketamine[tiab]) AND (misuse[tiab] OR abuse[tiab] OR dependence[tiab] OR "use disorder"[tiab] OR recreational[tiab] OR addiction[tiab]) AND (cognition[tiab] OR cystitis[tiab] OR depression[tiab] OR withdrawal[tiab] OR treatment[tiab])',
    '(ketamine[tiab]) AND (cystitis[tiab] OR "lower urinary tract"[tiab] OR uropathy[tiab] OR bladder[tiab]) AND (misuse[tiab] OR abuse[tiab] OR dependence[tiab])',
    '(ketamine[tiab]) AND (misuse[tiab] OR dependence[tiab] OR addiction[tiab]) AND (depression[tiab] OR anxiety[tiab] OR psychosis[tiab] OR dissociation[tiab] OR suicid*[tiab])',
    '(etomidate[tiab]) AND (abuse[tiab] OR misuse[tiab] OR dependence[tiab] OR addiction[tiab] OR withdrawal[tiab] OR intoxication[tiab])',
    '(etomidate[tiab]) AND ("adrenal suppression"[tiab] OR cortisol[tiab] OR intoxication[tiab] OR dependence[tiab] OR withdrawal[tiab])',
    '(etomidate[tiab]) AND ("case report"[Publication Type] OR "case reports"[tiab] OR series[tiab] OR toxicology[tiab] OR emergency[tiab])',
    '(("alcohol use disorder"[tiab] OR "cannabis use disorder"[tiab] OR ketamine[tiab] OR GHB[tiab] OR gambling[tiab] OR "compulsive sexual behavior"[tiab]) AND (depression[tiab] OR anxiety[tiab] OR PTSD[tiab] OR ADHD[tiab] OR bipolar[tiab] OR insomnia[tiab] OR suicid*[tiab])) AND (treatment[tiab] OR screening[tiab] OR psychotherapy[tiab] OR pharmacotherapy[tiab])',
    '(("gambling disorder"[tiab] OR "compulsive sexual behavior"[tiab] OR "cannabis use disorder"[tiab] OR "alcohol use disorder"[tiab] OR ketamine[tiab]) AND (impulsivity[tiab] OR compulsivity[tiab] OR "reward processing"[tiab] OR craving[tiab] OR "decision making"[tiab])) AND (neurobiology[tiab] OR neuroimaging[tiab] OR intervention[tiab] OR treatment[tiab])',
    '(("voyeuristic disorder"[tiab] OR voyeurism[tiab] OR "pedophilic disorder"[tiab] OR pedophilia[tiab] OR "image-based sexual abuse"[tiab] OR "non-consensual recording"[tiab]) AND (forensic[tiab] OR psychiatry[tiab] OR risk[tiab] OR recidivism[tiab] OR prevention[tiab] OR treatment[tiab]))',
    '(fentanyl[tiab]) AND ("use disorder"[tiab] OR misuse[tiab] OR dependence[tiab] OR overdose[tiab] OR addiction[tiab]) AND (treatment[tiab] OR naloxone[tiab] OR buprenorphine[tiab] OR methadone[tiab] OR prevention[tiab] OR "harm reduction"[tiab])',
    '("fentanyl overdose"[tiab] OR "opioid overdose"[tiab]) AND (naloxone[tiab] OR prevention[tiab] OR "harm reduction"[tiab] OR emergency[tiab] OR "take-home naloxone"[tiab])',
    '("fentanyl use disorder"[tiab] OR "fentanyl dependence"[tiab] OR ("fentanyl"[tiab] AND addiction[tiab])) AND (treatment[tiab] OR withdrawal[tiab] OR pharmacotherapy[tiab] OR "medication-assisted treatment"[tiab])',
    '(fentanyl[tiab]) AND (polysubstance[tiab] OR "xylazine"[tiab] OR "heroin"[tiab] OR "counterfeit"[tiab] OR "illicitly manufactured"[tiab]) AND (overdose[tiab] OR mortality[tiab] OR epidemiology[tiab] OR treatment[tiab])',
]

HEADERS = {"User-Agent": "AddictionBrainBot/1.0 (research aggregator)"}


def build_query(days: int = 7, max_journals: int = 15) -> str:
    journal_part = " OR ".join([f'"{j}"[Journal]' for j in JOURNALS[:max_journals]])
    lookback = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y/%m/%d")
    date_part = f'"{lookback}"[Date - Publication] : "3000"[Date - Publication]'
    return f"({journal_part}) AND {date_part}"


def build_extra_queries(days: int = 7) -> list[str]:
    lookback = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y/%m/%d")
    date_part = f'"{lookback}"[Date - Publication] : "3000"[Date - Publication]'
    queries = []
    for template in EXTRA_SEARCH_TEMPLATES:
        queries.append(f"({template}) AND {date_part}")
    return queries


def search_papers(query: str, retmax: int = 50) -> list[str]:
    params = (
        f"?db=pubmed&term={quote_plus(query)}&retmax={retmax}&sort=date&retmode=json"
    )
    url = PUBMED_SEARCH + params
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"[ERROR] PubMed search failed: {e}", file=sys.stderr)
        return []


def fetch_details(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    ids = ",".join(pmids)
    params = f"?db=pubmed&id={ids}&retmode=xml"
    url = PUBMED_FETCH + params
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=60) as resp:
            xml_data = resp.read().decode()
    except Exception as e:
        print(f"[ERROR] PubMed fetch failed: {e}", file=sys.stderr)
        return []

    papers = []
    try:
        root = ET.fromstring(xml_data)
        for article in root.findall(".//PubmedArticle"):
            medline = article.find(".//MedlineCitation")
            art = medline.find(".//Article") if medline else None
            if art is None:
                continue

            title_el = art.find(".//ArticleTitle")
            title = (
                (title_el.text or "").strip()
                if title_el is not None and title_el.text
                else ""
            )

            abstract_parts = []
            for abs_el in art.findall(".//Abstract/AbstractText"):
                label = abs_el.get("Label", "")
                text = "".join(abs_el.itertext()).strip()
                if label and text:
                    abstract_parts.append(f"{label}: {text}")
                elif text:
                    abstract_parts.append(text)
            abstract = " ".join(abstract_parts)[:2000]

            journal_el = art.find(".//Journal/Title")
            journal = (
                (journal_el.text or "").strip()
                if journal_el is not None and journal_el.text
                else ""
            )

            pub_date = art.find(".//PubDate")
            date_str = ""
            if pub_date is not None:
                year = pub_date.findtext("Year", "")
                month = pub_date.findtext("Month", "")
                day = pub_date.findtext("Day", "")
                parts = [p for p in [year, month, day] if p]
                date_str = " ".join(parts)

            pmid_el = medline.find(".//PMID")
            pmid = pmid_el.text if pmid_el is not None else ""
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""

            keywords = []
            for kw in medline.findall(".//KeywordList/Keyword"):
                if kw.text:
                    keywords.append(kw.text.strip())

            papers.append(
                {
                    "pmid": pmid,
                    "title": title,
                    "journal": journal,
                    "date": date_str,
                    "abstract": abstract,
                    "url": link,
                    "keywords": keywords,
                }
            )
    except ET.ParseError as e:
        print(f"[ERROR] XML parse failed: {e}", file=sys.stderr)

    return papers


def main():
    parser = argparse.ArgumentParser(description="Fetch addiction papers from PubMed")
    parser.add_argument("--days", type=int, default=7, help="Lookback days")
    parser.add_argument(
        "--max-papers", type=int, default=40, help="Max papers to fetch"
    )
    parser.add_argument("--output", default="-", help="Output file (- for stdout)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    query = build_query(days=args.days)
    print(
        f"[INFO] Searching PubMed for addiction papers from last {args.days} days...",
        file=sys.stderr,
    )

    all_pmids = search_papers(query, retmax=args.max_papers)
    print(f"[INFO] Journal search found {len(all_pmids)} papers", file=sys.stderr)

    print(
        f"[INFO] Running {len(EXTRA_SEARCH_TEMPLATES)} extra topic searches...",
        file=sys.stderr,
    )
    extra_queries = build_extra_queries(days=args.days)
    for i, eq in enumerate(extra_queries):
        extra_pmids = search_papers(eq, retmax=10)
        new_pmids = [p for p in extra_pmids if p not in all_pmids]
        if new_pmids:
            print(
                f"[INFO] Extra search {i+1}/{len(extra_queries)}: +{len(new_pmids)} new papers",
                file=sys.stderr,
            )
            all_pmids.extend(new_pmids)

    all_pmids = all_pmids[: args.max_papers * 2]
    print(f"[INFO] Total unique PMIDs: {len(all_pmids)}", file=sys.stderr)

    if not all_pmids:
        print("NO_CONTENT", file=sys.stderr)
        if args.json:
            print(
                json.dumps(
                    {
                        "date": datetime.now(timezone(timedelta(hours=8))).strftime(
                            "%Y-%m-%d"
                        ),
                        "count": 0,
                        "papers": [],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        return

    papers = fetch_details(all_pmids)
    print(f"[INFO] Fetched details for {len(papers)} papers", file=sys.stderr)

    output_data = {
        "date": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d"),
        "count": len(papers),
        "papers": papers,
    }

    out_str = json.dumps(output_data, ensure_ascii=False, indent=2)

    if args.output == "-":
        print(out_str)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str)
        print(f"[INFO] Saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
