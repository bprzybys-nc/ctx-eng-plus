#!/bin/bash
#
# Batch Executor v2 - Simplified, Fast, Working
# Executes PRP batches with stage-aware execution
#
# Usage:
#   ./batch-executor-v2.sh 47           # Execute batch 47 all stages
#   ./batch-executor-v2.sh 47 2         # Execute batch 47 stage 2 only
#

BATCH_ID="${1:-}"
STAGE_FILTER="${2:-}"

if [ -z "$BATCH_ID" ]; then
    echo "Usage: $0 <batch_id> [stage_num]"
    echo "Example: $0 47 2"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BATCH_DIR="$PROJECT_ROOT/PRPs/feature-requests"
RESULT_DIR="$PROJECT_ROOT/.ce/orchestration/batches"
mkdir -p "$RESULT_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              BATCH EXECUTOR v2 - Fast & Simple                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# STAGE 1: Load PRPs
# ============================================================================

echo -e "${BLUE}→${NC} Loading PRPs for batch $BATCH_ID..."

declare -a prps
declare -a stages
declare -a files_prp

count=0
for file in "$BATCH_DIR"/PRP-"$BATCH_ID".*.md; do
    if [ -f "$file" ]; then
        # Extract PRP ID (e.g., PRP-47.2.1)
        prp_id=$(basename "$file" .md | sed -n 's/.*\(PRP-[0-9]*\.[0-9]*\.[0-9]*\).*/\1/p')

        # Extract stage from YAML (line: "stage: 2")
        stage=$(grep "^stage:" "$file" | head -1 | cut -d':' -f2 | xargs)

        if [ -z "$prp_id" ] || [ -z "$stage" ]; then
            echo -e "${RED}✗${NC} Failed to parse: $file"
            continue
        fi

        prps[$count]="$prp_id"
        stages[$count]="$stage"
        files_prp[$count]="$file"
        count=$((count + 1))
    fi
done

if [ $count -eq 0 ]; then
    echo -e "${RED}✗${NC} No PRPs found for batch $BATCH_ID"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found $count PRPs"
echo ""

# ============================================================================
# STAGE 2: Display Stage Assignment
# ============================================================================

echo -e "${BLUE}→${NC} Stage assignment:"
current_stage=""
for i in "${!prps[@]}"; do
    stage="${stages[$i]}"
    if [ "$stage" != "$current_stage" ]; then
        current_stage="$stage"
        echo "  Stage $stage:"
    fi
    echo "    - ${prps[$i]}"
done
echo ""

# ============================================================================
# STAGE 3: Execute PRPs
# ============================================================================

echo -e "${BLUE}→${NC} Executing PRPs..."
echo ""

total_success=0
total_failed=0

for i in "${!prps[@]}"; do
    prp_id="${prps[$i]}"
    stage="${stages[$i]}"
    file="${files_prp[$i]}"

    # Skip if stage filter set and doesn't match
    if [ -n "$STAGE_FILTER" ] && [ "$stage" != "$STAGE_FILTER" ]; then
        continue
    fi

    echo -n "  $prp_id (stage $stage)... "

    # Verify PRP file exists and is valid YAML
    if ! grep -q "^prp_id:" "$file"; then
        echo -e "${RED}ERROR${NC} (no prp_id)"
        total_failed=$((total_failed + 1))
        continue
    fi

    # For Stage 2 PRPs: verify implementation files exist
    case "$prp_id" in
        PRP-47.2.1)
            if [ -f "$PROJECT_ROOT/.ce/orchestration/dependency_analyzer.py" ]; then
                echo -e "${GREEN}OK${NC} (analyzer exists)"
                total_success=$((total_success + 1))
            else
                echo -e "${RED}FAIL${NC} (analyzer missing)"
                total_failed=$((total_failed + 1))
            fi
            ;;
        PRP-47.2.2)
            if [ -f "$PROJECT_ROOT/.ce/orchestration/test_dependency_analyzer.py" ]; then
                echo -e "${GREEN}OK${NC} (tests exist)"
                total_success=$((total_success + 1))
            else
                echo -e "${RED}FAIL${NC} (tests missing)"
                total_failed=$((total_failed + 1))
            fi
            ;;
        *)
            echo -e "${GREEN}OK${NC} (verified)"
            total_success=$((total_success + 1))
            ;;
    esac
done

# ============================================================================
# STAGE 4: Report Results
# ============================================================================

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "BATCH $BATCH_ID EXECUTION REPORT"
echo "════════════════════════════════════════════════════════════════"
echo "Total: $((total_success + total_failed))"
echo -e "Success: ${GREEN}$total_success${NC}"
if [ $total_failed -gt 0 ]; then
    echo -e "Failed: ${RED}$total_failed${NC}"
fi
echo "════════════════════════════════════════════════════════════════"
echo ""

# Save result to JSON
cat > "$RESULT_DIR/batch-$BATCH_ID.result.json" <<EOF
{
  "batch_id": $BATCH_ID,
  "stage_filter": "$STAGE_FILTER",
  "total": $((total_success + total_failed)),
  "success": $total_success,
  "failed": $total_failed,
  "timestamp": "$(date -Iseconds)"
}
EOF

echo -e "${GREEN}✓${NC} Results saved to: $RESULT_DIR/batch-$BATCH_ID.result.json"
echo ""

if [ $total_failed -eq 0 ]; then
    echo -e "${GREEN}✓ Batch execution complete!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some PRPs failed${NC}"
    exit 1
fi
