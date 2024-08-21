class GraphConfig:
    def __init__(self, dot_file,input_folder, svg_file, output_svg, final_svg, final_pretty_svg, output_json):
        self.dot_file = dot_file
        self.svg_file = svg_file
        self.output_svg = output_svg
        self.final_svg = final_svg
        self.final_pretty_svg = final_pretty_svg
        self.output_json = output_json
        self.input_folder = input_folder

    def __repr__(self):
        return (f"GraphConfig(dot_file={self.dot_file}, input_folder={self.input_folder}, svg_file={self.svg_file}, "
                f"output_svg={self.output_svg}, final_svg={self.final_svg}, "
                f"final_pretty_svg={self.final_pretty_svg}, output_json={self.output_json}")
