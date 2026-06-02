import os
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime
from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

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

def generate_report():
    base_dir = Path(__file__).parent
    features_dir = base_dir / "clinical_mdr_api" / "tests" / "acceptance" / "features"
    xml_path = base_dir / "reports" / "unit_report.xml"
    
    # Parse JUnit XML if exists
    xml_root = None
    if xml_path.exists():
        try:
            tree = ET.parse(xml_path)
            xml_root = tree.getroot()
        except Exception as e:
            print(f"Warning: Failed to parse XML at {xml_path}: {e}")
            
    parser = Parser()
    
    # Store data by domain
    domains_data = {}

    for feature_file in features_dir.rglob("*.feature"):
        with open(feature_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        try:
            gherkin_document = parser.parse(TokenScanner(content))
        except Exception as e:
            print(f"Error parsing {feature_file}: {e}")
            continue
            
        feature = gherkin_document.get('feature')
        if not feature:
            continue
            
        feature_name = feature.get('name', 'Unnamed Feature')
        feature_desc = feature.get('description', '')
        
        # default domain based on directory
        domain = feature_file.parent.name.replace('_', ' ').title()
        
        # parse tags for @domain:xxx and @FS-xxx
        fs_ids = []
        for tag in feature.get('tags', []):
            tag_name = tag['name']
            if tag_name.startswith('@domain:'):
                domain = tag_name.split(':')[1].replace('_', ' ')
            elif tag_name.startswith('@FS-'):
                fs_ids.append(tag_name[1:])
                
        if domain not in domains_data:
            domains_data[domain] = []
            
        feature_scenarios = []
        for child in feature.get('children', []):
            scenario = child.get('scenario')
            if not scenario:
                continue
                
            scenario_name = scenario.get('name', '')
            
            # Scenario specific tags
            scenario_fs_ids = list(fs_ids)
            for tag in scenario.get('tags', []):
                tag_name = tag['name']
                if tag_name.startswith('@FS-'):
                    scenario_fs_ids.append(tag_name[1:])
            
            steps = []
            for step in scenario.get('steps', []):
                steps.append(f"{step['keyword'].strip()} {step['text']}")
                
            test_name = sanitize_test_name(scenario_name)
            status = get_test_status(xml_root, test_name)
            
            feature_scenarios.append({
                'name': scenario_name,
                'fs_ids': list(set(scenario_fs_ids)),
                'steps': steps,
                'status': status
            })
            
        domains_data[domain].append({
            'name': feature_name,
            'description': feature_desc,
            'scenarios': feature_scenarios,
            'file_name': feature_file.name
        })

    # Generate HTML
    html = [
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
        ".req-title { font-weight: bold; color: #555; margin-top: 10px; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }",
        "</style></head><body>",
        f"<h1>Living Validation Report</h1><p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
    ]
    
    for domain, features in sorted(domains_data.items()):
        html.append(f"<div class='domain'><h2 class='domain-title'>{domain}</h2>")
        for feature in features:
            html.append(f"<div class='feature'><h3>Feature: {feature['name']}</h3>")
            if feature['description']:
                html.append(f"<p>{feature['description']}</p>")
                
            for scenario in feature['scenarios']:
                html.append(f"<div class='scenario'>")
                html.append(f"<h4>Scenario: {scenario['name']}</h4>")
                
                if scenario['fs_ids']:
                    html.append("<div>")
                    for fs_id in scenario['fs_ids']:
                        html.append(f"<span class='fs-link'>Traceability: {fs_id}</span>")
                    html.append("</div>")
                
                status = scenario['status']
                status_text = "Verified" if status == "Passed" else ("Non-Compliant" if status == "Failing" else status)
                html.append(f"<div class='req-title'>Validation Proof</div>")
                html.append(f"<div class='status {status}'>{status_text}</div>")
                
                html.append(f"<div class='req-title'>Business Requirements</div>")
                html.append("<div class='steps'>")
                for step in scenario['steps']:
                    html.append(f"<div>{step}</div>")
                html.append("</div>")
                
                html.append("</div>") # end scenario
            html.append("</div>") # end feature
        html.append("</div>") # end domain
        
    html.append("</body></html>")
    
    out_path = base_dir / "reports" / "validation_report.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print(f"Validation report generated at: {out_path}")

if __name__ == "__main__":
    generate_report()
