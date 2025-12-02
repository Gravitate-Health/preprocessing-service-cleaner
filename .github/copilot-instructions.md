# Copilot Instructions: Preprocessing Service Cleaner

## Project Overview

This is a Python Flask/Connexion REST service that preprocesses FHIR R4 ePI (electronic Product Information) bundles for pharmaceutical and healthcare data pipelines. The service performs three main transformations on FHIR Composition resources:

1. **HTML Optimization** - Removes empty/non-functional tags and simplifies nested structures
2. **Extension Cleanup** - Removes unused HtmlElementLink extensions based on actual HTML class usage
3. **Style/Class Cleanup** - Removes style attributes and CSS classes not defined in HtmlElementLink extensions

## Architecture & Data Flow

### Request Processing Pipeline
```
POST /preprocess → preprocess_controller.py
  ↓
FhirEPI.from_dict() - Parse FHIR Bundle
  ↓
_apply_preprocessing() - Process each entry
  ↓
For each Composition:
  1. optimize_html() - Remove empty tags, simplify nesting
  2. _collect_all_html_classes_from_resource() - Extract classes recursively from ALL sections/subsections
  3. cleanup_unused_html_element_links() - Remove extensions for unused classes
  4. cleanup_html_styles_and_classes() - Remove styles and unaccounted classes
  ↓
Return preprocessed bundle
```

### Critical Pattern: Recursive Section Processing
**The HTML and classes exist in nested sections, not just top-level Composition.text.div**

```python
# WRONG - Only checks composition text.div
html = composition['text']['div']

# CORRECT - Must recursively collect from all sections
def _collect_all_html_classes_from_resource(resource):
    all_classes = set()
    all_classes.update(extract_html_classes(get_html_content(resource).raw_html))
    
    def collect_from_sections(sections):
        for section in sections:
            classes.update(extract_html_classes(get_html_content(section).raw_html))
            if 'section' in section:  # Process subsections recursively
                classes.update(collect_from_sections(section['section']))
```

See `preprocessor/controllers/preprocess_controller.py:_collect_all_html_classes_from_resource()` for the actual implementation.

## Key Components

### Models (`preprocessor/models/`)
- **`fhir_epi.py`** - FHIR Bundle wrapper with methods like `get_composition()`, `get_entries_by_resource_type()`
- **`html_optimizer.py`** - Core optimization: `optimize_html()`, `extract_html_classes()`, `validate_content_integrity()`
- **`html_content_manager.py`** - HTML extraction/update: `get_html_content()`, `update_html_content()`
- **`html_element_link_manager.py`** - CRUD for HtmlElementLink extensions: `list_html_element_links()`, `add_html_element_link()`, `remove_html_element_link()`, `get_element_classes()`
- **`html_element_link_cleanup.py`** - Cleanup logic: `cleanup_unused_html_element_links()`

### Controllers (`preprocessor/controllers/`)
- **`preprocess_controller.py`** - Main endpoint handler, contains all preprocessing business logic

## Configuration (Environment Variables)

Feature flags control preprocessing behavior (all default to `true`):

| Variable | Valid Values | Purpose |
|----------|--------------|---------|
| `ENABLE_HTML_OPTIMIZATION` | `true`,`1`,`yes`,`on` or `false`,`0`,`no`,`off` | Toggle empty tag removal and nested tag simplification |
| `ENABLE_LINK_CLEANUP` | Same | Toggle removal of unused HtmlElementLink extensions |
| `ENABLE_STYLE_CLEANUP` | Same | Toggle removal of style attributes and unaccounted CSS classes |

Set in `Dockerfile` or override at runtime:
```powershell
docker run -e ENABLE_HTML_OPTIMIZATION=false -p 8080:8080 ghcr.io/...
```

## Development Workflow

### Local Setup (Python 3.12+)
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Service
```powershell
# Local
python -m preprocessor

# Docker
docker build -t preprocessing-service .
docker run --rm -p 8080:8080 preprocessing-service
```

### Testing Strategy

**Standalone test runners** (no pytest needed):
- `test/test_html_element_link_standalone.py` - HtmlElementLink CRUD operations
- `test/test_html_content_manager_standalone.py` - HTML extraction/manipulation
- `test/test_html_optimization_standalone.py` - HTML optimization and cleanup

**Integration tests** (pytest required):
```powershell
pytest test/test_preprocessing_integration.py -v
pytest test/ -v -s  # All tests with output
```

Test data: `test/testing ePIs/` contains real ePI bundles (Karvea, Flucelvax, Dovato, etc.)

## Critical Conventions

### 1. BeautifulSoup HTML Handling
Always use `lxml` parser for consistency:
```python
soup = BeautifulSoup(html, 'lxml')
# lxml wraps content in <html><body>, extract properly:
if soup.body:
    return ''.join(str(child) for child in soup.body.children)
```

### 2. Content Integrity Validation
After any HTML transformation, validate that text content is preserved:
```python
if validate_content_integrity(original_html, optimized_html):
    update_html_content(composition, optimized_html)
else:
    print("Warning: Validation failed. Keeping original.")
```

### 3. FHIR Extension Structure
HtmlElementLink extensions follow this pattern:
```json
{
  "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
  "extension": [
    {"url": "elementClass", "valueString": "pregnancyCategory"},
    {"url": "concept", "valueCodeableReference": {"concept": {"coding": [{"code": "preg", "display": "Pregnancy"}]}}}
  ]
}
```

**Important**: Always use `HtmlElementLink.STRUCTURE_DEFINITION_URL` constant or `get_element_classes()` helper rather than hardcoding the URL.

### 4. Working with Composition Sections
Sections can be deeply nested. Always process recursively:
```python
def _process_sections_recursively(sections, stats):
    for section in sections:
        # Process this section's HTML
        html_content = get_html_content(section)
        if html_content and not html_content.is_empty:
            # ... optimization logic ...
        
        # Process subsections
        if 'section' in section:
            _process_sections_recursively(section['section'], stats)
```

## Common Pitfalls

1. **Forgetting to check subsections** - Classes and HTML exist at all section levels, not just Composition.text.div
2. **Not validating content integrity** - Always call `validate_content_integrity()` after HTML modifications
3. **Modifying dict while iterating** - When removing extensions, iterate over a copy: `for ext in list(extensions)`
4. **Assuming single-level structure** - Sections can be nested arbitrarily deep (section → section → section...)

## OpenAPI & Code Generation

The API is defined in `preprocessor/openapi/openapi.yaml`. To regenerate server code:
```powershell
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate `
  -i https://raw.githubusercontent.com/Gravitate-Health/preprocessing-service-example/refs/heads/main/openapi.yaml `
  -g python-flask -o /local/ --additional-properties=packageName=preprocessor
```

## CI/CD

Images published to GHCR: `ghcr.io/gravitate-health/preprocessing-service-cleaner:main`
See `.github/workflows/docker-publish.yml` for automated builds on push to main.
