import xml.etree.ElementTree as ET
import html
import re

def clean_cell_value(value):
    """Remove HTML tags from a string."""
    return re.sub(r'<[^>]+>', '', value).strip()

def convert_drawio_to_plantuml(xml_path, output_path):
    # Load and parse the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extract relevant information from mxCell elements
    cells_data = []
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        cell_value = cell.get('value')
        cell_style = cell.get('style')

        if cell_value:
            cell_value = html.unescape(cell_value)

            # Extracting style information
            styles = {}
            if cell_style:
                for style in cell_style.split(';'):
                    if '=' in style:
                        key, value = style.split('=')
                        styles[key] = value

            cells_data.append({
                'id': cell_id,
                'value': cell_value,
                'styles': styles
            })

    # Define the mapping for Archimate types to PlantUML definitions
    archimate_to_plantuml = {
        'goal': 'Motivation_Goal',
        'capability': 'Strategy_Capability',
        'constraint': 'Motivation_Constraint',
        'course': 'Strategy_CourseOfAction',
        'proc': 'Business_Service',
        'gap': 'Implementation_Gap',
        'deliverable': 'Implementation_Deliverable'
    }

    # Generate PlantUML syntax based on the extracted cell data
    plantuml_output = ["@startuml", "!include <archimate/Archimate>"]

    for cell in cells_data:
        # Identify Archimate type based on style attribute
        shape_type = cell['styles'].get('shape', '').split('.')[-1]
        app_type = cell['styles'].get('appType', '').lower()
        archimate_type = app_type if app_type else shape_type

        if archimate_type in archimate_to_plantuml:
            name = clean_cell_value(cell['value'])
            line = f"{archimate_to_plantuml[archimate_type]}({cell['id']}, \"{name}\")"
            plantuml_output.append(line)

    # Extract relationships (edges) and their labels from mxCell elements
    relationships = []
    for cell in root.findall('.//mxCell'):
        source_id = cell.get('source')
        target_id = cell.get('target')
        value = cell.get('value')

        if source_id and target_id:
            if value:
                value = clean_cell_value(value)
            relationships.append({
                'source': source_id,
                'target': target_id,
                'label': value
            })

    # Add relationships to the PlantUML output
    for relation in relationships:
        if relation['label']:
            line = f"{relation['source']} --> {relation['target']} : {relation['label']}"
        else:
            line = f"{relation['source']} --> {relation['target']}"
        plantuml_output.append(line)

    plantuml_output.append("@enduml")

    # Write the PlantUML output to a file
    with open(output_path, 'w') as f:
        for line in plantuml_output:
            f.write(line + '\n')

# Example usage (can be adjusted or commented out):
convert_drawio_to_plantuml('Strategy Execution Patterns.xml', 'output.puml')
