# Split into FILE_part1.txt and FILE_part2.txt
FILE=${1}
echo "Splitting $FILE into two parts."
TOTAL=$(wc -l < "$FILE")
HALF=$(( (TOTAL + 1) / 2 ))
head -n "$HALF" "$FILE" > "${FILE%.txt}_part1.txt"
tail -n "$(( TOTAL - HALF ))" "$FILE" > "${FILE%.txt}_part2.txt"

# Optional: verify line counts
wc -l "$FILE" "${FILE%.txt}_part1.txt" "${FILE%.txt}_part2.txt"