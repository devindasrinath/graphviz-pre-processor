from io import BytesIO

from lxml import etree
import re
import xml.etree.ElementTree as et


class SVGExtractor:
    @staticmethod
    def extract_data(svg_file):
        parser = etree.XMLParser(remove_blank_text=True)
        with open(svg_file, 'rb') as file:
            svg_content = file.read()

        tree = etree.parse(BytesIO(svg_content), parser)
        root = tree.getroot()

        nodes = {}
        edges = []
        arrow_heads = []

        namespaces = {
            'svg': 'http://www.w3.org/2000/svg',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

        for elem in root.findall('.//svg:g[@class="node"]', namespaces):
            # Extract the title value
            title_elem = elem.find('.//{http://www.w3.org/2000/svg}title', namespaces)
            node_title = title_elem.text if title_elem is not None else None

            if node_title:  # Proceed only if title exists
                polygon_elem = elem.find('.//{http://www.w3.org/2000/svg}polygon', namespaces)
                image_elem = elem.find('.//{http://www.w3.org/2000/svg}image', namespaces)
                text_elem = elem.find('.//{http://www.w3.org/2000/svg}text', namespaces)

                if image_elem is not None:
                    x = float(image_elem.get('x'))
                    y = float(image_elem.get('y'))
                    width = image_elem.get('width')
                    height = image_elem.get('height')
                    xlink = image_elem.get('{http://www.w3.org/1999/xlink}href')
                    points = polygon_elem.get('points') if polygon_elem is not None else None
                    nodes[node_title] = {
                        'coordinate': (x, y),
                        'points': points,
                        'lengths': (width, height),
                        'xlink': xlink
                    }
                else:
                    x = float(text_elem.get('x'))
                    y = float(text_elem.get('y'))
                    points = polygon_elem.get('points') if polygon_elem is not None else None
                    nodes[node_title] = {
                        'coordinate': (x, y),
                        'points': points
                    }

        for elem in root.findall('.//{http://www.w3.org/2000/svg}g[@class="edge"]'):
            path_elem = elem.find('.//{http://www.w3.org/2000/svg}path')
            if path_elem is not None:
                d = path_elem.get('d')
                coords = SVGExtractor._parse_path_d_attribute(d)
                edges.append((coords, d))
            poly_elem = elem.find('.//{http://www.w3.org/2000/svg}polygon')
            if poly_elem is not None:
                poly = poly_elem.get('points')
                arrow_heads.append(poly)

        return nodes, edges, arrow_heads

    @staticmethod
    def _parse_path_d_attribute(d):
        path_commands = re.findall(r'([MLC])([^MLC]*)', d)
        coords = []

        for command, values in path_commands:
            if values:
                pairs = values.strip().split()
                for pair in pairs:
                    if ',' in pair:
                        (x, y) = map(float, pair.split(','))
                        if (x, y) not in coords:
                            coords.append((x, y))

        filtered_coords = []
        for i in range(len(coords)):
            if i == 0 or i == len(coords) - 1:
                filtered_coords.append(coords[i])
            else:
                prev_coord = coords[i - 1]
                curr_coord = coords[i]
                next_coord = coords[i + 1]
                if not ((prev_coord[0] == curr_coord[0] == next_coord[0]) or (
                        prev_coord[1] == curr_coord[1] == next_coord[1])):
                    filtered_coords.append(curr_coord)

        return filtered_coords

    @staticmethod
    def extract_svg_attributes(svg_file):
        """
        Extracts the width, height, viewBox, and transform attributes from the given SVG content.

        Args:
            svg_content (str): The SVG content as a string.

        Returns:
            dict: A dictionary containing the extracted attributes.
            :param svg_file:
        """
        parser = etree.XMLParser(remove_blank_text=True)
        with open(svg_file, 'rb') as file:
            svg_content = file.read()

        tree = etree.parse(BytesIO(svg_content), parser)
        root = tree.getroot()

        svg_attributes = {
            'width': root.get('width'),
            'height': root.get('height'),
            'viewBox': root.get('viewBox')
        }

        namespaces = {
            'svg': 'http://www.w3.org/2000/svg',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

        # Extract the transform attribute from the first <g> tag, if it exists
        g_elem = root.find('.//{http://www.w3.org/2000/svg}g', namespaces)
        if g_elem is not None:
            svg_attributes['transform'] = g_elem.get('transform')

        # Extract the top-level polygon element and return its points
        polygon_elem = root.find('.//{http://www.w3.org/2000/svg}polygon', namespaces)
        if polygon_elem is not None:
            svg_attributes['polygon_points'] = polygon_elem.get('points')
        else:
            svg_attributes['polygon_points'] = None

        return svg_attributes
