"""
Inter-Annotator Agreement Calculator
=====================================
Computes Cohen's Kappa, Percentage Agreement, and Confusion Matrices
for two annotators across 8 categorical columns.

Expected file structure:
  - One row per item
  - Columns named like: column_annotator1, column_annotator2
    OR the script lets you map column pairs manually below.

Usage:
  1. Set FILE_PATH to your CSV or Excel file
  2. Set COLUMN_PAIRS to map annotator1 col -> annotator2 col
  3. Set YES_NO_NA_COLS and MULTI_COLS accordingly
  4. Run: python inter_annotator_agreement.py
"""

import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score, confusion_matrix
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIGURATION — Edit these to match your file
# ─────────────────────────────────────────────

FILE_PATH = "merged_annotations_v1.xlsx"   # or "your_file.xlsx"

# Map each column from annotator 1 to its matching annotator 2 column
# Format: ("annotator1_col_name", "annotator2_col_name")
COLUMN_PAIRS = [
    # Yes/No/NA columns
    ("caught_static_right_ann1", "caught_static_right_ann2"),
    ("capable_static_ann1", "capable_static_ann2"),
    ("caught_grammar_right_ann1", "caught_grammar_right_ann2"),
    ("capable_grammar_ann1", "capable_grammar_ann2"),
    # Library/Library-Flow/Lambda/Lambda-Library-Flow columns
    ("caught_static_comment_ann1", "caught_static_comment_ann2"),
    ("capable_static_comment_ann1", "capable_static_comment_ann2"),
    ("caught_grammar_comment_ann1", "caught_grammar_comment_ann2"),
    ("capable_grammar_comment_ann1", "capable_grammar_comment_ann2")
]

# Friendly display names for each column pair (same order as COLUMN_PAIRS)
COL_DISPLAY_NAMES = [
    "Caught Static (Yes/No/NA)",
    "Capable Static (Yes/No/NA)",
    "Caught Grammar (Yes/No/NA)",
    "Capable Grammar (Yes/No/NA)",
    "Caught Static Reason (Library types)",
    "Capable Static Reason (Library types)",
    "Caught Grammar Reason (Library types)",
    "Capable Grammar Reason (Library types)",
]

# Category definitions (for ordering in confusion matrices)
YES_NO_NA_CATS   = ["Yes", "No", "nan"]
LIBRARY_CATS     = ['nan','data-test','data-flow-logic','flow-scope','flow-test','data-flow-lambda', 'logic-valid','data','flow-valid', 'flow-logic','error-test','environment', 'flow-lambda-scope','flow-lambda','flow', 'environment-library','ambiguous-test', 'library-valid','test', 'data-library','lambda-scope','library','flow-lambda-library','flow-library','flow-library-test','data-logic','data-error-test']
# Which columns use which category set (by index in COLUMN_PAIRS, 0-based)
YES_NO_NA_IDX  = [2, 4, 6, 8]
LIBRARY_IDX    = [3, 5, 7, 9]

# ─────────────────────────────────────────────
# LOAD FILE
# ─────────────────────────────────────────────

def load_file(path):
    if path.endswith(".xlsx") or path.endswith(".xls"):
        return pd.read_excel(path)
    return pd.read_csv(path)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def percentage_agreement(y1, y2):
    return round(100 * np.mean(np.array(y1) == np.array(y2)), 2)

def kappa(y1, y2, labels):
    # Filter out rows where either annotator has NaN
    mask = pd.notna(y1) & pd.notna(y2)
    y1_clean = list(y1[mask])
    y2_clean = list(y2[mask])
    if len(y1_clean) < 2:
        return None, 0
    k = cohen_kappa_score(y1_clean, y2_clean)
    return round(k, 4), len(y1_clean)

def interpret_kappa(k):
    if k is None:   return "N/A"
    if k < 0:       return "Poor (worse than chance)"
    if k < 0.20:    return "Slight"
    if k < 0.40:    return "Fair"
    if k < 0.60:    return "Moderate"
    if k < 0.80:    return "Substantial"
    return "Almost Perfect"

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    df = load_file(FILE_PATH)
    print(f"\n{'='*65}")
    print(f"  Inter-Annotator Agreement Report")
    print(f"  File: {FILE_PATH}  |  Rows: {len(df)}")
    print(f"{'='*65}\n")

    summary_rows = []
    kappas = []

    for i, ((col1, col2), name) in enumerate(zip(COLUMN_PAIRS, COL_DISPLAY_NAMES)):
        labels = YES_NO_NA_CATS if i in YES_NO_NA_IDX else LIBRARY_CATS

        y1 = df[col1].astype(str).str.strip()
        y2 = df[col2].astype(str).str.strip()

        # Replace string 'nan' back to actual NaN
        y1 = y1.replace("nan", np.nan)
        y2 = y2.replace("nan", np.nan)

        # For percentage agreement, use only non-NaN rows
        mask = pd.notna(y1) & pd.notna(y2)
        pa = percentage_agreement(y1[mask], y2[mask])

        k, n = kappa(y1, y2, labels)
        interp = interpret_kappa(k)

        if k is not None:
            kappas.append(k)

        summary_rows.append({
            "Column": name,
            "N (valid pairs)": n,
            "% Agreement": pa,
            "Cohen's Kappa": k if k is not None else "N/A",
            "Interpretation": interp,
        })

        # ── Per-column detail ──
        print(f"── {name} ──")
        print(f"   Valid pairs     : {n}")
        print(f"   % Agreement     : {pa}%")
        print(f"   Cohen's Kappa   : {k}  →  {interp}")
        print()

    # ── Summary table ──
    print(f"\n{'='*65}")
    print("  SUMMARY TABLE")
    print(f"{'='*65}")
    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))

    # ── Overall / average kappa ──
    if kappas:
        avg_k = round(np.mean(kappas), 4)
        print(f"\n  Average Cohen's Kappa (across all columns): {avg_k}  →  {interpret_kappa(avg_k)}")

    print(f"\n{'='*65}\n")

    # ── Save summary to CSV ──
    out_csv = "iaa_summary.csv"
    summary_df.to_csv(out_csv, index=False)
    print(f"  Summary saved to: {out_csv}\n")


if __name__ == "__main__":
    main()