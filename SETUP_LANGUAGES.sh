#!/bin/bash
# Quick Setup Guide for Multi-Language Support

echo "================================"
echo "Multi-Language Support Setup"
echo "================================"

# Step 1: Apply migrations
echo ""
echo "Step 1: Applying database migrations..."
echo "Run: python manage.py migrate"
echo ""

# Step 2: Update URLs
echo "Step 2: URLs have been configured"
echo "Available routes:"
echo "  - /language/               - Select language"
echo "  - /language/set/           - Set language (POST)"
echo "  - /language/settings/      - Language preferences page"
echo "  - /api/translation/<key>/  - Get translation API"
echo ""

# Step 3: Template usage
echo "Step 3: Using translations in templates"
echo "Add to template: {% load custom_tags %}"
echo "Then use: {% t 'welcome' %}"
echo ""

# Step 4: View usage
echo "Step 4: Using translations in views"
echo "Example:"
echo "  from .language_utils import get_translation"
echo "  text = get_translation('welcome', user_language)"
echo ""

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Run: python manage.py migrate"
echo "2. Update your templates to use {% t 'key' %} tags"
echo "3. Test language selection at /language/"
echo "4. Test language settings at /language/settings/"
echo ""
