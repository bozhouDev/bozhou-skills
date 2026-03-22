# Style Presets

`--style X` expands to a palette + rendering combination. Users can override either dimension.

| --style | Palette | Rendering |
|---------|---------|-----------|
| `bauhaus` | `bauhaus` | `flat-vector` |
| `swiss-design` | `mono` | `flat-vector` |
| `glassmorphism` | `cool` | `digital` |
| `editorial-chic` | `elegant` | `hand-drawn` |
| `dark-brutalism` | `dark` | `digital` |
| `corporate-memphis` | `pastel` | `flat-vector` |
| `neo-cyber` | `neon` | `digital` |
| `organic-abstract` | `earth` | `painterly` |
| `risograph` | `duotone` | `screen-print` |
| `wireframe-core` | `mono` | `digital` |
| `monolithic` | `dark` | `flat-vector` |
| `cinematic-void` | `duotone` | `painterly` |
| `acid-graphics` | `vivid` | `flat-vector` |
| `claymorphism` | `pastel` | `digital` |
| `vintage-offset` | `retro` | `screen-print` |

## Override Examples

- `--style swiss-design --rendering digital` = mono palette with digital rendering
- `--style editorial-chic --palette warm` = warm palette with hand-drawn rendering

Explicit `--palette`/`--rendering` flags always override preset values.
