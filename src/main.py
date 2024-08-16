import sys
import os

# Add the src directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.graph_config import GraphConfig
from src.server.server import FlaskServer
from processor.svg_processor import SVGProcessor

# Parameters
dot_file = './input/graph.dot'
svg_file = 'output/graph.svg'
output_svg = 'output/resized_graph.svg'
final_svg = 'output/final_output.svg'
final_pretty_svg = 'output/final_output_pretty.svg'
output_json = 'output/json_output.json'


# Create an instance of GraphConfig
graph_config = GraphConfig(
    dot_file=dot_file,
    svg_file=svg_file,
    output_svg=output_svg,
    final_svg=final_svg,
    final_pretty_svg=final_pretty_svg,
    output_json=output_json)

svg_processor = SVGProcessor(graph_config)

svg_processor.process()

server = FlaskServer(final_pretty_svg, output_json, svg_processor)
server.run()
