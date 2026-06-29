#!/usr/bin/env python3
"""
DeepBait - Fake LinkedIn Profile Detector (OSINT + ML)
Author: Aqsa
GitHub: https://github.com/Aqsa819/DeepBait
"""

import json
import os
import sys
import argparse
import random
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = CYAN = WHITE = MAGENTA = BLUE = ""
    class Style:
        BRIGHT = RESET_ALL = ""

REPORT_DIR = "reports"
MODEL_FILE = "deepbait_model.pkl"

# ─── Banner ──────────────────────────────────────────────────────────────────

def banner():
    print(f"""{Fore.CYAN}{Style.BRIGHT}
  ██████  ███████ ███████ ██████  ██████   █████  ██ ████████
  ██   ██ ██      ██      ██   ██ ██   ██ ██   ██ ██    ██
  ██   ██ █████   █████   ██████  ██████  ███████ ██    ██
  ██   ██ ██      ██      ██      ██   ██ ██   ██ ██    ██
  ██████  ███████ ███████ ██      ██████  ██   ██ ██    ██
{Style.RESET_ALL}
{Fore.YELLOW}  [*] Fake LinkedIn Profile Detector — OSINT + ML
  [*] Detects bots, fake recruiters, and sockpuppet accounts
{Style.RESET_ALL}""")

# ─── Heuristic Scoring Engine ────────────────────────────────────────────────

SIGNALS = {
    "no_profile_photo":         {"weight": 20, "desc": "No profile photo"},
    "stock_photo_suspected":    {"weight": 15, "desc": "Stock/AI-generated photo suspected"},
    "low_connections":          {"weight": 15, "desc": "Very few connections (<30)"},
    "no_activity":              {"weight": 10, "desc": "No posts or activity"},
    "generic_headline":         {"weight": 10, "desc": "Generic/vague headline"},
    "copied_bio":               {"weight": 15, "desc": "Templated or copied bio text"},
    "experience_mismatch":      {"weight": 10, "desc": "Experience doesn't match education timeline"},
    "new_account_old_exp":      {"weight": 15, "desc": "New account but claims years of experience"},
    "no_recommendations":       {"weight": 5,  "desc": "Zero recommendations"},
    "suspicious_username":      {"weight": 10, "desc": "Username looks auto-generated"},
    "no_education":             {"weight": 8,  "desc": "No education listed"},
    "multiple_locations":       {"weight": 12, "desc": "Inconsistent location info"},
    "keyword_stuffed_skills":   {"weight": 8,  "desc": "Skills section is keyword-stuffed"},
    "unreachable_company":      {"weight": 12, "desc": "Company listed doesn't exist online"},
    "contact_info_mismatch":    {"weight": 10, "desc": "Contact info looks fake or mismatched"},
}

def calculate_risk_score(signals_triggered):
    """Calculate 0-100 fake probability score from triggered signals."""
    total_possible = sum(s["weight"] for s in SIGNALS.values())
    triggered_weight = sum(SIGNALS[s]["weight"] for s in signals_triggered if s in SIGNALS)
    score = min(100, int((triggered_weight / total_possible) * 100 * 1.5))
    return score

def get_risk_level(score):
    if score >= 70:
        return "HIGH", Fore.RED
    elif score >= 40:
        return "MEDIUM", Fore.YELLOW
    else:
        return "LOW", Fore.GREEN

# ─── Profile Input ───────────────────────────────────────────────────────────

def get_profile_interactive():
    """Collect profile info via interactive terminal prompts."""
    print(f"\n{Fore.CYAN}[*] Enter LinkedIn Profile Details (press Enter to skip){Style.RESET_ALL}\n")

    profile = {}
    profile["name"] = input(f"{Fore.WHITE}  Full Name          : {Style.RESET_ALL}").strip()
    profile["url"] = input(f"{Fore.WHITE}  LinkedIn URL       : {Style.RESET_ALL}").strip()
    profile["headline"] = input(f"{Fore.WHITE}  Headline/Title     : {Style.RESET_ALL}").strip()
    profile["connections"] = input(f"{Fore.WHITE}  Connections count  : {Style.RESET_ALL}").strip()
    profile["account_age_years"] = input(f"{Fore.WHITE}  Account age (years): {Style.RESET_ALL}").strip()
    profile["exp_years"] = input(f"{Fore.WHITE}  Experience claimed (years): {Style.RESET_ALL}").strip()
    profile["has_photo"] = input(f"{Fore.WHITE}  Has profile photo? (y/n): {Style.RESET_ALL}").strip().lower()
    profile["has_posts"] = input(f"{Fore.WHITE}  Has posts/activity? (y/n): {Style.RESET_ALL}").strip().lower()
    profile["has_education"] = input(f"{Fore.WHITE}  Has education listed? (y/n): {Style.RESET_ALL}").strip().lower()
    profile["has_recommendations"] = input(f"{Fore.WHITE}  Has recommendations? (y/n): {Style.RESET_ALL}").strip().lower()
    profile["bio"] = input(f"{Fore.WHITE}  Paste bio/about text: {Style.RESET_ALL}").strip()
    profile["company"] = input(f"{Fore.WHITE}  Current company    : {Style.RESET_ALL}").strip()

    return profile

def load_profile_json(path):
    with open(path, "r") as f:
        return json.load(f)

# ─── Analyze Profile ─────────────────────────────────────────────────────────

GENERIC_HEADLINES = [
    "looking for opportunities", "open to work", "student", "fresher",
    "professional", "enthusiast", "specialist", "expert", "guru", "ninja"
]

COPIED_BIO_PHRASES = [
    "results-driven professional", "passionate about", "dynamic team player",
    "proven track record", "leverage synergies", "thought leader",
    "go-getter", "detail-oriented", "self-starter", "hardworking individual"
]

SUSPICIOUS_USERNAME_PATTERNS = [
    lambda u: any(char.isdigit() for char in u[-4:]),  # ends in numbers
    lambda u: len(u.replace("-", "").replace(".", "")) < 5,  # too short
    lambda u: u.count("-") > 2,  # too many hyphens
]

def analyze_profile(profile):
    """Run all heuristic checks and return triggered signals."""
    triggered = []
    notes = []

    # Photo check
    if profile.get("has_photo", "y") == "n":
        triggered.append("no_profile_photo")

    # Connections check
    try:
        conns = int(profile.get("connections", 500))
        if conns < 30:
            triggered.append("low_connections")
            notes.append(f"Only {conns} connections")
    except ValueError:
        pass

    # Activity check
    if profile.get("has_posts", "y") == "n":
        triggered.append("no_activity")

    # Education check
    if profile.get("has_education", "y") == "n":
        triggered.append("no_education")

    # Recommendations
    if profile.get("has_recommendations", "y") == "n":
        triggered.append("no_recommendations")

    # Headline check
    headline = profile.get("headline", "").lower()
    if any(phrase in headline for phrase in GENERIC_HEADLINES):
        triggered.append("generic_headline")
        notes.append(f"Generic headline: '{profile.get('headline', '')}'")

    # Bio analysis
    bio = profile.get("bio", "").lower()
    if bio:
        matches = [p for p in COPIED_BIO_PHRASES if p in bio]
        if len(matches) >= 2:
            triggered.append("copied_bio")
            notes.append(f"Copied phrases found: {matches[:3]}")

    # New account + old experience mismatch
    try:
        acc_age = float(profile.get("account_age_years", 5))
        exp_years = float(profile.get("exp_years", 0))
        if acc_age < 1 and exp_years > 3:
            triggered.append("new_account_old_exp")
            notes.append(f"Account only {acc_age}yr old but claims {exp_years}yr experience")
    except ValueError:
        pass

    # Username check
    url = profile.get("url", "")
    if url:
        username = url.rstrip("/").split("/")[-1]
        if any(check(username) for check in SUSPICIOUS_USERNAME_PATTERNS):
            triggered.append("suspicious_username")
            notes.append(f"Suspicious username pattern: {username}")

    return triggered, notes

# ─── ML Model ────────────────────────────────────────────────────────────────

def build_feature_vector(profile, triggered_signals):
    """Convert profile to numeric feature vector for ML."""
    try:
        connections = int(profile.get("connections", 500))
    except ValueError:
        connections = 500

    try:
        acc_age = float(profile.get("account_age_years", 3))
    except ValueError:
        acc_age = 3

    try:
        exp_years = float(profile.get("exp_years", 0))
    except ValueError:
        exp_years = 0

    return [
        1 if profile.get("has_photo", "y") == "n" else 0,
        min(connections, 500) / 500,
        1 if profile.get("has_posts", "y") == "n" else 0,
        1 if profile.get("has_education", "y") == "n" else 0,
        1 if profile.get("has_recommendations", "y") == "n" else 0,
        min(acc_age, 10) / 10,
        min(exp_years, 20) / 20,
        len(triggered_signals) / len(SIGNALS),
    ]

def train_model():
    """Train Random Forest on synthetic labeled dataset."""
    import pickle
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report

    print(f"{Fore.YELLOW}[*] Generating synthetic training data...")

    # Synthetic data: [no_photo, connections_norm, no_posts, no_edu, no_rec, acc_age_norm, exp_norm, signal_ratio]
    # Label: 1 = fake, 0 = real
    real_profiles = [
        [0, random.uniform(0.3, 1.0), 0, 0, 0, random.uniform(0.3, 1.0), random.uniform(0.1, 0.5), random.uniform(0, 0.2)]
        for _ in range(300)
    ]
    fake_profiles = [
        [random.choice([0, 1]), random.uniform(0, 0.1), random.choice([0, 1]),
         random.choice([0, 1]), 1, random.uniform(0, 0.2), random.uniform(0.3, 0.9), random.uniform(0.4, 1.0)]
        for _ in range(300)
    ]

    X = np.array(real_profiles + fake_profiles)
    y = np.array([0] * 300 + [1] * 300)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print(f"\n{Fore.GREEN}[+] Model Performance:")
    print(classification_report(y_test, model.predict(X_test),
                                 target_names=["Real", "Fake"]))

    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)
    print(f"{Fore.GREEN}[+] Model saved: {MODEL_FILE}")
    return model

def load_model():
    import pickle
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, "rb") as f:
            return pickle.load(f)
    return None

def ml_predict(model, features):
    import numpy as np
    pred = model.predict([features])[0]
    prob = model.predict_proba([features])[0][1]
    return pred, prob

# ─── Report Generator ────────────────────────────────────────────────────────

def generate_report(profile, triggered, notes, score, risk_level, ml_result=None):
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_slug = profile.get("name", "unknown").replace(" ", "_").lower()
    report_path = os.path.join(REPORT_DIR, f"deepbait_{name_slug}_{ts}.json")

    report = {
        "timestamp": datetime.now().isoformat(),
        "profile": profile,
        "triggered_signals": triggered,
        "signal_details": [SIGNALS[s]["desc"] for s in triggered if s in SIGNALS],
        "analyst_notes": notes,
        "heuristic_score": score,
        "risk_level": risk_level,
        "ml_prediction": ml_result,
    }

    # Convert numpy types to native Python for JSON serialization
    def convert(obj):
        import numpy as np
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, (np.ndarray,)): return obj.tolist()
        raise TypeError(f"Not serializable: {type(obj)}")

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=convert)

    return report_path

# ─── Display Results ─────────────────────────────────────────────────────────

def display_results(profile, triggered, notes, score, risk_level, color, ml_result=None):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"  DEEPBAIT ANALYSIS REPORT")
    print(f"{'='*60}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Name   : {Fore.YELLOW}{profile.get('name', 'N/A')}")
    print(f"  {Fore.WHITE}URL    : {Fore.CYAN}{profile.get('url', 'N/A')}")
    print(f"\n{Fore.CYAN}  HEURISTIC SIGNALS TRIGGERED ({len(triggered)}/{len(SIGNALS)}):{Style.RESET_ALL}")

    if triggered:
        for sig in triggered:
            desc = SIGNALS.get(sig, {}).get("desc", sig)
            weight = SIGNALS.get(sig, {}).get("weight", 0)
            print(f"  {Fore.RED}  ✗ [{weight:>2}pts] {desc}")
    else:
        print(f"  {Fore.GREEN}  ✓ No suspicious signals detected")

    if notes:
        print(f"\n{Fore.CYAN}  ANALYST NOTES:{Style.RESET_ALL}")
        for note in notes:
            print(f"  {Fore.YELLOW}  • {note}")

    print(f"\n{Fore.CYAN}  RISK ASSESSMENT:{Style.RESET_ALL}")
    bar_filled = int(score / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    print(f"  {color}  Score : {score}/100  [{bar}]")
    print(f"  {color}  Level : {risk_level}{Style.RESET_ALL}")

    if ml_result:
        pred, prob = ml_result
        ml_label = "FAKE" if pred == 1 else "REAL"
        ml_color = Fore.RED if pred == 1 else Fore.GREEN
        print(f"\n{Fore.CYAN}  ML PREDICTION:{Style.RESET_ALL}")
        print(f"  {ml_color}  Result     : {ml_label}")
        print(f"  {ml_color}  Confidence : {prob*100:.1f}%{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

# ─── Demo Mode ───────────────────────────────────────────────────────────────

DEMO_PROFILES = [
    {
        "name": "John Smith123",
        "url": "linkedin.com/in/johnsmith4821",
        "headline": "Looking for opportunities | Fresher | Enthusiast",
        "connections": "12",
        "account_age_years": "0.3",
        "exp_years": "5",
        "has_photo": "n",
        "has_posts": "n",
        "has_education": "n",
        "has_recommendations": "n",
        "bio": "Results-driven professional with a proven track record. Passionate about leveraging synergies.",
        "company": "XYZ Global Solutions"
    },
    {
        "name": "Sara Ahmed",
        "url": "linkedin.com/in/sara-ahmed-pk",
        "headline": "Software Engineer at Google | CS Graduate",
        "connections": "842",
        "account_age_years": "4",
        "exp_years": "3",
        "has_photo": "y",
        "has_posts": "y",
        "has_education": "y",
        "has_recommendations": "y",
        "bio": "Building scalable backend systems. Love open source and contributing to the community.",
        "company": "Google"
    }
]

def run_demo(model):
    print(f"\n{Fore.YELLOW}[*] Running DEMO mode on 2 sample profiles...\n")
    for i, profile in enumerate(DEMO_PROFILES):
        print(f"{Fore.CYAN}[*] Analyzing Profile {i+1}: {profile['name']}{Style.RESET_ALL}")
        triggered, notes = analyze_profile(profile)
        score = calculate_risk_score(triggered)
        risk_level, color = get_risk_level(score)

        ml_result = None
        if model:
            features = build_feature_vector(profile, triggered)
            ml_result = ml_predict(model, features)

        display_results(profile, triggered, notes, score, risk_level, color, ml_result)
        report_path = generate_report(profile, triggered, notes, score, risk_level, ml_result)
        print(f"{Fore.GREEN}[+] Report saved: {report_path}\n")

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    banner()

    parser = argparse.ArgumentParser(description="DeepBait — Fake LinkedIn Profile Detector")
    parser.add_argument("--demo", action="store_true", help="Run demo on sample profiles")
    parser.add_argument("--train", action="store_true", help="Train Random Forest model")
    parser.add_argument("--profile", metavar="JSON", help="Analyze a profile from JSON file")
    parser.add_argument("--no-ml", action="store_true", help="Skip ML prediction (heuristics only)")
    args = parser.parse_args()

    # Train mode
    if args.train:
        train_model()
        return

    # Load model
    model = None
    if not args.no_ml:
        model = load_model()
        if not model:
            print(f"{Fore.YELLOW}[!] No ML model found. Run --train first for ML predictions.")
            print(f"{Fore.YELLOW}    Running heuristics only...\n")

    # Demo mode
    if args.demo:
        run_demo(model)
        return

    # JSON file mode
    if args.profile:
        profile = load_profile_json(args.profile)
    else:
        # Interactive mode
        profile = get_profile_interactive()

    # Analyze
    print(f"\n{Fore.CYAN}[*] Analyzing profile...{Style.RESET_ALL}")
    triggered, notes = analyze_profile(profile)
    score = calculate_risk_score(triggered)
    risk_level, color = get_risk_level(score)

    ml_result = None
    if model:
        features = build_feature_vector(profile, triggered)
        ml_result = ml_predict(model, features)

    display_results(profile, triggered, notes, score, risk_level, color, ml_result)

    report_path = generate_report(profile, triggered, notes, score, risk_level, ml_result)
    print(f"{Fore.GREEN}[+] Report saved: {report_path}")

if __name__ == "__main__":
    main()
