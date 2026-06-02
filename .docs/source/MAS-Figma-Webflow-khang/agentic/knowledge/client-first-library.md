# Client-First Library

The Client-First library is split into two layers:

- `knowledge-base/client-first-theory.md`: human-readable rules and rationale.
- `knowledge-base/client-first-class-map.json`: structured class, property, and Figma signal catalog for agents and scripts.

## How Agents Use It

1. Read Figma raw data from `workspace/rawdata/`.
2. Match Figma signals against `knowledge-base/client-first-class-map.json`.
3. Choose the Client-First class strategy:
   - required global class,
   - utility selection,
   - utility pair,
   - variable-backed utility,
   - custom section,
   - custom component,
   - combo class.
4. Write the decision into `workspace/blueprints/*.json`.
5. Copy the same selected classes into Webflow build actions after user approval.

## Class Mapping Rule

Every mapped class in a blueprint must include:

- `figma_property`
- `figma_value`
- `client_first_class` or `client_first_class_pattern`
- `webflow_property`
- `reason`
- `source`

Example:

```json
{
  "figma_property": "vertical section padding",
  "figma_value": "80px top and bottom",
  "client_first_class": "padding-section-medium",
  "webflow_property": "padding-top and padding-bottom",
  "reason": "Section-level vertical rhythm maps to the Client-First section padding utility.",
  "source": "knowledge-base/client-first-class-map.json"
}
```

## Webflow Project Sync

The Webflow project should contain matching variables and global classes before build execution:

- page and main wrappers,
- section, padding, and container classes,
- text-size, heading-style, text-weight, and text-align utilities,
- text-color, background-color, and border-color utilities backed by variables,
- component custom classes generated from the approved blueprint.

If a mapped utility class does not exist in Webflow, the operator must record the missing class in `workspace/error-logs.json` and ask PM before creating or substituting it.

