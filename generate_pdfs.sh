#!/bin/bash
# Script to generate PDFs for all presentations

echo "Generating PDFs for all presentations..."

for i in {01..06}; do
  echo "Processing pract_$i..."
  npx @marp-team/marp-cli pract_$i/presentation/slides.md --pdf --output pract_$i/presentation/slides.pdf
  if [ $? -eq 0 ]; then
    echo "✓ pract_$i/presentation/slides.pdf generated successfully"
  else
    echo "✗ Error generating pract_$i/presentation/slides.pdf"
  fi
done

echo "Done!"
