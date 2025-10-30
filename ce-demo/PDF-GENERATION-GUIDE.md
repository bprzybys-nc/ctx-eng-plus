# PDF Generation Guide

**How to convert TUTORIAL-PDF.md to beautiful PDF**

---

## Quick Start (Recommended: Pandoc)

### Install Pandoc (One-time)

**macOS:**
```bash
brew install pandoc
brew install --cask basictex  # LaTeX for PDF generation
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install pandoc texlive-latex-base texlive-fonts-recommended texlive-fonts-extra
```

**Windows:**
Download from https://pandoc.org/installing.html

### Generate PDF

```bash
cd ce-demo

pandoc TUTORIAL-PDF.md \
  -o TUTORIAL.pdf \
  --pdf-engine=xelatex \
  -V geometry:landscape \
  -V geometry:margin=0.5in \
  -V fontsize=10pt \
  -V columns=2 \
  --toc \
  --toc-depth=2 \
  --highlight-style=tango

# Result: TUTORIAL.pdf (landscape, 2-column, modern fonts)
```

---

## Method 1: Pandoc (Best Quality)

### Basic Command

```bash
pandoc TUTORIAL-PDF.md -o TUTORIAL.pdf --pdf-engine=xelatex
```

### Advanced Command (Recommended)

```bash
pandoc TUTORIAL-PDF.md \
  -o TUTORIAL.pdf \
  --pdf-engine=xelatex \
  -V geometry:landscape \
  -V geometry:margin=0.5in \
  -V fontsize=10pt \
  -V columns=2 \
  -V mainfont="Helvetica" \
  -V sansfont="Helvetica" \
  -V monofont="Menlo" \
  --toc \
  --toc-depth=2 \
  --number-sections \
  --highlight-style=tango \
  --pdf-engine-opt=-shell-escape

# Creates: Professional 2-column landscape PDF
```

### Customize Options

**Page Layout:**
```bash
-V geometry:landscape          # Landscape orientation
-V geometry:margin=0.5in       # Minimal margins (0.5 inch)
-V geometry:margin=1cm         # Or use centimeters
-V papersize:a4                # A4 paper (default: letter)
```

**Fonts:**
```bash
-V mainfont="Helvetica"        # Main text font
-V sansfont="Arial"            # Sans-serif font
-V monofont="Courier New"      # Code blocks font
-V fontsize=10pt               # Font size (8pt, 10pt, 11pt, 12pt)
```

**Columns:**
```bash
-V columns=2                   # Two-column layout
-V columns=1                   # Single column (more readable)
```

**Table of Contents:**
```bash
--toc                          # Include TOC
--toc-depth=2                  # TOC depth (1=sections, 2=subsections)
--number-sections              # Number sections (1.1, 1.2, etc.)
```

**Code Highlighting:**
```bash
--highlight-style=tango        # Tango theme (colorful)
--highlight-style=zenburn      # Zenburn (dark background)
--highlight-style=pygments     # Pygments (default)
--listings                     # Use LaTeX listings package
```

---

## Method 2: Typora (GUI, Easy)

### Install Typora

Download from https://typora.io/ (Free trial, then paid)

### Generate PDF

1. Open TUTORIAL-PDF.md in Typora
2. File → Export → PDF
3. Settings:
   - Page size: A4 Landscape
   - Margins: Narrow (0.5in)
   - Theme: GitHub or Academic
4. Export

**Pros:** Easy, WYSIWYG preview
**Cons:** Not free, limited customization

---

## Method 3: VS Code + Markdown PDF Extension

### Install Extension

1. Open VS Code
2. Extensions → Search "Markdown PDF"
3. Install "Markdown PDF" by yzane

### Configure

Create `.vscode/settings.json` in `ce-demo/`:

```json
{
  "markdown-pdf.displayHeaderFooter": true,
  "markdown-pdf.headerTemplate": "<div style='font-size:9px; width:100%; text-align:left;'>Context Engineering Tutorial</div>",
  "markdown-pdf.footerTemplate": "<div style='font-size:9px; width:100%; text-align:center;'><span class='pageNumber'></span> / <span class='totalPages'></span></div>",
  "markdown-pdf.format": "A4",
  "markdown-pdf.orientation": "landscape",
  "markdown-pdf.margin.top": "0.5cm",
  "markdown-pdf.margin.bottom": "0.5cm",
  "markdown-pdf.margin.left": "0.5cm",
  "markdown-pdf.margin.right": "0.5cm",
  "markdown-pdf.styles": [
    "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.1.0/github-markdown.min.css"
  ]
}
```

### Generate PDF

1. Open TUTORIAL-PDF.md in VS Code
2. Right-click in editor
3. "Markdown PDF: Export (pdf)"
4. PDF saves to same directory

**Pros:** Free, integrated with VS Code
**Cons:** Less control than Pandoc, Chrome-based rendering

---

## Method 4: Online Converters (Quick & Dirty)

### Option A: Dillinger (Online Editor)

1. Visit https://dillinger.io/
2. Paste TUTORIAL-PDF.md content
3. Export As → PDF
4. Download

**Pros:** No installation
**Cons:** No landscape support, basic styling

### Option B: Markdown to PDF (Web Tool)

1. Visit https://www.markdowntopdf.com/
2. Upload TUTORIAL-PDF.md
3. Configure:
   - Page size: A4
   - Margins: Narrow
4. Generate & Download

**Pros:** No installation
**Cons:** Limited customization, privacy concerns

---

## Method 5: LaTeX Direct (Advanced)

### Convert Markdown → LaTeX → PDF

```bash
# Step 1: Convert to LaTeX
pandoc TUTORIAL-PDF.md -o TUTORIAL.tex

# Step 2: Edit TUTORIAL.tex (optional, customize layout)

# Step 3: Compile to PDF
xelatex TUTORIAL.tex
xelatex TUTORIAL.tex  # Run twice for TOC

# Result: TUTORIAL.pdf
```

**Pros:** Maximum control, professional typesetting
**Cons:** Requires LaTeX knowledge, manual editing

---

## Comparison Matrix

| Method | Quality | Ease | Cost | Customization | Speed |
|--------|---------|------|------|---------------|-------|
| **Pandoc** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Typora** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $15 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **VS Code** | ⭐⭐⭐ | ⭐⭐⭐⭐ | Free | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Online** | ⭐⭐ | ⭐⭐⭐⭐⭐ | Free | ⭐ | ⭐⭐⭐⭐⭐ |
| **LaTeX** | ⭐⭐⭐⭐⭐ | ⭐⭐ | Free | ⭐⭐⭐⭐⭐ | ⭐⭐ |

**Recommendation:** Use **Pandoc** for best results.

---

## Troubleshooting

### Issue: "pandoc: command not found"

**Solution:**
```bash
# macOS
brew install pandoc

# Linux
sudo apt-get install pandoc

# Windows
# Download installer from pandoc.org
```

### Issue: "xelatex not found"

**Solution:**
```bash
# macOS
brew install --cask basictex

# Linux
sudo apt-get install texlive-xetex texlive-fonts-recommended

# Windows
# Install MiKTeX: https://miktex.org/
```

### Issue: PDF has wrong fonts (Times Roman)

**Solution:**
Specify fonts explicitly:
```bash
pandoc TUTORIAL-PDF.md -o TUTORIAL.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Helvetica" \
  -V monofont="Courier New"
```

Or edit TUTORIAL-PDF.md header:
```yaml
mainfont: "Helvetica"
sansfont: "Arial"
monofont: "Menlo"
```

### Issue: PDF is portrait instead of landscape

**Solution:**
```bash
# Method 1: Command line
pandoc TUTORIAL-PDF.md -o TUTORIAL.pdf -V geometry:landscape

# Method 2: Edit TUTORIAL-PDF.md header
---
geometry: "landscape, margin=0.5in"
---
```

### Issue: Columns not working

**Solution:**
```bash
# Ensure columns in YAML header
---
columns: 2
---

# Or specify in command
pandoc TUTORIAL-PDF.md -o TUTORIAL.pdf -V columns=2
```

### Issue: Code blocks not syntax highlighted

**Solution:**
```bash
# Add highlight style
pandoc TUTORIAL-PDF.md -o TUTORIAL.pdf --highlight-style=tango

# Available styles:
pandoc --list-highlight-styles
# pygments, tango, espresso, zenburn, kate, monochrome, breezedark, haddock
```

### Issue: "LaTeX Error: Too many columns"

**Cause:** Two-column layout conflicts with wide content.

**Solution:**
Remove columns for compatibility:
```bash
pandoc TUTORIAL-PDF.md -o TUTORIAL.pdf -V columns=1
```

### Issue: PDF file size too large

**Solution:**
```bash
# Compress images before conversion
# Or use ghostscript after:
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=TUTORIAL-compressed.pdf TUTORIAL.pdf
```

---

## Custom Styling (Advanced)

### Create Custom CSS (for HTML → PDF)

**custom-style.css:**
```css
body {
  font-family: 'Helvetica', sans-serif;
  font-size: 10pt;
  line-height: 1.5;
  max-width: 100%;
  margin: 0.5in;
}

code {
  font-family: 'Menlo', monospace;
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
}

pre {
  background: #263238;
  color: #ffffff;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}

h1 {
  color: #1976d2;
  border-bottom: 2px solid #1976d2;
  padding-bottom: 5px;
}

h2 {
  color: #388e3c;
  border-left: 4px solid #388e3c;
  padding-left: 10px;
}

table {
  border-collapse: collapse;
  width: 100%;
}

th {
  background: #1976d2;
  color: white;
  padding: 10px;
}

td {
  border: 1px solid #e0e0e0;
  padding: 8px;
}

tr:nth-child(even) {
  background: #fafafa;
}
```

**Use with Pandoc:**
```bash
pandoc TUTORIAL-PDF.md -o TUTORIAL.pdf \
  --css=custom-style.css \
  --pdf-engine=weasyprint
```

### Create Custom LaTeX Template

**custom-template.latex:**
```latex
\documentclass[10pt,landscape,twocolumn]{article}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[margin=0.5in]{geometry}
\usepackage{xcolor}
\definecolor{codebackground}{RGB}{245,245,245}
\usepackage{listings}
\lstset{backgroundcolor=\color{codebackground}}

\begin{document}
$body$
\end{document}
```

**Use:**
```bash
pandoc TUTORIAL-PDF.md -o TUTORIAL.pdf \
  --template=custom-template.latex \
  --pdf-engine=xelatex
```

---

## Batch Generation (Multiple Formats)

### Shell Script: generate-all.sh

```bash
#!/bin/bash

# Generate multiple formats from TUTORIAL-PDF.md

echo "Generating PDFs..."

# Landscape 2-column (presentation handout)
pandoc TUTORIAL-PDF.md -o TUTORIAL-landscape-2col.pdf \
  --pdf-engine=xelatex \
  -V geometry:landscape \
  -V geometry:margin=0.5in \
  -V columns=2 \
  --toc

# Portrait 1-column (reading)
pandoc TUTORIAL-PDF.md -o TUTORIAL-portrait-1col.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V columns=1 \
  --toc --number-sections

# A4 Landscape (international)
pandoc TUTORIAL-PDF.md -o TUTORIAL-a4-landscape.pdf \
  --pdf-engine=xelatex \
  -V geometry:a4paper \
  -V geometry:landscape \
  -V geometry:margin=1cm \
  -V columns=2

echo "Done! Generated:"
echo "  - TUTORIAL-landscape-2col.pdf (handout)"
echo "  - TUTORIAL-portrait-1col.pdf (reading)"
echo "  - TUTORIAL-a4-landscape.pdf (A4)"
```

**Run:**
```bash
chmod +x generate-all.sh
./generate-all.sh
```

---

## Best Practices

1. **Preview before sharing:**
   - Open PDF in Adobe Reader (most compatible)
   - Check on different devices (mobile, tablet)
   - Verify code blocks are readable

2. **Optimize for print:**
   - Use minimum 10pt font
   - Avoid pure black (#000) → Use #1a1a1a
   - Test print one page before bulk printing

3. **Optimize for screen:**
   - Hyperlink table of contents
   - Use color for code syntax
   - Embed fonts (pandoc does this automatically)

4. **File naming:**
   - Include version: `TUTORIAL-v1.0.pdf`
   - Include date: `TUTORIAL-2025-01-15.pdf`
   - Include format: `TUTORIAL-landscape-2col.pdf`

---

## Recommended Workflow

**For presentation handouts:**
```bash
pandoc TUTORIAL-PDF.md -o TUTORIAL.pdf \
  --pdf-engine=xelatex \
  -V geometry:landscape \
  -V geometry:margin=0.5in \
  -V columns=2 \
  -V fontsize=10pt \
  --toc --toc-depth=2
```

**For in-depth reading:**
```bash
pandoc TUTORIAL.md -o TUTORIAL-full.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  --toc --toc-depth=3 \
  --number-sections
```

**For mobile/tablet:**
```bash
pandoc TUTORIAL.md -o TUTORIAL-mobile.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=0.5in \
  -V fontsize=12pt \
  -V columns=1
```

---

## Quality Checklist

Before distributing PDF:

- [ ] Fonts render correctly (no Times Roman unless intended)
- [ ] Code blocks have syntax highlighting
- [ ] Tables fit on page (not cut off)
- [ ] Links are clickable (if digital distribution)
- [ ] Table of contents page numbers accurate
- [ ] Headers/footers show correctly
- [ ] Page orientation correct (landscape/portrait)
- [ ] Margins allow for comfortable reading
- [ ] File size reasonable (<10MB for 50 pages)
- [ ] Metadata set (title, author)

---

## Resources

**Pandoc Documentation:**
- Official guide: https://pandoc.org/MANUAL.html
- PDF options: https://pandoc.org/MANUAL.html#creating-a-pdf

**LaTeX Fonts:**
- Font catalog: https://tug.org/FontCatalogue/
- XeLaTeX fonts: System fonts (macOS: /Library/Fonts)

**Markdown to PDF Tools:**
- Pandoc: https://pandoc.org/
- Typora: https://typora.io/
- mdpdf: https://github.com/BlueHatbRit/mdpdf
- md-to-pdf: https://github.com/simonhaenisch/md-to-pdf

---

**Questions?**

Check TUTORIAL-PDF.md header for inline configuration.
Most settings can be controlled via YAML frontmatter.

**Happy PDF generation!**
