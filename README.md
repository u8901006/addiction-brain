# Addiction Brain 🧠

**成癮醫學文獻日報** — 每日自動從 PubMed 抓取最新成癮醫學與心理學 Q1/Q2 期刊文獻，由 AI 分析整理，部署至 GitHub Pages。

## 架構

```
GitHub Actions (每日 11:00 台北時間)
  → fetch_papers.py (PubMed API)
  → generate_report.py (Zhipu GLM-5.1 AI 分析)
  → docs/addiction-YYYY-MM-DD.html
  → docs/index.html
  → GitHub Pages
```

## 期刊來源（Q1-Q2）

Addiction, Addictive Behaviors, Drug and Alcohol Dependence, Psychology of Addictive Behaviors, Journal of Behavioral Addictions, Journal of Addiction Medicine, The American Journal on Addictions, Addiction Research & Theory, International Journal of Mental Health and Addiction, Nicotine & Tobacco Research, Journal of Studies on Alcohol and Drugs, Substance Use & Misuse, Addiction Biology, European Addiction Research, Alcohol and Alcoholism, The American Journal of Drug and Alcohol Abuse, Drug and Alcohol Review

## 本地測試

```bash
pip install -r scripts/requirements.txt
python scripts/fetch_papers.py --days 7 --max-papers 10 --json --output papers.json
ZHIPU_API_KEY=your_key python scripts/generate_report.py --input papers.json --output test.html
```

## 相關連結

- 🔗 [李政洋身心診所](https://www.leepsyclinic.com/)
- 📨 [訂閱電子報](https://blog.leepsyclinic.com/)
- 🧠 [Psychiatry Brain（精神醫學文獻日報）](https://u8901006.github.io/Psychiatry-brain/)
