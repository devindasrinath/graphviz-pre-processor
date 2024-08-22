from collections import defaultdict
from shapely.geometry import LineString, Point

from src.constants.constants import BUMPER_RADIUS
from src.utils.svg_creator import SVGCreator
from src.utils.svg_extractor import SVGExtractor
from src.utils.svg_utils import SVGUtils


class SVGProcessor:

    def __init__(self, graph_config):
        self._graph_config = graph_config

    @staticmethod
    def extract_lines(edges):
        lines = []
        for line_coordinates in edges:
            for i in range(0, len(line_coordinates[0]) - 1):
                lines.append(LineString([line_coordinates[0][i], line_coordinates[0][i + 1]]))
        print("\nLines:")
        print(lines)
        return lines

    @staticmethod
    def find_overlaps(lines):
        lines_without_overlapped = lines.copy()
        overlaps = []
        for i, line1 in enumerate(lines):
            for j, line2 in enumerate(lines):
                if i < j and line1.intersects(line2):
                    intersection = line1.intersection(line2)
                    if intersection.geom_type == 'Point':
                        line1_start = Point(line1.coords[0])
                        line1_end = Point(line1.coords[-1])
                        line2_start = Point(line2.coords[0])
                        line2_end = Point(line2.coords[-1])
                        if not (intersection.equals(line1_start) or
                                intersection.equals(line1_end) or
                                intersection.equals(line2_start) or
                                intersection.equals(line2_end)):
                            overlaps.append((line1, line2, (intersection.x, intersection.y)))
                            if line1 in lines_without_overlapped:
                                lines_without_overlapped.remove(line1)
                            if line2 in lines_without_overlapped:
                                lines_without_overlapped.remove(line2)

        return overlaps, lines_without_overlapped

    @staticmethod
    def add_intersection_to_lines(overlaps):
        line_intersections = defaultdict(set)

        for line1, line2, intersection in overlaps:
            intersection_point = Point(intersection)
            line_intersections[line1].add(intersection_point)
            line_intersections[line2].add(intersection_point)

        unique_lines = []
        for line, intersections in line_intersections.items():
            all_points = list(line.coords)
            all_points.extend((pt.x, pt.y) for pt in intersections)
            all_points = sorted(set(all_points))
            unique_line = LineString(all_points)
            unique_lines.append(unique_line)

        return unique_lines

    @staticmethod
    def create_final_lines(lines):
        final_paths = []
        for line in lines:
            if len(line.coords) >= 3 and line.coords[0][1] == line.coords[-1][1]:
                final_paths.append(SVGProcessor._create_path_data(line))
            else:
                final_paths.append(SVGProcessor._create_path_data(LineString([line.coords[0], line.coords[-1]])))
        return final_paths

    @staticmethod
    def _create_bumper_path(x, y):
        return f"{x - BUMPER_RADIUS},{y} S{x},{y - BUMPER_RADIUS},{x + BUMPER_RADIUS},{y}"

    @staticmethod
    def _create_path_data(line):
        if len(line.coords) == 2:
            return f"d=M{line.coords[0][0]},{line.coords[0][1]} L{line.coords[1][0]},{line.coords[1][1]}"
        elif len(line.coords) >= 3:
            bumpers = ''.join([SVGProcessor._create_bumper_path(x, y) + 'L' for x, y in line.coords[1:-1]])
            return f"d=M{line.coords[0][0]},{line.coords[0][1]} L{bumpers}{line.coords[-1][0]},{line.coords[-1][1]}"

    def process(self, input_dot=None):
        error = "DOT content processed successfully"
        try:
            if input_dot is None:
                # Generate, resize, and extract SVG data
                new_dot_file, url_to_local_map = SVGUtils.generate_svg_from_modified_dot_file(
                    self._graph_config.dot_file, self._graph_config.svg_file, self._graph_config.input_folder)
                print('no dot file content found. generate from default dot file')
                SVGUtils.replace_local_paths_with_urls(self._graph_config.svg_file, url_to_local_map)
            else:
                # Generate, resize, and extract SVG data
                new_dot_file, url_to_local_map = SVGUtils.generate_svg_from_modified_dot_content(input_dot,
                                                                                                 self._graph_config.svg_file,
                                                                                                 self._graph_config.dot_file,
                                                                                                 self._graph_config.input_folder)
                SVGUtils.replace_local_paths_with_urls(self._graph_config.svg_file, url_to_local_map)
                print('dot file content found. generate from new dot file')

            # SVGUtils.resize_svg(f'{self._graph_config.svg_file}.svg', self._graph_config.output_svg,
            # self._graph_config.width, self._graph_config.height, self._graph_config.translate)

            nodes, edges, arrow_heads, clusters = SVGExtractor.extract_data(self._graph_config.svg_file)
            svg_attributes = SVGExtractor.extract_svg_attributes(self._graph_config.svg_file)
            lines = SVGProcessor.extract_lines(edges)
            overlaps, lines_without_overlapped = SVGProcessor.find_overlaps(lines)
            overlap_lines = SVGProcessor.add_intersection_to_lines(overlaps)

            all_lines = lines_without_overlapped + overlap_lines
            all_paths = SVGProcessor.create_final_lines(all_lines)

            # Print node coordinates and points
            print("Nodes:")
            for node_title, info in nodes.items():
                x, y = info['coordinate']
                points = info['points']
                print(f"Node {node_title}: x={x}, y={y}, points={points}")

            print("Clusters:")
            for cluster_title, info in clusters.items():
                points = info['points']
                print(f"Cluster {cluster_title}: points={points}")

            # Print edge coordinates and 'd' attributes
            print("\nEdges:")
            for coords, d in edges:
                print(f"Edge with 'd' attribute: {d}")
                print(f"Coordinates: {coords}")
            print(len(edges))

            # Print overlapping lines
            print("\nOverlapping lines:")
            for line1, line2, coordinates in overlaps:
                print(f"Line 1: {line1}, Line 2: {line2}, Intersection: {coordinates}")

            # Print unique lines after adding intersections
            print("\nUnique lines after adding intersections:")
            for line in overlap_lines:
                print(line)

            # Create a new SVG with the final paths
            svg_creator = SVGCreator(svg_attributes)

            # Add nodes to the new SVG
            for node_title, info in nodes.items():
                svg_creator.add_node(node_title, info)

            # Add nodes to the new SVG
            for cluster_title, info in clusters.items():
                svg_creator.add_cluster(cluster_title, info)

            # Add arrow heads to the new SVG
            for idx, path_data in enumerate(arrow_heads):
                svg_creator.add_arrow(idx + 1, path_data)

            # Add edges to the new SVG
            for idx, path_data in enumerate(all_paths):
                svg_creator.add_edge(idx + 1, path_data)

            # Save the final SVG and the pretty-printed SVG
            svg_creator.save_svg(self._graph_config.final_svg)
            svg_creator.save_pretty_svg(self._graph_config.final_pretty_svg)

            print("\nAll paths:")
            print(len(all_paths))

            # ------------------------------------------------
            print('--------------------------------------------------------------------')
            # Create a Json object all the details
            json = SVGUtils.create_json(nodes, all_paths, arrow_heads, clusters,
                                        svg_attributes,
                                        self._graph_config.output_json)
            pass
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            error = f"An unexpected error occurred: {e}"

        return error
