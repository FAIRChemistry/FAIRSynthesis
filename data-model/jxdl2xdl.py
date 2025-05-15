import os

from utils import load_json, save_string_as_file
from generated.jxdl_data_structure import JXDLSchema
from lxml import etree

def convert_jxdl_to_xdl_string(jxdl: JXDLSchema) -> str:
    """
    Convert JXDLSchema to XDL format, which is in XML.
    """
    # Convert the JXDLSchema to a dictionary
    xdl_dict = jxdl.to_dict()

    # Convert the dictionary to XML
    xdl_xml = dict_to_xml("XDL", xdl_dict)

    return xdl_xml



def dict_to_xml(root_tag, data):
    """Convert a dict to XML with support for $xml_type, @attr, _attr, text/cdata/comments."""

    def build_element(parent, key, value):
        tag = value.get('$xml_type') if isinstance(value, dict) and '$xml_type' in value else key

        if isinstance(value, dict):
            # Collect attributes from both @ and _ keys
            attribs = {
                k.lstrip('@_'): v for k, v in value.items()
                if k.startswith('@') or k.startswith('_')
            }

            text = value.get('#text')
            cdata = value.get('#cdata')
            comment = value.get('#comment')

            print(f"Building element: {tag}, attribs: {attribs}, text: {text}, cdata: {cdata}, comment: {comment}")
            elem = etree.SubElement(parent, tag, attrib=attribs)

            if comment:
                elem.append(etree.Comment(comment))
            if cdata:
                elem.text = etree.CDATA(cdata)
            elif text:
                elem.text = text.strip() if isinstance(text, str) else str(text)

            for subkey, subval in value.items():
                if subkey in {'$xml_type', '#text', '#cdata', '#comment'}:
                    continue
                if subkey.startswith('@') or subkey.startswith('_'):
                    continue
                if isinstance(subval, list):
                    for item in subval:
                        build_element(elem, subkey, item)
                else:
                    build_element(elem, subkey, subval)

        elif isinstance(value, list):
            for item in value:
                build_element(parent, key, item)

        else:
            elem = etree.SubElement(parent, tag)
            elem.text = str(value)

    root = etree.Element(root_tag)
    for key, val in data.items():
        build_element(root, key, val)
    return etree.tostring(root, pretty_print=True, encoding="unicode")

if __name__ == '__main__':
    jdx_file_path = os.path.join('..', 'data', 'generated', 'jxdl.json')
    xml = convert_jxdl_to_xdl_string(JXDLSchema.from_dict(load_json(jdx_file_path)))
    print("XML Result: " + xml)
    save_string_as_file(xml, os.path.join('..', 'data', 'generated', 'xdl.xml'))



