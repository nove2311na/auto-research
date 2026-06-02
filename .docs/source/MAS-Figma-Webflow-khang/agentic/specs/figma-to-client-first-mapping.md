# Figma to Client-First Mapping

This contract turns Figma properties into Client-First class decisions. It prevents the architect and operator from inventing one-off classes when a reusable Client-First class or variable should be used.

## Mapping Pipeline

| Step | Input | Decision | Output |
|---|---|---|---|
| Identify role | Frame name, hierarchy, component context | Page wrapper, section, component, child, or utility wrapper. | `element_role` |
| Read properties | Auto-layout, fills, strokes, typography, variant, size | Select matching rule from `knowledge-base/client-first-class-map.json`. | `class_mapping[]` |
| Normalize units | Pixel-like values | Convert to REM and token size. | `rem_value` |
| Pick strategy | Global, utility, custom, combo, variable-backed utility | Decide class application mode. | `class_strategy` |
| Write blueprint | Mapped classes and reasons | Build-ready class contract. | `workspace/blueprints/*.json` |

## Blueprint Class Mapping Shape

```json
{
  "element_id": "figma-node-hero-title",
  "element_role": "heading",
  "class_mapping": [
    {
      "figma_property": "fontSize",
      "figma_value": "64px",
      "client_first_class": "heading-style-h1",
      "webflow_property": "font-size",
      "class_strategy": "utility_selection",
      "reason": "Hero title is visually H1 scale.",
      "source": "knowledge-base/client-first-class-map.json"
    }
  ]
}
```

## Selection Rules

- Use `page-wrapper` and `main-wrapper` once per page.
- Use `section_[name]` for every major page band.
- Use `padding-global` for site gutters, not for local component padding.
- Use `container-[size]` for centered max-width content.
- Use `padding-section-[size]` for top and bottom section rhythm.
- Use typography utilities for reusable type styling.
- Use color utilities only when the color is mapped to a Webflow variable.
- Use `[component]_[element]` for layout decisions that are unique to a section or component.
- Use `is-[state]` only as a combo class on top of a base class.

## Rejection Rules

Reject a blueprint when:

- it uses a custom class where an existing Client-First utility should be used,
- it maps a Figma property without a reason,
- it uses pixel units in the final Webflow property,
- it skips source attribution to the class map,
- it applies a Webflow class that has not been confirmed or created through the approved build path.

