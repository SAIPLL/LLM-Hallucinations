"""
Separate annotations by annotator based on the file editing chain.

Flow:
  File 1 (annotator 1) -> File 2 (annotator 2) -> File 3 (annotator 1)
  -> File 4 (annotator 1) -> File 5 (annotator 2) -> File 6 (final)

Logic:
  For each label column, if it was empty/NaN in the previous file and
  filled (non-empty) in the current file, the annotator who edited that
  step gets credit for that label.

Usage:
  1. Place your 6 files in the same directory as this script (or update FILENAMES below).
  2. Run: python separate_annotations.py
  3. Outputs: annotator_1_labels.csv and annotator_2_labels.csv
"""

import pandas as pd
import os
import sys

# =============================================================================
# CONFIGURATION — Update these filenames to match your actual files
# =============================================================================
FILENAMES = [
    "ds_for_annotation_og_1.csv",  # File 1
    "ds_for_annotation_Thomas_2.xlsx",  # File 2
    "ds_for_annotation_Thomas_review_Thomas_3.xlsx",  # File 3
    "ds_for_annotation_Thomas_review_batch2_Clarissa_4.xlsx",  # File 4
    "ds_for_annotation_Thomas_review_batch2_Thomas_5.xlsx",  # File 5
    "ds_for_annotation_review.csv",  # File 6 (final)
]

# The annotator responsible for each step (transition from previous file to current)
# Step 0: File 1 was created by annotator 1 (labels filled from nothing)
# Step 1: File 1 -> File 2, annotator 2 filled new labels
# Step 2: File 2 -> File 3, annotator 1 filled new labels
# Step 3: File 3 -> File 4, annotator 1 filled new labels
# Step 4: File 4 -> File 5, annotator 2 filled new labels
# Step 5: File 5 -> File 6, could be either (final merge) — adjust as needed
STEP_ANNOTATORS = [
    1,  # Step 0: File 1 created by annotator 1
    2,  # Step 1: File 1 -> File 2, annotator 2
    2,  # Step 2: File 2 -> File 3, annotator 
    1,  # Step 3: File 3 -> File 4, annotator 1
    2,  # Step 4: File 4 -> File 5, annotator 2
    1,  # Step 5: File 5 -> File 6 (final merge — see note below)
]

# Key columns to identify each annotation row
KEY_COLS = ["completion_id", "model"]

# Label columns to track
LABEL_COLS = ["caught_static_right", "caught_static_comment", "capable_static", "capable_static_comment", "caught_grammar_right", "caught_grammar_comment", "capable_grammar", "capable_grammar_comment"]

def load_and_index(filepath):
    if '.csv' in filepath:
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)
    return df.set_index(KEY_COLS)

def build_annotation_tracker(filenames, step_annotators):
    files = [load_and_index(f)[LABEL_COLS] for f in filenames]

    # Initialize trackers: who first filled each cell, and what value they wrote
    canonical_index = files[0].index
    first_annotator = pd.DataFrame(index=canonical_index, columns=LABEL_COLS, dtype=object)
    first_values    = pd.DataFrame(index=canonical_index, columns=LABEL_COLS, dtype=object)

    prev_df = None

    for step, (df, annotator) in enumerate(zip(files, step_annotators)):
        df = df.reindex(canonical_index)

        if prev_df is None:
            newly_filled = df.notna()
        else:
            prev_aligned = prev_df.reindex(canonical_index)
            newly_filled = prev_aligned.isna() & df.notna()

        # Only touch cells not yet assigned
        unassigned = first_annotator.isna()
        to_update  = newly_filled & unassigned

        first_annotator[to_update] = annotator
        first_values[to_update]    = df[to_update]

        prev_df = df

    return first_annotator.reset_index(), first_values.reset_index()

# ── Run ───────────────────────────────────────────────────────────────────────
first_annotator_df, first_values_df = build_annotation_tracker(FILENAMES, STEP_ANNOTATORS)

# ── Build a combined output with both annotator tag and value per column ──────
combined = first_values_df[KEY_COLS].copy()
for col in LABEL_COLS:
    combined[col]              = first_values_df[col]
    combined[f"{col}__by"]     = first_annotator_df[col]

# ── Split into one sheet per annotator (plus an "all" sheet) ──────────────────
all_annotators = sorted(set(STEP_ANNOTATORS))

with pd.ExcelWriter("first_annotations.xlsx", engine="openpyxl") as writer:
    # Sheet 1: everything together
    combined.to_excel(writer, sheet_name="all", index=False)

    for ann in all_annotators:
        # Rows where this annotator filled at least one label column
        mask = (first_annotator_df[LABEL_COLS] == ann).any(axis=1)
        subset_keys = first_values_df.loc[mask, KEY_COLS].copy()

        for col in LABEL_COLS:
            # Only show values this annotator was first to fill; blank otherwise
            is_this_ann = first_annotator_df.loc[mask, col] == ann
            subset_keys[col] = first_values_df.loc[mask, col].where(is_this_ann.values)

        subset_keys.to_excel(writer, sheet_name=f"annotator_{ann}", index=False)

print("Done! Saved to first_annotations.xlsx")
print(f"  Sheets: all, {', '.join(f'annotator_{a}' for a in all_annotators)}")
print(combined.head())