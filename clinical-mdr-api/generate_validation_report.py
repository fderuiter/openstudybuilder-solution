import os
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime
import html
import logging
from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

logger = logging.getLogger(__name__)

def sanitize_test_name(name):
    """Matches the pytest-bdd algorithm for converting scenario names to test names."""
    sanitized = re.sub(r'\W+', '_', name).strip('_').lower()
    return f"test_{sanitized}"

def get_test_status(xml_root, test_name):
    """Look up testcase in JUnit XML and return passed/failed/missing."""
    if xml_root is None:
        return "Missing"
    
    # In some versions, the classname or name might have modifications, but we search by name
    for testcase in xml_root.findall(".//testcase"):
        if testcase.get("name") == test_name:
            if testcase.find("failure") is not None or testcase.find("error") is not None:
                return "Failing"
            if testcase.find("skipped") is not None:
                return "Skipped"
            return "Passed"
    return "Missing"

def parse_markdown_metadata(content):
    metadata = {}
    body = content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]
            for line in frontmatter.split('\n'):
                line = line.strip()
                if ':' in line:
                    k, v = line.split(':', 1)
                    metadata[k.strip()] = v.strip()
    return metadata, body

def get_iso_category(iso_type):
    iso_type = (iso_type or '').strip().upper()
    if iso_type == 'CAPABILITY':
        return 'Capabilities'
    elif iso_type == 'CONSTRAINTS':
        return 'Constraints'
    elif iso_type == 'SYSTEM_CONTEXT':
        return 'System Context'
    return 'Uncategorized'

def generate_report():
    base_dir = Path(__file__).parent
    repo_root = base_dir.parent
    
    xml_path = base_dir / "reports" / "unit_report.xml"
    
    # Parse JUnit XML if exists
    xml_root = None
    if xml_path.exists():
        try:
            tree = ET.parse(xml_path)
            xml_root = tree.getroot()
        except Exception as e:
            logger.warning(f"Failed to parse XML at {xml_path}: {e}", exc_info=True)
            
    parser = Parser()
    
    # Store data by iso_category
    iso_data = {
        'System Context': [],
        'Capabilities': [],
        'Constraints': [],
        'Uncategorized': []
    }
    
    feature_dirs = [
        base_dir / "clinical_mdr_api" / "tests" / "acceptance" / "features",
        repo_root / "system-tests" / "ui-tests" / "cypress" / "e2e" / "features"
    ]
    
    markdown_dirs = [
        repo_root / "documentation-portal" / "docs" / "guides",
        base_dir / "doc",
        repo_root / "studybuilder" / "doc"
    ]
    
    # Process Gherkin files
    for fdir in feature_dirs:
        if not fdir.exists():
            continue
        for feature_file in fdir.rglob("*.feature"):
            with open(feature_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            try:
                gherkin_document = parser.parse(TokenScanner(content))
            except Exception as e:
                logger.error(f"Error parsing {feature_file}: {e}", exc_info=True)
                continue
                
            feature = gherkin_document.get('feature')
            if not feature:
                continue
                
            feature_name = feature.get('name', 'Unnamed Feature')
            feature_desc = feature.get('description', '')
            
            iso_category = 'Uncategorized'
            fs_ids = []
            urs_ids = []
            
            for tag in feature.get('tags', []):
                tag_name = tag['name']
                if tag_name.startswith('@ISO_TYPE:'):
                    iso_category = get_iso_category(tag_name.split(':', 1)[1])
                elif tag_name.startswith('@FS-'):
                    fs_ids.append(tag_name[1:])
                elif tag_name.startswith('@URS-'):
                    urs_ids.append(tag_name[1:])
                    
            feature_scenarios = []
            for child in feature.get('children', []):
                scenario = child.get('scenario')
                if not scenario:
                    continue
                    
                scenario_name = scenario.get('name', '')
                
                scenario_fs_ids = list(fs_ids)
                scenario_urs_ids = list(urs_ids)
                for tag in scenario.get('tags', []):
                    tag_name = tag['name']
                    if tag_name.startswith('@FS-'):
                        scenario_fs_ids.append(tag_name[1:])
                    elif tag_name.startswith('@URS-'):
                        scenario_urs_ids.append(tag_name[1:])
                        
                steps = []
                for step in scenario.get('steps', []):
                    steps.append(f"{step['keyword'].strip()} {step['text']}")
                    
                test_name = sanitize_test_name(scenario_name)
                status = get_test_status(xml_root, test_name)
                
                feature_scenarios.append({
                    'name': scenario_name,
                    'fs_ids': list(dict.fromkeys(scenario_fs_ids)),
                    'urs_ids': list(dict.fromkeys(scenario_urs_ids)),
                    'steps': steps,
                    'status': status
                })
                
            if iso_category not in iso_data:
                iso_data[iso_category] = []
                
            iso_data[iso_category].append({
                'type': 'feature',
                'name': feature_name,
                'description': feature_desc,
                'scenarios': feature_scenarios,
                'file_name': feature_file.name
            })
            
    # Process Markdown files
    for mdir in markdown_dirs:
        if not mdir.exists():
            continue
        for md_file in mdir.rglob("*.md"):
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            metadata, body = parse_markdown_metadata(content)
            
            normalized_metadata = {k.upper(): v for k, v in metadata.items()}
            iso_type = normalized_metadata.get('ISO_TYPE', '')
            iso_category = get_iso_category(iso_type)
            
            # Extract parent requirements and functional specifications
            fs_ids = []
            urs_ids = []
            
            for k, v in normalized_metadata.items():
                if k in ['FS', 'FS_ID', 'FS_IDS']:
                    fs_ids.extend([s.strip() for s in v.split(',')])
                elif k in ['URS', 'URS_ID', 'URS_IDS']:
                    urs_ids.extend([s.strip() for s in v.split(',')])
                    
            title_match = re.search(r'^#\s+(.*)', body, re.MULTILINE)
            if title_match:
                name = title_match.group(1).strip()
            else:
                name = md_file.stem
                
            if iso_category not in iso_data:
                iso_data[iso_category] = []
                
            iso_data[iso_category].append({
                'type': 'markdown',
                'name': name,
                'description': body.strip(),
                'fs_ids': fs_ids,
                'urs_ids': urs_ids,
                'file_name': md_file.name,
                'scenarios': []
            })
            
    # Generate HTML
    html_lines = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'><title>Living Validation Report</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9; color: #333; }",
        "h1 { color: #2c3e50; }",
        ".domain { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }",
        ".domain-title { border-bottom: 2px solid #3498db; padding-bottom: 10px; color: #2980b9; }",
        ".feature { margin-top: 20px; }",
        ".scenario { border-left: 4px solid #bdc3c7; padding-left: 15px; margin: 15px 0; background: #fafafa; padding: 15px; border-radius: 0 4px 4px 0; }",
        ".status { font-weight: bold; display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; margin-bottom: 10px; }",
        ".Passed { background-color: #d4edda; color: #155724; }",
        ".Failing { background-color: #f8d7da; color: #721c24; }",
        ".Skipped { background-color: #fff3cd; color: #856404; }",
        ".Missing { background-color: #e2e3e5; color: #383d41; }",
        ".steps { font-family: monospace; background: #eee; padding: 10px; border-radius: 4px; margin-top: 10px; }",
        ".fs-link { display: inline-block; background: #e1f5fe; color: #0277bd; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }",
        ".urs-link { display: inline-block; background: #f3e5f5; color: #7b1fa2; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }",
        ".req-title { font-weight: bold; color: #555; margin-top: 10px; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }",
        ".markdown-desc { white-space: pre-wrap; font-family: monospace; background: #fdfdfd; padding: 10px; border: 1px solid #eee; margin-top: 10px; border-radius: 4px; }",
        "</style></head><body>",
        f"<h1>Living Validation Report</h1><p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
    ]
    
    # Sort categories in specific order
    display_order = ['System Context', 'Capabilities', 'Constraints', 'Uncategorized']
    
    for category in display_order:
        items = iso_data.get(category, [])
        if not items:
            continue
            
        html_lines.append(f"<div class='domain'><h2 class='domain-title'>{category}</h2>")
        
        for item in items:
            item_type = item.get('type')
            label = "Feature" if item_type == 'feature' else "Requirement"
            
            safe_name = html.escape(item['name'])
            html_lines.append(f"<div class='feature'><h3>{label}: {safe_name}</h3>")
            
            # For Markdown items, show URS and FS traces at the top
            if item_type == 'markdown':
                if item.get('urs_ids') or item.get('fs_ids'):
                    html_lines.append("<div>")
                    for u in item.get('urs_ids', []):
                        html_lines.append(f"<span class='urs-link'>Parent URS: {html.escape(u)}</span>")
                    for f_id in item.get('fs_ids', []):
                        html_lines.append(f"<span class='fs-link'>Traceability: {html.escape(f_id)}</span>")
                    html_lines.append("</div>")
                
                if item['description']:
                    desc = item['description'][:500] + ('...' if len(item['description']) > 500 else '')
                    html_lines.append(f"<div class='markdown-desc'>{html.escape(desc)}</div>")
            else:
                if item['description']:
                    html_lines.append(f"<p>{html.escape(item['description'])}</p>")
                
            # Render scenarios (mainly for features)
            for scenario in item.get('scenarios', []):
                html_lines.append(f"<div class='scenario'>")
                html_lines.append(f"<h4>Scenario: {html.escape(scenario['name'])}</h4>")
                
                if scenario.get('urs_ids') or scenario.get('fs_ids'):
                    html_lines.append("<div>")
                    for u in scenario.get('urs_ids', []):
                        html_lines.append(f"<span class='urs-link'>Parent URS: {html.escape(u)}</span>")
                    for f_id in scenario.get('fs_ids', []):
                        html_lines.append(f"<span class='fs-link'>Traceability: {html.escape(f_id)}</span>")
                    html_lines.append("</div>")
                
                status = scenario['status']
                status_class = status if status in ["Passed", "Failing", "Skipped"] else "Missing"
                status_text = "Verified" if status == "Passed" else ("Non-Compliant" if status == "Failing" else status)
                safe_status_text = html.escape(status_text)
                
                html_lines.append(f"<div class='req-title'>Validation Proof</div>")
                html_lines.append(f"<div class='status {status_class}'>{safe_status_text}</div>")
                
                html_lines.append(f"<div class='req-title'>Business Requirements</div>")
                html_lines.append("<div class='steps'>")
                for step in scenario['steps']:
                    html_lines.append(f"<div>{html.escape(step)}</div>")
                html_lines.append("</div>")
                
                html_lines.append("</div>") # end scenario
            html_lines.append("</div>") # end item
        html_lines.append("</div>") # end category
        
    html_lines.append("</body></html>")
    
    out_path = base_dir / "reports" / "validation_report.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))
    logger.info(f"Validation report generated at: {out_path}")

if __name__ == "__main__":
    generate_report()
