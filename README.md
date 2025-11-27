# Preprocessing Service

## Overview

This service provides robust preprocessing for FHIR ePI (electronic Product Information) bundles, supporting extraction, validation, and modification of both FHIR extensions and embedded HTML content. It is designed for pharmaceutical and healthcare data pipelines, enabling safe and flexible manipulation of FHIR R4 resources, including custom extensions and XHTML narratives.

### Key Features
- FhirEPI model for structured ePI bundle parsing
- HtmlElementLink extension management (CRUD operations)
- HTML content extraction, analysis, and modification (from `Composition.text.div`)
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

### 3. API Endpoints
- See `openapi/openapi.yaml` for full specification.
- Main endpoint: `/preprocess` (accepts FHIR Bundle, returns processed bundle)

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

## Testing

Standalone test runners are provided for all major components:
- `test_html_element_link_standalone.py`
- `test_html_content_manager_standalone.py`

Run with:
```powershell
python test_html_element_link_standalone.py
python test_html_content_manager_standalone.py
```

## Documentation

See the following markdown files for detailed guides and examples:
- `HTMLELEMENTLINK_GUIDE.md`
- `HTMLELEMENTLINK_QUICK_REFERENCE.md`
- `HTMLELEMENTLINK_EXAMPLES.md`
- `HTMLELEMENTLINK_SUMMARY.md`
- `HTMLELEMENTLINK_INDEX.md`
- `HTMLELEMENTLINK_DELIVERABLES.md`

## License

See `LICENSE` for details.