

# 🎣 DeepBait

**Fake LinkedIn Profile Detector — OSINT + ML**

DeepBait analyzes LinkedIn profiles using **15 heuristic OSINT signals** and a **Random Forest classifier** to detect fake accounts, bots, sockpuppets, and fraudulent recruiters.

> Built for cybersecurity researchers, HR professionals, and anyone tired of fake connection requests.

---

## 🔍 What It Detects

| Signal | Description |
|---|---|
| No profile photo | Missing or blank avatar |
| Stock/AI photo suspected | Overly perfect or generic face |
| Low connections | Fewer than 30 connections |
| No activity | Zero posts or engagement |
| Generic headline | Vague titles like "Fresher" or "Enthusiast" |
| Copied bio | Templated corporate buzzword phrases |
| Experience mismatch | Claims don't match timeline |
| New account, old experience | 3-month-old account claiming 8 years experience |
| No recommendations | Zero endorsements from others |
| Suspicious username | Auto-generated looking URL slugs |
| No education | Education section completely empty |
| Inconsistent location | Location data doesn't match experience |
| Keyword-stuffed skills | Skills section spammed with buzzwords |
| Unreachable company | Company doesn't exist online |
| Contact info mismatch | Fake-looking email or phone |

---

## 🚀 Features

- **15-point heuristic scoring engine** (0–100 risk score)
- **Random Forest ML classifier** with confidence percentage
- **Interactive terminal mode** — analyze any profile manually
- **JSON file input** — batch analysis support
- **Demo mode** — test on built-in fake vs real sample profiles
- **Detailed JSON reports** auto-saved per analysis
- **Color-coded risk levels** — GREEN / YELLOW / RED

---

## 📁 Project Structure

```
DeepBait/
├── deepbait.py           # Main detector script
├── sample_profile.json   # Sample fake profile for testing
├── requirements.txt      # Dependencies
├── deepbait_model.pkl    # Auto-saved ML model (after --train)
├── reports/              # Auto-generated JSON reports
└── README.md
```

---

## ⚙️ Setup

```bash
pip install -r requirements.txt
```

---

## 🧠 Usage

```bash
# Train the Random Forest model first
python deepbait.py --train

# Demo mode — runs on 2 built-in sample profiles
python deepbait.py --demo

# Interactive mode — enter profile details manually
python deepbait.py

# Analyze from JSON file
python deepbait.py --profile sample_profile.json

# Heuristics only (no ML)
python deepbait.py --no-ml
```

---

## 📊 Output Example

<img width="1052" height="757" alt="Screenshot 2026-06-29 120350" src="https://github.com/user-attachments/assets/959a456d-6969-42d6-8d56-2e848e9a59c5" />



```
============================================================
  DEEPBAIT ANALYSIS REPORT
============================================================
  Name   : John Smith123
  URL    : linkedin.com/in/johnsmith4821

  HEURISTIC SIGNALS TRIGGERED (7/15):
    ✗ [20pts] No profile photo
    ✗ [15pts] Very few connections (<30)
    ✗ [15pts] New account but claims years of experience
    ✗ [15pts] Templated or copied bio text
    ✗ [10pts] No posts or activity
    ✗ [ 8pts] No education listed
    ✗ [ 5pts] Zero recommendations

  RISK ASSESSMENT:
    Score : 82/100  [████████████████░░░░]
    Level : HIGH

  ML PREDICTION:
    Result     : FAKE
    Confidence : 94.3%
============================================================
```

---

## 🤖 How It Works

**Phase 1 — Heuristic OSINT Analysis**
DeepBait checks 15 signals manually observable from a LinkedIn profile — no scraping required. Each signal has a weighted score; the total produces a 0–100 risk score.

**Phase 2 — Random Forest Classification**
An ML model trained on synthetic labeled data (real vs fake profiles) predicts the probability of the account being fake, giving a confidence percentage.

**Risk Levels:**
- 🟢 LOW (0–39): Likely legitimate
- 🟡 MEDIUM (40–69): Suspicious, verify manually
- 🔴 HIGH (70–100): Likely fake — do not engage

---

## ⚠️ Disclaimer

DeepBait is for **educational and research purposes only**. It does not scrape LinkedIn or violate LinkedIn's Terms of Service. All analysis is based on manually entered or publicly observable profile data. Always verify findings before taking action against any profile.

---

## 🛠️ Built With

- [scikit-learn](https://scikit-learn.org/) — Random Forest classifier
- [colorama](https://pypi.org/project/colorama/) — terminal colors
- Python standard library — json, argparse, os

---

## 👤 Author

**Aqsa** — Cybersecurity Researcher | ICE Student @ IUB  
[GitHub](https://github.com/Aqsa819) · [LinkedIn](https://linkedin.com/in/aqsa)

---

## 📄 License

MIT License
