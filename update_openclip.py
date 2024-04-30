#!.venv/bin/python

import os
import re
import yaml
import xml.etree.ElementTree as ET
import xml.dom.minidom
import datetime
import argparse


def get_creation_date(file_path):
    creation_timestamp = os.path.getctime(file_path)
    creation_datetime = datetime.datetime.fromtimestamp(creation_timestamp)
    formatted_creation_date = creation_datetime.strftime('%Y/%m/%d %H:%M:%S')

    return formatted_creation_date


# Gets XML structure for new versions
def element_from_template(template):
    element = ET.Element(template['tag'])
    for attr, value in template.get('attributes', {}).items():
        element.set(attr, value)
    for child_info in template.get('children', []):
        child = ET.SubElement(element, child_info['tag'])
        if 'text' in child_info:
            child.text = child_info['text']
        for attr, value in child_info.get('attributes', {}).items():
            child.set(attr, value)
        create_nested_elements(child_info.get('children', []), child)

    return element


# Recursive read of nested elements in temple (like spans)
def create_nested_elements(children_info, parent_element):
    for child_info in children_info:
        child = ET.SubElement(parent_element, child_info['tag'])
        if 'text' in child_info:
            child.text = child_info['text']
        for attr, value in child_info.get('attributes', {}).items():
            child.set(attr, value)
        create_nested_elements(child_info.get('children', []), child)


# Builds image sequence string from path to image
def find_file_sequence(directory):
    # Get list of files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    img_seq_pattern = r'(\w+.v\d+.\d+.\w+)'
    files = [filename for filename in files if re.match(img_seq_pattern, filename)]
    # Find the range of numbers
    image_name = [f.split('.')[-3] for f in files]
    frames = [int(f.split('.')[-2].split('.')[-1]) for f in files]
    extension = [f.split('.')[-1] for f in files]

    start_frame = min(frames)
    end_frame = max(frames)

    # Construct the output string
    prefix = os.path.commonprefix(image_name)
    suffix = os.path.commonprefix([s[::-1] for s in extension])[::-1]

    sequence = f"{prefix}.[{start_frame}-{end_frame}].{suffix}"
    sequence_string = os.path.join(directory, sequence)

    return sequence_string


# Loads Openclip and appends relevant elements
def update_openclip(
        openclip,
        render_path,
        feed_preset="default",
        version_preset="nuke_version",
        dryrun=False
        ):

    render_date = get_creation_date(render_path)
    # Get Version from image filename
    types_seq = ['EXR', 'exr', 'JPG', 'jpg', 'JPEG', 'jpeg', 'PNG', 'png']
    # types_movies = ['MOV', 'mov', 'MP4', 'mp4']
    version_pattern = r'(\w+.(v\d+))'
    filename, extension = os.path.splitext(os.path.basename(render_path))
    input_extension = extension[1:]
    if input_extension in types_seq:
        render_dir = os.path.dirname(render_path)
        render_path = find_file_sequence(render_dir)
    name_version_match = re.search(version_pattern, os.path.basename(render_path))
    render_name = name_version_match.group(1)
    render_version = name_version_match.group(2)
    render_version_int = str(int(re.sub("v", "", render_version)))

    ########################################
    # Starts openclip work
    tree = ET.parse(openclip)
    root = tree.getroot()

    versions = root.find('.//versions')

    # Checks if version is already in openclip and exists if is true
    for version in versions:
        if render_version == version.get('uid'):
            print("|||||||||||||||||||||||||||||||||")
            print(f"Version {render_version} already in OpenClip ")
            print("|||||||||||||||||||||||||||||||||")
            return

    # Continue if version is new
    openclip_presets_file = os.path.join(os.path.dirname(__file__), 'openclip_templates.yaml')
    with open(openclip_presets_file, 'r') as file:
        op_template = yaml.safe_load(file)

    # Creates a new feed entry with structure from template file
    new_render_element = element_from_template(op_template[feed_preset])

    # Read first feed
    feeds = root.find('.//feeds')
    existing_feed = feeds.find('./feed')
    rate = existing_feed.find('.//rate')
    nbticks = existing_feed.find('.//nbTicks')

    # Set rate and timing
    new_render_element.find('.//rate').text = rate.text
    new_render_element.find('.//nbTicks').text = nbticks.text

    # Set UID and path
    new_render_element.set('uid', render_name)
    new_render_element.find('.//path').text = render_path
    new_render_element.set('uid', render_name)
    new_render_element.set('vuid', render_version)

    # Versions
    feeds.set('currentVersion', render_version)
    versions.set('currentVersion', render_version)

    # Creates a new version entry with structure from template file
    new_version_element = element_from_template(op_template[version_preset])

    # Modify version values
    new_version_element.set('uid', render_version)
    new_version_element.find('./name').text = render_version
    new_version_element.find('./creationDate').text = render_date
    new_version_element.find('.//versionNumber').text = render_version_int

    # Updates feed and version
    feeds.append(new_render_element)
    versions.append(new_version_element)

    # Write out new openclip
    xml_string = ET.tostring(root, encoding='utf-8').decode()
    xml_string = xml.dom.minidom.parseString(xml_string).toprettyxml(indent="\t")
    xml_string = '\n'.join(line for line in xml_string .split('\n') if line.strip())

    if not dryrun:
        with open(openclip, 'w') as file:
            file.write(xml_string)

    print("|||||||||||||||||||||||||||||||||")
    print(f"Updated openclip file: {openclip}")
    print(f"Appended version: {render_version}")
    print(f"Image sequence: {render_path}")
    print("|||||||||||||||||||||||||||||||||")


def main():
    parser = argparse.ArgumentParser(description='Utility to update version on a Openclip file')
    parser.add_argument('-f', '--file',
                        action="store",
                        dest="file",
                        default='',
                        help='Openclip file')

    parser.add_argument('-i', '--input',
                        action="store",
                        dest="input",
                        default='',
                        help='Image sequence or movie clip')

    parser.add_argument('-p', '--feed_preset',
                        action="store",
                        dest="feed_preset",
                        default='default',
                        help='Openclip feed preset from YAML presets file')

    parser.add_argument('-m', '--version_preset',
                        action="store",
                        dest="version_preset",
                        default='nuke_version',
                        help='Openclip version preset from YAML presets file')

    parser.add_argument('-n', '--dry_run',
                        action="store_true",
                        dest="dry_run",
                        help='Print results but dont do anything')

    # Currently the appender version is forsed as the CURRENT for the opnclip
    # Wondering if I should add a flag do this as an option

    args = parser.parse_args()

    if args.file and args.input:
        openclip_file = args.file
        render_path = args.input
        dryrun = args.dry_run
        feed_preset = args.feed_preset
        version_preset = args.version_preset

        update_openclip(openclip_file, render_path, feed_preset, version_preset, dryrun)
    else:
        print("Please provide -f and -c arguments")


if __name__ == "__main__":
    main()
