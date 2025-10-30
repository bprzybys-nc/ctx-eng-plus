# Context Engineering Components Architecture

**Copy the code below into https://mermaid.live/ and export as SVG or PNG (2400×1200)**

---

```mermaid
%%{init: {'theme':'default', 'themeVariables': { 'fontSize':'13px', 'fontFamily':'Arial, sans-serif'}}}%%

graph TB
    subgraph Framework["🎯 Context Engineering Framework<br/> "]
        direction TB
        A["📋 CLAUDE.md<br/>Project Rules<br/>Style, Testing, Gotchas<br/> "]
        B["📁 PRPs/<br/>Implementation Plans<br/>Goals, Tasks, Validation<br/> "]
        C["💻 examples/<br/>Code Patterns<br/>Real Implementations<br/> "]
        D["⚙️ .ce/<br/>Framework Core<br/>Boilerplate, Templates<br/> "]
    end

    subgraph Commands["🚀 Commands<br/> "]
        direction TB
        E["generate-prp<br/>Create Comprehensive Plan<br/> "]
        F["execute-prp<br/>Build with Validation<br/> "]
    end

    subgraph Output["✨ Output<br/> "]
        direction TB
        G["✅ Production Code<br/>Follows Patterns<br/> "]
        H["🧪 Passing Tests<br/>80%+ Coverage<br/> "]
        I["📊 Clean Reports<br/>Lint, Type, Integration<br/> "]
    end

    A -->|"provides rules"| E
    B -->|"contains templates"| E
    C -->|"shows patterns"| E
    D -->|"core framework"| E

    E -->|"creates"| F
    B -->|"guides execution"| F

    F -->|"produces"| G
    F -->|"runs"| H
    F -->|"generates"| I

    style A fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000
    style B fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px,color:#000
    style C fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    style D fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000

    style E fill:#fff9c4,stroke:#f9a825,stroke-width:3px,color:#000
    style F fill:#ffe0b2,stroke:#ef6c00,stroke-width:3px,color:#000

    style G fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#000
    style H fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#000
    style I fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#000

    style Framework fill:#fafafa,stroke:#424242,stroke-width:2px,color:#000
    style Commands fill:#fafafa,stroke:#424242,stroke-width:2px,color:#000
    style Output fill:#fafafa,stroke:#424242,stroke-width:2px,color:#000
```

---

## Export Instructions

1. **Copy the mermaid code above** (between the \`\`\`mermaid markers)
2. **Paste into https://mermaid.live/**
3. **Export Settings:**
   - **SVG** (recommended): Actions → Export SVG → Save as `components.svg`
   - **PNG** (2x): Actions → Export PNG → Width: 2400px → Save as `components.png`
4. **Save to:** `ce-demo/assets/components.png`

## Diagram Details

- **Orientation:** TB (top-to-bottom, vertical flow with subgraphs)
- **Optimal size:** 2400×1200 PNG (display at 1200×600)
- **Slide placement:** 80% width, centered
- **Theme:** Light pastel colors, grouped by function
- **Subgraphs:** 3 (Framework, Commands, Output)
- **Nodes:** 9 total across 3 layers

## Usage in Slides

**Slide 9: Key Components Deep Dive** (alternative to 3-column card layout)
- Insert as full-width image
- Shows how components connect
- Framework (inputs) → Commands (process) → Output (results)

**Alternative:** Use for backup slide or appendix showing system architecture

---

## Color Coding

- **Blue (CLAUDE.md):** Rules and conventions
- **Purple (PRPs/):** Implementation blueprints
- **Green (examples/):** Code patterns
- **Orange (.ce/):** Framework infrastructure
- **Yellow (Commands):** Execution layer
- **Light green (Output):** Final deliverables

---

**Recommended export:** SVG → PNG at 2400×1200, then display at 1200×600. The vertical layout with subgraphs needs height, but fits well in landscape slide.
