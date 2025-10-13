# Mermaid Diagram Color Palette - Standard

**Purpose:** Standard color palette for Mermaid diagrams in Context Engineering documentation
**Requirement:** Always specify text color for theme compatibility

---

## Color Palette Reference

### Primary Palette (System Components)

```mermaid
graph LR
    A["Primary Blue<br/>#e3f2fd"] --> B["Light Yellow<br/>#fff8e1"]
    B --> C["Light Purple<br/>#f3e5f5"]
    C --> D["Light Cyan<br/>#b2ebf2"]
    D --> E["Light Orange<br/>#ffe0b2"]

    style A fill:#e3f2fd,color:#000
    style B fill:#fff8e1,color:#000
    style C fill:#f3e5f5,color:#000
    style D fill:#b2ebf2,color:#000
    style E fill:#ffe0b2,color:#000
```

### Secondary Palette (Detail Nodes)

```mermaid
graph LR
    A["Pale Yellow<br/>#fff9c4"] --> B["Very Light Cyan<br/>#e1f5fe"]
    B --> C["Light Teal<br/>#b2dfdb"]
    C --> D["Pale Orange<br/>#ffecb3"]

    style A fill:#fff9c4,color:#000
    style B fill:#e1f5fe,color:#000
    style C fill:#b2dfdb,color:#000
    style D fill:#ffecb3,color:#000
```

### Status Colors

```mermaid
graph LR
    A["Success Green<br/>#c8e6c9"] --> B["Warning Red<br/>#ff9999"]
    B --> C["Error Salmon<br/>#ffccbc"]
    C --> D["Failure Red<br/>#ef9a9a"]

    style A fill:#c8e6c9,color:#000
    style B fill:#ff9999,color:#000
    style C fill:#ffccbc,color:#000
    style D fill:#ef9a9a,color:#000
```

---

## Usage Guidelines

### 1. Always Specify Text Color

**MANDATORY:** Include `color:#000` for light backgrounds to ensure readability in both light and dark themes.

```mermaid
graph LR
    A["Node Text"]

    style A fill:#e3f2fd,color:#000
```

### 2. Node Type Color Mapping

| Node Type | Color | Hex Code | Usage |
|-----------|-------|----------|-------|
| **Entry Point** | Light Yellow | `#fff8e1` | Start nodes, input documents |
| **Process** | Light Purple | `#f3e5f5` | Processing steps, commands |
| **Data/Document** | Light Cyan | `#b2ebf2` | Documents, data stores |
| **Decision** | Pale Orange | `#fff3e0` | Decision nodes, branches |
| **Action** | Light Orange | `#ffe0b2` | Actions, operations |
| **Critical Checkpoint** | Warning Red | `#ff9999` | Human validation, critical decisions |
| **Success** | Success Green | `#c8e6c9` | Final success states |
| **Error/Manual** | Error Salmon | `#ffccbc` | Error handling, manual intervention |

### 3. Hierarchical Color Scheme

**Parent → Child relationship:**

- Parent node: Primary palette color
- Child nodes: Secondary palette color (lighter shade)

```mermaid
graph TB
    A["Parent Node<br/>Primary Color"]
    A --> B["Child Node<br/>Secondary Color"]
    A --> C["Child Node<br/>Secondary Color"]

    style A fill:#f3e5f5,color:#000
    style B fill:#e1f5fe,color:#000
    style C fill:#e1f5fe,color:#000
```

---

## Standard Templates

### Template 1: System Architecture

**Use Case:** Component hierarchy, system overview

```mermaid
graph TB
    A["System"]
    A --> B["Component 1"]
    A --> C["Component 2"]

    B --> B1["Sub-component 1.1"]
    B --> B2["Sub-component 1.2"]

    C --> C1["Sub-component 2.1"]
    C --> C2["Sub-component 2.2"]

    style A fill:#e3f2fd,color:#000
    style B fill:#fff8e1,color:#000
    style C fill:#f3e5f5,color:#000
    style B1 fill:#fff9c4,color:#000
    style B2 fill:#fff9c4,color:#000
    style C1 fill:#e1f5fe,color:#000
    style C2 fill:#e1f5fe,color:#000
```

### Template 2: Workflow Process

**Use Case:** Step-by-step processes, workflows

```mermaid
graph LR
    A["Input"] --> B["Process 1"]
    B --> C["Document"]
    C --> D{"Decision"}
    D -->|"Yes"| E["Action"]
    D -->|"No"| F["Alternative"]
    E --> G["Success"]
    F --> G

    style A fill:#fff8e1,color:#000
    style B fill:#f3e5f5,color:#000
    style C fill:#b2ebf2,color:#000
    style D fill:#fff3e0,color:#000
    style E fill:#ffe0b2,color:#000
    style F fill:#fff9c4,color:#000
    style G fill:#c8e6c9,color:#000
```

### Template 3: Decision Flow

**Use Case:** Complex decision trees, conditional logic

```mermaid
graph TD
    A["Start"] --> B{"Condition 1?"}
    B -->|"Yes"| C["Path A"]
    B -->|"No"| D["Path B"]

    C --> E{"Condition 2?"}
    E -->|"Yes"| F["Success"]
    E -->|"No"| G["Retry"]

    D --> H["Manual Action"]
    H --> F
    G --> B

    style A fill:#fff8e1,color:#000
    style B fill:#fff3e0,color:#000
    style C fill:#b2ebf2,color:#000
    style D fill:#ffe0b2,color:#000
    style E fill:#fff3e0,color:#000
    style F fill:#c8e6c9,color:#000
    style G fill:#ffccbc,color:#000
    style H fill:#ff9999,color:#000
```

### Template 4: Validation Gates

**Use Case:** Testing, validation processes

```mermaid
graph TB
    A["Code"] --> B["Level 1: Syntax"]
    B --> B1["Auto-fix"]
    B1 --> C["Level 2: Unit Tests"]
    C --> C1["Analyze & Fix"]
    C1 --> D["Level 3: Integration"]
    D --> D1["Debug"]
    D1 --> E["Production"]

    style A fill:#e3f2fd,color:#000
    style B fill:#fff8e1,color:#000
    style B1 fill:#fff9c4,color:#000
    style C fill:#f3e5f5,color:#000
    style C1 fill:#e1f5fe,color:#000
    style D fill:#b2ebf2,color:#000
    style D1 fill:#b2dfdb,color:#000
    style E fill:#c8e6c9,color:#000
```

---

## Complete Color Reference Table

| Color Name | Hex Code | RGB | Usage Context |
|------------|----------|-----|---------------|
| **Primary Blue** | `#e3f2fd` | rgb(227, 242, 253) | Top-level system nodes |
| **Light Yellow** | `#fff8e1` | rgb(255, 248, 225) | Entry points, inputs |
| **Light Purple** | `#f3e5f5` | rgb(243, 229, 245) | Processing steps |
| **Light Cyan** | `#b2ebf2` | rgb(178, 235, 242) | Documents, data |
| **Light Orange** | `#ffe0b2` | rgb(255, 224, 178) | Actions, commands |
| **Pale Yellow** | `#fff9c4` | rgb(255, 249, 196) | Secondary details |
| **Very Light Cyan** | `#e1f5fe` | rgb(225, 245, 254) | Secondary details |
| **Light Teal** | `#b2dfdb` | rgb(178, 223, 219) | Secondary details |
| **Pale Orange** | `#ffecb3` | rgb(255, 236, 179) | Secondary details |
| **Pale Orange 2** | `#fff3e0` | rgb(255, 243, 224) | Decision nodes |
| **Success Green** | `#c8e6c9` | rgb(200, 230, 201) | Success states |
| **Warning Red** | `#ff9999` | rgb(255, 153, 153) | Critical checkpoints |
| **Error Salmon** | `#ffccbc` | rgb(255, 204, 188) | Errors, manual steps |
| **Failure Red** | `#ef9a9a` | rgb(239, 154, 154) | Failure states |

---

## Anti-Patterns to Avoid

### ❌ BAD: No text color specified

```mermaid
graph LR
    A["Node Text"]

    style A fill:#e3f2fd
```

**Problem:** Text may be invisible in dark themes.

### ❌ BAD: Inconsistent color scheme

```mermaid
graph LR
    A["Node 1"] --> B["Node 2"]
    B --> C["Node 3"]

    style A fill:#ff0000,color:#000
    style B fill:#00ff00,color:#000
    style C fill:#0000ff,color:#000
```

**Problem:** Random colors break visual hierarchy.

### ✅ GOOD: Consistent palette with text color

```mermaid
graph LR
    A["Node 1"] --> B["Node 2"]
    B --> C["Node 3"]

    style A fill:#e3f2fd,color:#000
    style B fill:#fff8e1,color:#000
    style C fill:#f3e5f5,color:#000
```

**Benefit:** Clear hierarchy, theme-compatible.

---

## Quick Copy-Paste Templates

### Basic Node Styles

```
style A fill:#e3f2fd,color:#000    # Primary Blue
style B fill:#fff8e1,color:#000    # Light Yellow
style C fill:#f3e5f5,color:#000    # Light Purple
style D fill:#b2ebf2,color:#000    # Light Cyan
style E fill:#ffe0b2,color:#000    # Light Orange
```

### Detail Node Styles

```
style A1 fill:#fff9c4,color:#000   # Pale Yellow
style A2 fill:#e1f5fe,color:#000   # Very Light Cyan
style A3 fill:#b2dfdb,color:#000   # Light Teal
style A4 fill:#ffecb3,color:#000   # Pale Orange
```

### Status Node Styles

```
style SUCCESS fill:#c8e6c9,color:#000   # Success Green
style WARNING fill:#ff9999,color:#000   # Warning Red
style ERROR fill:#ffccbc,color:#000     # Error Salmon
style FAIL fill:#ef9a9a,color:#000      # Failure Red
```

---

## Version History

- **v1.0** (2025-10-11): Initial palette extraction from PRPs/Model.md
- Based on production diagrams: System Components, PRP Architecture, Validation Gates

---

## References

- Source: [PRPs/Model.md](../PRPs/Model.md)
- Documentation Standard: [CLAUDE.md](../CLAUDE.md) (Mermaid color requirements)
- Mermaid Documentation: <https://mermaid.js.org/syntax/flowchart.html#styling-and-classes>
