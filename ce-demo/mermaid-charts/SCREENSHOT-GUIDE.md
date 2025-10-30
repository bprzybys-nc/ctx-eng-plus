# Mermaid Chart Screenshot Guide

**How to capture high-quality diagram screenshots for presentation**

---

## Quick Method (Recommended)

### Using Mermaid Live Editor

1. Visit https://mermaid.live/
2. Open each `*-preview.md` file below
3. Copy the mermaid code block content (without the \`\`\`mermaid markers)
4. Paste into Mermaid Live editor
5. **Export Settings:**
   - Format: **SVG** (best quality, vector)
   - Or PNG at **2x scale** (2400×1200px for workflow/components)
   - Background: **White** (matches presentation)
6. Save to `assets/` folder

---

## Optimal Export Sizes (For 16:9 Slides)

**Slide dimensions:** 1920×1080 (16:9)

**Target sizes for diagrams:**

| Diagram | Slide Area | Export Size (PNG 2x) | Final Display |
|---------|-----------|---------------------|---------------|
| **workflow** | 80% width | 2400×1200 | 1200×600 |
| **components** | 80% width | 2400×1200 | 1200×600 |
| **validation-loop** | 60% width, centered | 1800×1200 | 900×600 |

**Why 2x resolution?**
- Supersampling antialiasing (render at 2x, display at 1x)
- Crisp text on high-DPI displays (Retina, 4K monitors)
- Smooth lines and edges
- No jagged pixels

---

## Antialiasing Strategy

### Best Quality: SVG → PNG Conversion

**Method 1: Browser Screenshot (Easiest)**
```bash
# In Mermaid Live:
1. Export as SVG
2. Open SVG in Chrome/Safari at 200% zoom
3. Take screenshot (cmd+shift+4 on macOS)
4. Crop to exact diagram bounds
5. Resize to target size in Preview/Photoshop
```

**Method 2: Inkscape (Best Control)**
```bash
# Install Inkscape
brew install --cask inkscape

# Convert SVG → PNG with antialiasing
inkscape diagram.svg \
  --export-type=png \
  --export-dpi=192 \
  --export-width=2400 \
  --export-background=white \
  --export-filename=diagram.png
```

**Method 3: ImageMagick (Command Line)**
```bash
brew install imagemagick

# Convert with supersampling
convert -density 300 -background white diagram.svg \
  -resize 2400x1200 \
  -quality 100 diagram.png
```

---

## Screenshot Workflow

### For macOS (Native)

1. **Open preview file** (workflow-preview.md, etc.)
2. **Render in Mermaid Live** (https://mermaid.live/)
3. **Export SVG** (Actions → Export SVG)
4. **Open in browser** at 200% zoom
5. **Screenshot** (cmd+shift+4, drag selection)
6. **Save** to `assets/workflow.png`

### For VS Code + Mermaid Extension

1. Install "Markdown Preview Mermaid Support" extension
2. Open `workflow-preview.md`
3. Click preview icon
4. Right-click diagram → "Copy Image"
5. Paste into image editor
6. Export at 2400×1200 PNG

### For Typora (WYSIWYG)

1. Open `workflow-preview.md` in Typora
2. Diagram renders automatically
3. Right-click → Copy as Image
4. Paste into Preview.app
5. Export as PNG (2400×1200)

---

## Image Optimization (After Screenshot)

### Resize with Preview (macOS)

1. Open PNG in Preview.app
2. Tools → Adjust Size
3. Width: 1200 pixels (for workflow/components)
4. Resolution: 144 pixels/inch
5. ✓ Scale proportionally
6. ✓ Resample image (antialiasing)
7. Save

### Optimize File Size

```bash
# Install pngquant (lossless compression)
brew install pngquant

# Compress PNG (reduces size ~50%, keeps quality)
pngquant --quality=85-95 workflow.png -o workflow-optimized.png

# Or use ImageOptim (GUI)
# Download: https://imageoptim.com/mac
```

---

## Quality Checklist

Before using diagrams in presentation:

- [ ] Text is crisp and readable at 100% zoom
- [ ] No jagged edges on arrows/boxes
- [ ] Colors match Mermaid theme (blues, greens)
- [ ] Background is pure white (#FFFFFF)
- [ ] File size reasonable (<500KB per diagram)
- [ ] Transparent background if needed (for overlays)
- [ ] Emoji render correctly (if included)

---

## Recommended Settings per Diagram

### workflow.mermaid (LR orientation)

**Mermaid Live Settings:**
- Width: Auto (fits ~2400px)
- Theme: Default
- Background: White

**Export:**
- Format: SVG → PNG (2400×1200)
- Display: 1200×600 (80% slide width)

**Notes:**
- Left-to-right flow works best for this
- Wide aspect ratio fits slide nicely
- Keep text readable at 10-12pt minimum

---

### components.mermaid (TB orientation with subgraphs)

**Mermaid Live Settings:**
- Width: Auto
- Theme: Default
- Background: White

**Export:**
- Format: SVG → PNG (2400×1200)
- Display: 1200×600 (80% slide width)

**Notes:**
- Subgraphs need vertical space
- May need to tweak node spacing
- Ensure labels don't overlap

---

### validation-loop.mermaid (TD orientation, cyclic)

**Mermaid Live Settings:**
- Width: Auto
- Theme: Default
- Background: White

**Export:**
- Format: SVG → PNG (1800×1200)
- Display: 900×600 (60% slide width, centered)

**Notes:**
- Taller aspect ratio for cyclic flow
- Center on slide for visual balance
- Loop arrows should be clear

---

## Troubleshooting

### Issue: Text too small in exported PNG

**Solution:**
```mermaid
%%{init: {'theme':'default', 'themeVariables': { 'fontSize':'16px'}}}%%
```
Add to top of Mermaid code to increase font size.

### Issue: Colors don't match presentation theme

**Solution:**
Use custom theme variables:
```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor':'#e3f2fd',
  'primaryTextColor':'#000',
  'primaryBorderColor':'#1976d2',
  'lineColor':'#1976d2',
  'secondaryColor':'#c8e6c9',
  'tertiaryColor':'#fff9c4'
}}}%%
```

### Issue: Diagram too wide/tall for slide

**Solution:**
- Reduce node count (simplify diagram)
- Adjust Mermaid layout direction (LR ↔ TD)
- Split into multiple diagrams
- Use smaller font size in theme

### Issue: Blurry diagram on Retina display

**Solution:**
- Export at 2x or 3x resolution
- Use SVG instead of PNG (vector, infinite zoom)
- Ensure "Resample image" checked when resizing

---

## Final File Structure

After screenshots:

```
ce-demo/
├── assets/
│   ├── workflow.png           (1200×600, ~200KB)
│   ├── components.png         (1200×600, ~250KB)
│   └── validation-loop.png    (900×600, ~150KB)
└── mermaid-charts/
    ├── workflow.mermaid
    ├── components.mermaid
    ├── validation-loop.mermaid
    ├── workflow-preview.md       (← Open these)
    ├── components-preview.md
    └── validation-loop-preview.md
```

---

## Quick Reference Commands

```bash
# Create assets directory
mkdir -p assets

# Screenshot workflow (macOS)
# 1. Open workflow-preview.md in Mermaid Live
# 2. Export SVG
# 3. Convert to PNG:
inkscape workflow.svg --export-type=png --export-dpi=192 \
  --export-width=2400 --export-background=white \
  --export-filename=assets/workflow.png

# Resize to display size
sips -z 600 1200 assets/workflow.png

# Optimize file size
pngquant --quality=85-95 assets/workflow.png \
  -o assets/workflow-optimized.png
```

---

**Ready to create screenshots!**

1. Open `workflow-preview.md` in Mermaid Live
2. Export at 2x resolution
3. Save to `assets/`
4. Repeat for other diagrams
5. Import into Google Slides
