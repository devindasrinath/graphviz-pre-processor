import json
import re

import graphviz
from io import BytesIO
from lxml import etree


class SVGUtils:
    @staticmethod
    def generate_svg_from_dot_file(dot_file, svg_file):
        graph = graphviz.Source.from_file(dot_file)
        graph.render(filename=svg_file, format='svg', cleanup=True)

    @staticmethod
    def generate_svg_from_dot_content(dot_content, svg_file, dot_file):
        # Create a graph from DOT content
        graph = graphviz.Source(dot_content)
        # Render the graph to an SVG file
        graph.render(filename=svg_file, format='svg', cleanup=True)

        with open(dot_file, 'w') as file:
            file.write(dot_content)

    @staticmethod
    def resize_svg(input_svg, output_svg, width, height, translate):
        with open(input_svg, 'rb') as file:
            svg_content = file.read()

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(BytesIO(svg_content), parser)
        root = tree.getroot()

        root.set('width', f'{width}px')
        root.set('height', f'{height}px')

        # Find the <g> element with the transform attribute and update the translate part
        for g in root.findall('.//{http://www.w3.org/2000/svg}g'):
            transform = g.get('transform')
            if transform:
                # Use regex to find and replace the translate values
                new_transform = re.sub(r'translate\([\d\s.,-]+\)', f'translate({translate[0]} {translate[1]})',
                                       transform)
                g.set('transform', new_transform)

        with open(output_svg, 'wb') as file:
            file.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
        print(f"SVG resized and saved to {output_svg}")

    @staticmethod
    def create_json(nodes, edges, polygons, general, save_path):
        data = {'general': general,
                'nodes': nodes,
                'edges': edges,
                'polygons': polygons}
        json_object = json.dumps(data, indent=4)
        # Open the file in write mode and save the JSON object
        with open(save_path, 'w') as file:
            json.dump(data, file, indent=4)  # `indent=4` for pretty-printing
        return json_object
