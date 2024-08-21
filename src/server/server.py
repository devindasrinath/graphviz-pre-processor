from flask import Flask, jsonify, request
from flask_cors import CORS


class FlaskServer:
    def __init__(self, output_svg_path, output_json_path, svg_processor):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for all routes
        self._configure_routes()
        self._svg_path = output_svg_path
        self._output_json_path = output_json_path
        self._svg_processor = svg_processor

    def _configure_routes(self):
        # Define a route to accept and process DOT content from the request body
        @self.app.route('/input/dot', methods=['POST'])
        def process_dot():
            # Get the DOT content from the request body
            dot_content = request.data.decode('utf-8')

            if not dot_content:
                return jsonify(error="No DOT content provided"), 400

            error = self._svg_processor.process(dot_content)
            return jsonify(success=error)

        # Define a route to serve an SVG file
        @self.app.route('/output/svg', methods=['GET'])
        def serve_svg():
            try:
                with open(self._svg_path, 'r') as file:
                    svg_content = file.read()
                return jsonify(svg_content=svg_content)
            except FileNotFoundError:
                return jsonify(error="SVG file not found"), 404

        # Define a route to serve a JSON file
        @self.app.route('/output/json', methods=['GET'])
        def serve_json():
            try:
                with open(self._output_json_path, 'r') as file:
                    json_content = file.read()
                return json_content
            except FileNotFoundError:
                return jsonify(error="SVG file not found"), 404

    def run(self, host='0.0.0.0', port=5500, debug=False):
        self.app.run(host=host, port=port, debug=debug)
