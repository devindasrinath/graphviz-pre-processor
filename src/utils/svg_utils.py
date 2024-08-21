import json
import os
import re

import graphviz
from io import BytesIO
from lxml import etree
import os
import requests
import graphviz


class SVGUtils:

    @staticmethod
    def clear_and_download_images(dot_file, download_folder):
        # Create the download folder if it doesn't exist
        os.makedirs(download_folder, exist_ok=True)

        # Remove all SVG files in the download folder
        for filename in os.listdir(download_folder):
            if filename.endswith('.svg'):
                file_path = os.path.join(download_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # Dictionary to map URL to local file path
        url_to_local_map = {}

        # Create a new dot file with the updated image paths
        new_dot_file = dot_file.replace('.dot', '_modified.dot')

        with open(dot_file, 'r') as original_file, open(new_dot_file, 'w') as modified_file:
            for line in original_file:
                if 'image=' in line:
                    # Extract the image URL (it will be enclosed in double quotes)
                    start = line.find('image="') + 7
                    end = line.find('"', start)
                    image_url = line[start:end]

                    if image_url.startswith("http"):  # Only process URLs
                        # Get the image filename from the URL
                        image_name = os.path.basename(image_url)
                        local_image_path = os.path.join(download_folder, image_name)

                        # Download the image
                        response = requests.get(image_url)
                        with open(local_image_path, 'wb') as img_file:
                            img_file.write(response.content)

                        # Replace the URL with the local image path in the DOT file
                        line = line.replace(image_url, local_image_path)

                        # Update the map
                        url_to_local_map[image_url] = local_image_path

                # Write the modified line to the new DOT file
                modified_file.write(line)

        # Return the new DOT file and the mapping
        return new_dot_file, url_to_local_map

    @staticmethod
    def replace_local_paths_with_urls(svg_file, url_to_local_map):
        # Read the SVG file
        with open(svg_file, 'r') as file:
            svg_content = file.read()

        # Create a reverse mapping from local paths to URLs
        local_to_url_map = {v: k for k, v in url_to_local_map.items()}

        # Replace local paths with URLs
        for local_path, url in local_to_url_map.items():
            if local_path in svg_content:
                svg_content = svg_content.replace(local_path, url)

        # Write the updated SVG content back to the original file
        with open(svg_file, 'w') as file:
            file.write(svg_content)

        return svg_file

    @staticmethod
    def generate_svg_from_modified_dot_file(dot_file, svg_file, download_folder):
        # Step 1: Clear the existing images and download the new ones
        new_dot_file, url_to_local_map = SVGUtils.clear_and_download_images(dot_file, download_folder)

        # Step 2: Generate the SVG from the modified DOT file
        name, extension = svg_file.rsplit('.', 1)
        graph = graphviz.Source.from_file(new_dot_file)
        graph.render(filename=name, format=extension, cleanup=True)

        # Step 3: Return the new DOT file and the URL-to-local map
        return new_dot_file, url_to_local_map

    @staticmethod
    def generate_svg_from_dot_file(dot_file, svg_file):
        name, extension = svg_file.rsplit('.', 1)
        graph = graphviz.Source.from_file(dot_file)
        graph.render(filename=name, format=extension, cleanup=True)

    @staticmethod
    def generate_svg_from_modified_dot_content(dot_content, svg_file, dot_file, download_folder):
        # Step 0: Save original dot file
        with open(dot_file, 'w') as file:
            file.write(dot_content)

        # Step 1: Clear the existing images and download the new ones
        new_dot_file, url_to_local_map = SVGUtils.clear_and_download_images(dot_file, download_folder)

        # Step 2: Generate the SVG from the modified DOT file
        name, extension = svg_file.rsplit('.', 1)
        graph = graphviz.Source.from_file(new_dot_file)
        graph.render(filename=name, format=extension, cleanup=True)

        # Step 3: Return the new DOT file and the URL-to-local map
        return new_dot_file, url_to_local_map

    @staticmethod
    def generate_svg_from_dot_content(dot_content, svg_file, dot_file):
        name, extension = svg_file.rsplit('.', 1)
        # Create a graph from DOT content
        graph = graphviz.Source(dot_content)
        # Render the graph to an SVG file
        graph.render(filename=name, format=extension, cleanup=True)

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
    def create_json(nodes, edges, polygons, svg_attributes, save_path):
        data = {'svg_attributes': svg_attributes,
                'nodes': nodes,
                'edges': edges,
                'polygons': polygons}
        json_object = json.dumps(data, indent=4)
        # Open the file in write mode and save the JSON object
        with open(save_path, 'w') as file:
            json.dump(data, file, indent=4)  # `indent=4` for pretty-printing
        return json_object
