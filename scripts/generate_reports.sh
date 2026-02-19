#!/bin/bash
# =============================================================================
# generate_reports.sh
# Full quality analysis suite for the Reservation System.
#
# Tools: flake8, pylint and coverage (unittest)
#
# Usage:
#   ./scripts/generate_reports.sh              # Analyze all src/ files
#   ./scripts/generate_reports.sh src/hotel.py # Analyze a single file
#
# Author: A00841954 Christian Erick Mercado Flores
# Date: February 2026
# =============================================================================

# Paths
REPORT_DIR="results/reports"
COVERAGE_DIR="results/coverage"
TIMESTAMP=$(date "+%Y-%m-%d_%H-%M-%S")
SUMMARY_FILE="${REPORT_DIR}/summary_${TIMESTAMP}.txt"

mkdir -p "$REPORT_DIR" "$COVERAGE_DIR"

# Target selection
if [ $# -eq 0 ]; then
    TARGET="src/"
    LABEL="all"
else
    TARGET="$1"
    LABEL=$(basename "$TARGET" .py)
fi