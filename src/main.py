from src.config.graph_config import GraphConfig
from src.server.server import FlaskServer
from utils.svg_extractor import SVGExtractor
from processor.svg_processor import SVGProcessor
from utils.svg_creator import SVGCreator
from utils.svg_utils import SVGUtils

# Parameters
dot_file = './input/graph.dot'
svg_file = 'output/graph'
output_svg = 'output/resized_graph.svg'
final_svg = 'output/final_output.svg'
final_pretty_svg = 'output/final_output_pretty.svg'
output_json = 'output/json_output.json'
width = 2465.00
height = 549.00
viewBox = '0.00 0.00 2465.00 549.00'
translate = (4, 545)


# Create an instance of GraphConfig
graph_config = GraphConfig(
    dot_file=dot_file,
    svg_file=svg_file,
    output_svg=output_svg,
    final_svg=final_svg,
    final_pretty_svg=final_pretty_svg,
    output_json=output_json,
    width=width,
    height=height,
    viewBox=viewBox,
    translate=translate
)

svg_processor = SVGProcessor(graph_config)

svg_processor.process()

server = FlaskServer(final_pretty_svg, output_json, svg_processor)
server.run()
