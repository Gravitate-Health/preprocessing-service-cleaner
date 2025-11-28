# Test Documentation

## Integration Tests

### test_preprocessing_integration.py

Comprehensive integration tests for the preprocessing pipeline using real ePI examples from the `testing ePIs/` directory.

#### Test Classes

##### TestPreprocessingWithKarvea
Tests using the Karvea (Bundle-Processedbundlekarvea.json) ePI which contains HtmlElementLink extensions and CSS classes in nested subsections.

**Key Tests:**
- `test_load_karvea_bundle`: Verifies the bundle loads correctly
- `test_karvea_has_composition_with_html_element_links`: Confirms HtmlElementLink extensions exist
- `test_karvea_composition_html_has_classes`: Verifies class names in Composition HTML
- `test_karvea_section_html_has_classes`: Checks for classes in section HTML
- `test_extract_classes_from_karvea_composition`: Tests class extraction from Composition
- `test_extract_classes_from_karvea_section`: Tests class extraction from sections
- `test_optimize_preserves_classes`: Ensures HTML optimization preserves CSS classes
- `test_full_preprocessing_pipeline`: End-to-end test of the complete preprocessing flow

**Important:** The Karvea ePI has CSS classes like `pregnancyCategory` and `breastfeedingCategory` in **subsections** (not top-level sections), which tests the recursive section processing.

##### TestPreprocessingWithFlucelvax
Tests using the Flucelvax ePI for additional coverage.

##### TestPreprocessingAPI
Tests the HTTP API endpoints:
- POST with valid ePI
- POST with no body (400 error)
- POST with invalid resource type (400 error)

#### Running the Tests

```bash
# Install dependencies (if in a virtualenv)
pip install pytest

# Run all tests
pytest test/ -v

# Run all integration tests
pytest test/test_preprocessing_integration.py -v

# Run specific test class
pytest test/test_preprocessing_integration.py::TestPreprocessingWithKarvea -v

# Run specific test
pytest test/test_preprocessing_integration.py::TestPreprocessingWithKarvea::test_full_preprocessing_pipeline -v -s

# Run with output
pytest test/test_preprocessing_integration.py -v -s

# Run standalone tests (no pytest required)
python test/test_html_element_link_standalone.py
python test/test_html_content_manager_standalone.py
python test/test_html_optimization_standalone.py
```

## Bug Fix: Subsection HTML Processing

### The Problem

The preprocessing service was incorrectly removing HtmlElementLink extensions even when the referenced CSS classes existed in the ePI content. 

**Root Cause:**
- CSS classes like `pregnancyCategory` and `breastfeedingCategory` exist in **subsections** (nested sections)
- The original code only processed top-level entries and sections
- It never extracted HTML from subsections, so it couldn't find the classes
- This caused valid HtmlElementLink extensions to be removed incorrectly

### The Solution

Updated `preprocess_controller.py` to:

1. **Process sections recursively** - Added `_process_sections_recursively()` to optimize HTML in all sections and subsections
2. **Collect classes from entire tree** - Added `_collect_all_html_classes_from_resource()` to gather CSS classes from:
   - Resource-level `text.div`
   - All top-level sections' `text.div`
   - All nested subsections' `text.div` (recursively)
3. **Clean up based on complete data** - Only remove HtmlElementLink extensions for classes that truly don't exist anywhere in the content

### Verification

Run `test_fix.py` to verify the fix:

```bash
python3 test_fix.py
```

Expected output shows all important classes found:
```
✓ pregnancyCategory: FOUND
✓ breastfeedingCategory: FOUND
✓ lactose: FOUND
✓ contra-indication-pregnancy: FOUND
...
```

## Directory Structure

```
test/
├── README_TESTS.md                           # This file
├── __init__.py                               # Package initialization
├── testing ePIs/                             # Real ePI test data
│   ├── Bundle-Processedbundlekarvea.json
│   ├── Bundle-processedbundleflucelvax.json
│   └── ... (other test bundles)
├── test_preprocessing_integration.py         # Integration tests
├── test_fhir_epi.py                         # Unit tests
├── test_html_element_link.py                # Unit tests
├── test_preprocess_controller.py            # Unit tests
├── test_real_epis.py                        # Real ePI tests
├── test_html_element_link_standalone.py     # Standalone runner
├── test_html_content_manager_standalone.py  # Standalone runner
├── test_html_optimization_standalone.py     # Standalone runner
├── debug_class_extraction.py                # Debug tool
└── test_fix.py                              # Quick verification
```

## Test Data

The `testing ePIs/` directory contains real ePI bundles:

- **Bundle-Processedbundlekarvea.json** - Karvea ePI with nested sections containing CSS classes
- **Bundle-processedbundleflucelvax.json** - Flucelvax ePI
- **Bundle-processedbundledovato-en.json** - Dovato English ePI
- **Bundle-processedbundledovato-es.json** - Dovato Spanish ePI
- Other ePI variants for comprehensive testing

These files test real-world scenarios and edge cases.
