# Preprocessing Clueanup Service

![Docker Publish (GHCR)](https://github.com/Gravitate-Health/preprocessing-service-cleaner/actions/workflows/docker-publish.yml/badge.svg?branch=main)

## Overview

This service provides robust preprocessing for FHIR ePI (electronic Product Information) bundles, supporting extraction, validation, and modification of both FHIR extensions and embedded HTML content. It is designed for pharmaceutical and healthcare data pipelines, enabling safe and flexible manipulation of FHIR R4 resources, including custom extensions and XHTML narratives.

### Key Features
- FhirEPI model for structured ePI bundle parsing
- **Automatic HTML optimization** - removes non-functional tags and simplifies nested structures
- **Smart extension cleanup** - removes unused HtmlElementLink extensions based on actual HTML class usage
- HtmlElementLink extension management (CRUD operations)
- HTML content extraction, analysis, and modification (from `Composition.text.div`)
- Content integrity validation ensures safe transformations
- Standalone test runners for all major components
- Dockerized deployment and OpenAPI integration
- Extensive documentation and examples

## Usage Guide

### 1. Local Setup

#### Prerequisites
- Python 3.12+
- (Optional) Docker
- (Optional) Virtual environment

#### Install dependencies
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### Run tests
```powershell
python test_html_element_link_standalone.py
python test_html_content_manager_standalone.py
python test_html_optimization_standalone.py
```

### 2. Docker Usage

#### Build and run the service
```powershell
docker build -t preprocessing-service .
docker run --rm -p 8080:8080 preprocessing-service
```

#### Generate server code from OpenAPI (if needed)
```powershell
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate -i https://raw.githubusercontent.com/Gravitate-Health/preprocessing-service-example/refs/heads/main/openapi.yaml -g python-flask -o /local/ --additional-properties=packageName=preprocessor
```

### 2.1 GHCR Image (recommended)

Images are published automatically to GitHub Container Registry (GHCR) by CI for this repo and any forks.

- Canonical image for this repo: `ghcr.io/gravitate-health/preprocessing-service-cleaner`
- For forks: `ghcr.io/<your-github-username-or-org>/<your-fork-repo>`

#### Pull
```powershell
docker pull ghcr.io/gravitate-health/preprocessing-service-cleaner:main
# or a release tag, when available
docker pull ghcr.io/gravitate-health/preprocessing-service-cleaner:v1.0.0
```

#### Run
```powershell
docker run --rm -p 8080:8080 ghcr.io/gravitate-health/preprocessing-service-cleaner:main
```

#### Run with custom configuration
```powershell
# Disable HTML optimization
docker run --rm -p 8080:8080 -e ENABLE_HTML_OPTIMIZATION=false ghcr.io/gravitate-health/preprocessing-service-cleaner:main

# Disable unused link cleanup
docker run --rm -p 8080:8080 -e ENABLE_LINK_CLEANUP=false ghcr.io/gravitate-health/preprocessing-service-cleaner:main

# Disable both features (passthrough mode)
docker run --rm -p 8080:8080 -e ENABLE_HTML_OPTIMIZATION=false -e ENABLE_LINK_CLEANUP=false ghcr.io/gravitate-health/preprocessing-service-cleaner:main
```

#### Authenticate (if needed)
If the image is private or your org requires auth, login to GHCR:
```powershell
$env:CR_PAT = "<YOUR_GH_PAT_WITH_packages:read>"
$env:CR_PAT | docker login ghcr.io -u <YOUR_GH_USERNAME> --password-stdin
```

### 3. Configuration

The service can be configured using environment variables:

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ENABLE_HTML_OPTIMIZATION` | `true` | Enable/disable HTML optimization (empty tag removal, nested tag simplification) |
| `ENABLE_LINK_CLEANUP` | `true` | Enable/disable removal of unused HtmlElementLink extensions |
| `PYTHONUNBUFFERED` | `1` | Disable Python output buffering for real-time logs |

**Valid values for boolean flags:** `true`, `1`, `yes`, `on` (enable) or `false`, `0`, `no`, `off` (disable)

### 4. API Endpoints
- See `openapi/openapi.yaml` for full specification.
- Main endpoint: `/preprocess` (accepts FHIR Bundle, returns processed bundle)

## Preprocessing Pipeline

The `/preprocess` endpoint applies the following transformations (controlled by environment variables):

1. **HTML Optimization** (controlled by `ENABLE_HTML_OPTIMIZATION`)
   - Removes empty and non-functional tags (e.g., `<span></span>`, empty divs without attributes)
   - Simplifies nested tags of the same type (e.g., `<p class="c1"><p class="c2">text</p></p>` becomes `<p class="c1 c2">text</p>`)
   - Merges class attributes intelligently
   - Validates content integrity (text content must remain identical)
   - Processes all sections and subsections recursively

2. **Extension Cleanup** (controlled by `ENABLE_LINK_CLEANUP`)
   - Extracts all CSS classes actually used in the HTML (from all sections recursively)
   - Removes HtmlElementLink extensions that reference classes not present in the HTML
   - Keeps only extensions with active references

3. **Statistics & Logging**
   - Reports feature flag status on startup
   - Reports compositions processed, optimizations applied, and extensions removed
   - Validates each transformation for safety

## Manager Guides & Examples

### HtmlElementLink Manager

**Purpose:** Manage FHIR HtmlElementLink extensions in Composition resources.

**Key Functions:**
- `list_html_element_links(composition)`
- `add_html_element_link(composition, element_class, concept, replace_if_exists=False)`
- `remove_html_element_link(composition, element_class)`
- `get_html_element_link(composition, element_class)`

**Example Usage:**
```python
from preprocessor.models.html_element_link_manager import (
	list_html_element_links, add_html_element_link, remove_html_element_link
)

# List all HtmlElementLink extensions
links = list_html_element_links(composition)

# Add a new HtmlElementLink
add_html_element_link(composition, 'section-title', {'code': 'title', 'display': 'Section Title'})

# Remove an HtmlElementLink by class
remove_html_element_link(composition, 'section-title')
```

### HTML Content Manager

**Purpose:** Extract, analyze, and modify HTML content in FHIR Composition `text.div`.

**Key Functions:**
- `get_html_content(composition)`
- `update_html_content(composition, new_html)`
- `find_elements_by_class(html, class_name)`
- `replace_html_section(html, start_marker, end_marker, replacement)`
- `get_html_structure_summary(html)`

**Example Usage:**
```python
from preprocessor.models.html_content_manager import (
	get_html_content, update_html_content, find_elements_by_class, get_html_structure_summary
)

# Extract HTML from composition
html = get_html_content(composition)

# Find all elements with a specific class
elements = find_elements_by_class(html, 'epi-section')

# Get a summary of the HTML structure
summary = get_html_structure_summary(html)
print(summary)

# Update the HTML content in the composition
new_html = html.replace('<h1>', '<h2>')
update_html_content(composition, new_html)
```

### HTML Optimizer

**Purpose:** Optimize HTML by removing non-functional elements and simplifying structure while preserving content.

**Key Functions:**
- `optimize_html(html)` - Main optimization function
- `extract_html_classes(html)` - Get all CSS classes used in HTML
- `validate_content_integrity(original, optimized)` - Verify text content is preserved

**Example Usage:**
```python
from preprocessor.models.html_optimizer import (
    optimize_html, extract_html_classes, validate_content_integrity
)

# Optimize HTML (removes empty tags, simplifies nesting)
original = '<div><span></span><p class="c1"><p class="c2">Content</p></p></div>'
optimized = optimize_html(original)
# Result: '<div><p class="c1 c2">Content</p></div>'

# Extract classes
classes = extract_html_classes(optimized)
# Result: {'c1', 'c2'}

# Validate integrity
is_valid = validate_content_integrity(original, optimized)
# Result: True (text content "Content" preserved)
```

### HtmlElementLink Cleanup

**Purpose:** Remove unused HtmlElementLink extensions based on actual HTML class usage.

**Key Functions:**
- `cleanup_unused_html_element_links(composition, html_classes)` - Remove unused extensions
- `analyze_html_element_link_usage(composition, html_content)` - Analyze usage patterns

**Example Usage:**
```python
from preprocessor.models.html_element_link_cleanup import (
    cleanup_unused_html_element_links, analyze_html_element_link_usage
)
from preprocessor.models.html_optimizer import extract_html_classes

# Get classes from HTML
html_classes = extract_html_classes(composition['text']['div'])

# Remove unused extensions
stats = cleanup_unused_html_element_links(composition, html_classes)
print(f"Removed {stats['removed']} unused extensions")

# Analyze usage (for debugging)
analysis = analyze_html_element_link_usage(composition, composition['text']['div'])
print(f"Used classes: {analysis['used_classes']}")
print(f"Unused extensions: {analysis['unused_extension_classes']}")
```

## Testing

All tests are located in the `test/` directory and excluded from Docker builds.

### Test Files

**Unit Tests:**
- `test_fhir_epi.py` - FHIR ePI model tests
- `test_html_element_link.py` - HtmlElementLink extension tests
- `test_preprocess_controller.py` - Controller tests

**Integration Tests:**
- `test_preprocessing_integration.py` - End-to-end preprocessing pipeline tests with real ePIs
- `test_real_epis.py` - Real ePI bundle processing tests

**Standalone Test Runners:**
- `test_html_element_link_standalone.py` - HtmlElementLink extension tests
- `test_html_content_manager_standalone.py` - HTML content manipulation tests
- `test_html_optimization_standalone.py` - HTML optimization and cleanup tests

**Debug/Helper Scripts:**
- `debug_class_extraction.py` - Debug tool for class extraction analysis
- `test_fix.py` - Quick verification script for subsection processing

**Test Data:**
- `testing ePIs/` - Real ePI bundles for testing (Karvea, Flucelvax, Dovato, etc.)

### Running Tests

```bash
# Run with pytest (recommended)
pytest test/

# Run specific test file
pytest test/test_preprocessing_integration.py -v

# Run specific test class
pytest test/test_preprocessing_integration.py::TestPreprocessingWithKarvea -v

# Run with output
pytest test/ -v -s

# Run standalone tests (no pytest required)
python test/test_html_element_link_standalone.py
python test/test_html_content_manager_standalone.py
python test/test_html_optimization_standalone.py
```

### Test Coverage

- Empty tag removal and nested tag simplification
- Class extraction from HTML content (including nested subsections)
- Content integrity validation
- HtmlElementLink cleanup logic
- Recursive section processing
- Real ePI bundle processing with 8+ test bundles
- API endpoint validation

See `test/README_TESTS.md` for detailed test documentation.

## License

Licensed under Apache Software License 2.0, See `LICENSE` for details.