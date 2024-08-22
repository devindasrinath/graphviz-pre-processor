import xml.etree.ElementTree as et
import xml.dom.minidom


class SVGCreator:
    def __init__(self, svg_attributes):
        self.width = svg_attributes['width']
        self.height = svg_attributes['height']
        self.viewBox = svg_attributes['viewBox']
        self.transform = svg_attributes['transform']
        self.polygon_points = svg_attributes['polygon_points']
        self.svg = et.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'width': f'{self.width}',
            'height': f'{self.height}',
            'viewBox': self.viewBox
        })
        self.graph = et.SubElement(self.svg, 'g', {
            'id': 'graph0',
            'class': 'graph',
            'transform': str(self.transform)
        })
        title = et.SubElement(self.graph, 'title')
        title.text = 'G'
        et.SubElement(self.graph, 'polygon', {
            'fill': 'white',
            'stroke': 'none',
            'points': str(self.polygon_points)
        })

    def add_node(self, node_id, info):
        node = et.SubElement(self.graph, 'g', {'id': f'{node_id}', 'class': 'node'})
        et.SubElement(node, 'polygon', {
            'fill': 'none',
            'stroke': 'none',
            'points': info['points']
        })
        et.SubElement(node, 'image', {
            'xlink:href': str(info['xlink']),
            'width': str(info['lengths'][0]),
            'height': str(info['lengths'][1]),
            'preserveAspectRatio': "xMinYMin meet",
            'x': str(info['coordinate'][0]),
            'y': str(info['coordinate'][1])
        })

    def add_cluster(self, cluster_title, info):
        cluster = et.SubElement(self.graph, 'g', {'id': f'{cluster_title}', 'class': 'cluster'})
        et.SubElement(cluster, 'polygon', {
            'fill': 'none',
            'stroke': 'black',
            'points': info['points']
        })

    def add_arrow(self, arrow_id, points):
        node = et.SubElement(self.graph, 'g', {'id': f'arrow{arrow_id}', 'class': 'arrow'})
        et.SubElement(node, 'polygon', {
            'fill': 'black',
            'stroke': 'black',
            'points': points
        })

    def add_edge(self, edge_id, path_data):
        edge = et.SubElement(self.graph, 'g', {'id': f'edge{edge_id}', 'class': 'edge'})
        et.SubElement(edge, 'path', {
            'fill': 'none',
            'stroke': 'black',
            'd': path_data[2:]
        })
        et.SubElement(edge, 'polygon', {
            'fill': 'black',
            'stroke': 'black'
        })

    def get_svg(self):
        return self.svg

    def save_svg(self, output_file):
        tree = et.ElementTree(self.svg)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"SVG created and saved to {output_file}")

    def save_pretty_svg(self, output_file):
        dom = xml.dom.minidom.parseString(et.tostring(self.svg))
        pretty_svg = dom.toprettyxml()
        with open(output_file, "w") as f:
            f.write(pretty_svg)
        print(f"Pretty SVG created and saved to {output_file}")
