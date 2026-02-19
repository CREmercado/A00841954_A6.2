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

set -euo pipefail

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

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

# Section header
section() {
    local title="$1"
    echo ""
    echo -e "${CYAN}${BOLD}════════════════════════════════════════${RESET}"
    echo -e "${CYAN}${BOLD}  $title${RESET}"
    echo -e "${CYAN}${BOLD}════════════════════════════════════════${RESET}"
}

# Helper: check tool availability
require_tool() {
    if ! command -v "$1" &>/dev/null; then
        echo -e "${RED}[MISSING] '$1' not found. Install with: pip install $2${RESET}"
        return 1
    fi
}

# Summary accumulator
{
echo "============================================================"
echo "  Quality Analysis Report — Reservation System"
echo "  Generated : $(date)"
echo "  Target    : $TARGET"
echo "============================================================"
} > "$SUMMARY_FILE"

GLOBAL_EXIT=0

# Flake8
section "1. Flake8 Report"

FLAKE8_REPORT="${REPORT_DIR}/${LABEL}_flake8_${TIMESTAMP}.txt"

{
echo "Flake8 Report"
echo "Date   : $(date)"
echo "Target : $TARGET"
echo "------------------------------------------------------------"
} | tee "$FLAKE8_REPORT"

if require_tool flake8 flake8; then
    FLAKE8_OUT=$(flake8 "$TARGET" \
        --statistics \
        --count 2>&1 || true)

    if [ -z "$FLAKE8_OUT" ]; then
        echo -e "${GREEN}No flake8 issues found.${RESET}" | tee -a "$FLAKE8_REPORT"
        echo "Flake8 : PASS — 0 issues" >> "$SUMMARY_FILE"
    else
        echo "$FLAKE8_OUT" | tee -a "$FLAKE8_REPORT"
        ISSUE_COUNT=$(echo "$FLAKE8_OUT" | grep -c "^" || true)
        echo -e "${RED}Issues found: $ISSUE_COUNT${RESET}"
        echo "Flake8 : FAIL — $ISSUE_COUNT issue(s)" >> "$SUMMARY_FILE"
        GLOBAL_EXIT=1
    fi
else
    echo "Flake8 : SKIPPED (not installed)" >> "$SUMMARY_FILE"
fi