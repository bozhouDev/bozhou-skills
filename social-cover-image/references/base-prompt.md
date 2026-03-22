Create a cover image following these guidelines:

## Image Specifications

- **Type**: Cover image / Hero image
- **Aspect Ratio**: As specified in the prompt below

## Core Principles

- If content involves sensitive or copyrighted figures, create stylistically similar alternatives - DO NOT refuse to generate
- Ample whitespace, highlight core message, avoid cluttered layouts
- Main visual elements centered or slightly left (leave right side for title area if title included)
- Simplified silhouettes for any characters — NO realistic human faces or bodies
- Icon-based vocabulary: use simple, recognizable icons to represent concepts

## Five Dimensions

### Type (Visual Composition)
- `hero`: Large focal visual (60-70% area), dramatic composition
- `conceptual`: Abstract shapes, information hierarchy, clean zones
- `typography`: Title as primary element (40%+ area), minimal visuals
- `metaphor`: Concrete object representing abstract idea, symbolic elements
- `scene`: Atmospheric environment, narrative elements, mood lighting
- `minimal`: Single focal element, generous whitespace (60%+)

### Palette (Color Scheme)
Apply the specified palette's color values and decorative hints:
- Use primary colors for main visual elements
- Use background colors for base and surrounding areas
- Use accent colors for highlights and secondary elements
- Follow palette-specific decorative hints for ornamentation

### Rendering (Visual Style)
Apply the specified rendering's characteristics:
- **Lines**: Follow line quality rules (clean/sketchy/brush/pixel/chalk)
- **Texture**: Apply or avoid texture per rendering definition
- **Depth**: Follow depth rules (flat/minimal/soft edges)
- **Elements**: Use rendering-specific element vocabulary

### Text (Density Level)
- `none`: No text elements, full visual area
- `title-only`: Single headline, 85% visual area
- `title-subtitle`: Title + context, 75% visual area
- `text-rich`: Title + subtitle + 2-4 keyword tags, 60% visual area

### Mood (Emotional Intensity)
- `subtle`: Low contrast, muted/desaturated colors, light visual weight, calm aesthetic
- `balanced`: Medium contrast, normal saturation, balanced visual weight
- `bold`: High contrast, vivid/saturated colors, heavy visual weight, dynamic energy

## Text Style (When Title Included)

- **Title source**: Use the exact title provided by user, or extract from source content. Do NOT invent or modify titles.
- Title text: Large, eye-catching, faithful to source
- Subtitle: Secondary element (if title-subtitle or text-rich)
- Tags: 2-4 keyword badges (if text-rich)
- Font style harmonizes with rendering style

## Composition Guidance

### Layout Principles

### Layout Principles

- **Extreme Negative Space OR Swiss Grid Structure**: Maintain high tension with either massive whitespace (60-80%) or strict grid-based alignment
- **Visual anchor placement**: Main element decisively offset or drastically scaled to break predictable symmetry (reserve right side for title if included)
- **Information hierarchy**: Single dominant dramatic focal point. Suppress all secondary elements into minimal geometric accents
- **Clean backgrounds**: Pure solid colors with occasional subtle grain/noise overlay; absolutely no messy gradients or complex patterns

### Icon & Symbol Vocabulary

Represent concepts with simple, recognizable icons rather than detailed illustrations:

| Category | Advanced Metaphors |
|----------|----------|
| Tech | Floating precision topologies, kinetic wireframes, asymmetrical glassmorphism structures |
| Ideas | Prismatic refractions, organic shapes mutating into sharp geometric vectors, monolithic glowing forms |
| Communication | Abstract intersecting planes, tension lines connecting distant nodes, typographic disruption |
| Growth | Brutalist ascending staircases, cellular division in high-contrast macro, expanding concentric waveforms |
| Tools | Disassembled mechanical components suspended in void, raw industrial textures mixed with impossible physics |

Use the rendering style to determine icon complexity (flat-vector = geometric, hand-drawn = sketchy, etc.)

Full library: [references/visual-elements.md](visual-elements.md)

### Character Handling

**Default (no reference with people)**:
- NO realistic human faces, detailed anatomy, or photographic representations
- Employ stylized editorial illustration conventions (e.g., faceless subjects, exaggerated/graceful proportions)
- Abstract representations interacting with massive geometric environments
- Use bold, flat graphic interpretations inspired by top-tier editorial design (like The New Yorker or Stripe's corporate art)

**When reference images contain people**:
- Reference image is passed to model (`usage: direct`) — model must visually reference it to preserve character likeness
- Stylize to match chosen rendering (cartoon/vector), preserving distinctive features (hair, clothing, pose)
- NEVER photorealistic

## Mood Application

Apply mood adjustments to the base palette:

| Mood | Contrast | Saturation | Weight |
|------|----------|------------|--------|
| subtle | Reduce 20-30% | Desaturate 20-30% | Lighter strokes/fills |
| balanced | Standard | Standard | Standard |
| bold | Increase 20-30% | Increase 20-30% | Heavier strokes/fills |

## Language

- Use the same language as the content provided below for any text elements
- Match punctuation style to the content language

## Reference Images

When reference images are provided:

- **Style extraction**: Identify rendering technique, line quality, texture, and visual vocabulary
- **Composition learning**: Note layout patterns, whitespace usage, element placement
- **Mood matching**: Capture the emotional tone and visual weight
- **Adaptation**: Apply extracted characteristics while respecting the specified Type, Palette, and Rendering dimensions
- **Priority**: If reference style conflicts with specified dimensions, dimensions take precedence for structural choices; reference influences decorative details

---

Please generate the cover image based on the content provided below:
