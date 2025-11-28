"""
Tests for style and unaccounted class cleanup feature
"""
import unittest
from preprocessor.models.html_optimizer import cleanup_html_styles_and_classes


class TestStyleCleanup(unittest.TestCase):
    """Test cleanup_html_styles_and_classes function"""
    
    def test_removes_style_attributes(self):
        """Test that style attributes are removed"""
        html = '<div style="color: red;">Hello</div>'
        allowed_classes = set()
        result = cleanup_html_styles_and_classes(html, allowed_classes)
        
        self.assertNotIn('style', result)
        self.assertIn('Hello', result)
    
    def test_removes_unaccounted_classes(self):
        """Test that classes not in allowed set are removed"""
        html = '<div class="allowed other">Hello</div>'
        allowed_classes = {'allowed'}
        result = cleanup_html_styles_and_classes(html, allowed_classes)
        
        self.assertIn('allowed', result)
        self.assertNotIn('other', result)
        self.assertIn('Hello', result)
    
    def test_keeps_allowed_classes(self):
        """Test that allowed classes are kept"""
        html = '<div class="pregnancyCategory breastfeedingCategory">Hello</div>'
        allowed_classes = {'pregnancyCategory', 'breastfeedingCategory'}
        result = cleanup_html_styles_and_classes(html, allowed_classes)
        
        self.assertIn('pregnancyCategory', result)
        self.assertIn('breastfeedingCategory', result)
        self.assertIn('Hello', result)
    
    def test_removes_class_attribute_when_no_allowed_classes(self):
        """Test that class attribute is removed when no classes are allowed"""
        html = '<div class="notallowed">Hello</div>'
        allowed_classes = set()
        result = cleanup_html_styles_and_classes(html, allowed_classes)
        
        self.assertNotIn('class', result)
        self.assertIn('Hello', result)
    
    def test_complex_html_with_multiple_elements(self):
        """Test cleanup on complex HTML with multiple elements"""
        html = '''
        <div class="allowed" style="color: red;">
            <p class="notallowed" style="font-size: 12px;">Text 1</p>
            <span class="allowed other">Text 2</span>
        </div>
        '''
        allowed_classes = {'allowed'}
        result = cleanup_html_styles_and_classes(html, allowed_classes)
        
        # No style attributes
        self.assertNotIn('style', result)
        # Allowed class kept
        self.assertIn('allowed', result)
        # Unallowed classes removed
        self.assertNotIn('notallowed', result)
        self.assertNotIn('other', result)
        # Content preserved
        self.assertIn('Text 1', result)
        self.assertIn('Text 2', result)
    
    def test_preserves_other_attributes(self):
        """Test that non-class, non-style attributes are preserved"""
        html = '<div id="test" class="notallowed" style="color: red;" data-value="123">Hello</div>'
        allowed_classes = set()
        result = cleanup_html_styles_and_classes(html, allowed_classes)
        
        self.assertIn('id="test"', result)
        self.assertIn('data-value="123"', result)
        self.assertNotIn('style', result)
        self.assertNotIn('class', result)
        self.assertIn('Hello', result)
    
    def test_empty_html(self):
        """Test handling of empty HTML"""
        html = ''
        allowed_classes = set()
        result = cleanup_html_styles_and_classes(html, allowed_classes)
        
        self.assertEqual(result, '')
    
    def test_html_without_classes_or_styles(self):
        """Test HTML that has no classes or styles"""
        html = '<div><p>Hello World</p></div>'
        allowed_classes = {'someclass'}
        result = cleanup_html_styles_and_classes(html, allowed_classes)
        
        self.assertIn('Hello World', result)
        self.assertNotIn('class', result)
        self.assertNotIn('style', result)
    
    def test_nested_elements_with_mixed_classes(self):
        """Test nested elements with some allowed and some not allowed classes"""
        html = '''
        <div class="outer allowed">
            <p class="middle notallowed">
                <span class="inner allowed">Text</span>
            </p>
        </div>
        '''
        allowed_classes = {'allowed'}
        result = cleanup_html_styles_and_classes(html, allowed_classes)
        
        # Count how many times 'allowed' appears in class attributes
        self.assertEqual(result.count('class="allowed"'), 2)
        self.assertNotIn('outer', result)
        self.assertNotIn('middle', result)
        self.assertNotIn('notallowed', result)
        self.assertNotIn('inner', result)
        self.assertIn('Text', result)


if __name__ == '__main__':
    unittest.main()
