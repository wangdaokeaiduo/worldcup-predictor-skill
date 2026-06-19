#!/usr/bin/env python3
import json
import sys
import os

def render_template(template_str, data):
    # A simple and robust recursive template renderer
    def get_value(keys, context):
        for k in keys.split('.'):
            if isinstance(context, dict):
                context = context.get(k, '')
            else:
                return ''
        return str(context)

    # Find all {{ key.subkey }} and replace them
    import re
    matches = re.findall(r'\{\{\s*(.*?)\s*\}\}', template_str)
    for match in matches:
        val = get_value(match, data)
        template_str = template_str.replace('{{ ' + match + ' }}', val).replace('{{' + match + '}}', val)
    return template_str

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_html.py <input_json> <output_html>")
        sys.exit(1)

    input_json = sys.argv[1]
    output_html = sys.argv[2]
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'report_template.html')

    try:
        with open(input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        html_content = render_template(template, data)

        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report generated successfully: {output_html}")
    except Exception as e:
        print(f"❌ Error generating report: {e}")
