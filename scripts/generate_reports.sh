#!/bin/bash
# =============================================================================
# generate_reports.sh
# Full quality analysis suite for the Reservation System.
#
# Tools: flake8, pylint and coverage (unittest)
#
# Usage:
#   ./scripts/generate_reports.sh              Analyze all src/ files
#   ./scripts/generate_reports.sh src/hotel.py Analyze a single file
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
SUMMARY_FILE="${REPORT_DIR}/summary.txt"

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
    echo -e "${CYAN}${BOLD}========================================${RESET}"
    echo -e "${CYAN}${BOLD}  $title${RESET}"
    echo -e "${CYAN}${BOLD}========================================${RESET}"
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

FLAKE8_REPORT="${REPORT_DIR}/${LABEL}_flake8.txt"

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

# Pylint
section "2. Pylint  (Static analysis)"

PYLINT_REPORT="${REPORT_DIR}/${LABEL}_pylint.txt"

{
echo "Pylint Report"
echo "Date   : $(date)"
echo "Target : $TARGET"
echo "------------------------------------------------------------"
} | tee "$PYLINT_REPORT"

if require_tool pylint pylint; then
    PYLINT_OUT=$(pylint "$TARGET" \
        2>&1 || true)

    echo "$PYLINT_OUT" | tee -a "$PYLINT_REPORT"

    PYLINT_SCORE=$(echo "$PYLINT_OUT" | awk '/rated at/ {print $7; exit}')
    PYLINT_SCORE=${PYLINT_SCORE:-N/A}

    echo ""
    if [[ "$PYLINT_SCORE" == 10* ]]; then
        echo -e "${GREEN}Pylint score: $PYLINT_SCORE${RESET}"
        echo "Pylint : PASS — $PYLINT_SCORE" >> "$SUMMARY_FILE"
    else
        echo -e "${YELLOW}Pylint score: $PYLINT_SCORE${RESET}"
        echo "Pylint : $PYLINT_SCORE" >> "$SUMMARY_FILE"
    fi
else
    echo "Pylint : SKIPPED (not installed)" >> "$SUMMARY_FILE"
fi

# Coverage
section "3. Coverage  (unittest & line coverage)"

COVERAGE_REPORT="${REPORT_DIR}/${LABEL}_coverage.txt"

if require_tool coverage "coverage[toml]"; then
    coverage run -m unittest discover -s tests/unit 2>&1 \
        | tee "$COVERAGE_REPORT"

    echo "" | tee -a "$COVERAGE_REPORT"
    coverage report --show-missing 2>&1 | tee -a "$COVERAGE_REPORT"
    coverage html -d "$COVERAGE_DIR/html" 2>/dev/null || true
    coverage xml  -o "$COVERAGE_DIR/coverage.xml" 2>/dev/null || true

    COVERAGE_TOTAL=$(coverage report 2>/dev/null \
        | grep "TOTAL" | awk '{print $NF}' || echo "N/A")

    echo ""
    if [ "$COVERAGE_TOTAL" != "N/A" ]; then
        COVERAGE_NUM=$(echo "$COVERAGE_TOTAL" | tr -d '%')
        if [ "$COVERAGE_NUM" -ge 85 ] 2>/dev/null; then
            echo -e "${GREEN}Coverage: $COVERAGE_TOTAL (≥85% — PASS)${RESET}"
            echo "Coverage: PASS — $COVERAGE_TOTAL" >> "$SUMMARY_FILE"
        else
            echo -e "${RED}Coverage: $COVERAGE_TOTAL (<85% — FAIL)${RESET}"
            echo "Coverage: FAIL — $COVERAGE_TOTAL" >> "$SUMMARY_FILE"
            GLOBAL_EXIT=1
        fi
    fi
else
    echo "Coverage : SKIPPED (not installed)" >> "$SUMMARY_FILE"
fi

# Final summary
section "Summary"
cat "$SUMMARY_FILE"

echo ""
if [ "$GLOBAL_EXIT" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}All checks passed. Reports saved to: $REPORT_DIR${RESET}"
else
    echo -e "${YELLOW}${BOLD}Some checks reported issues. Review reports in: $REPORT_DIR${RESET}"
fi

exit "$GLOBAL_EXIT"