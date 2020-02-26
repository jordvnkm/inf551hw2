import re
import sys
from lxml import etree
from io import StringIO, BytesIO

def printf(elem):
    for child in elem:
        if isinstance(child, str):
            print(child)
        else:
            print(etree.tostring(child))


# find which inumbers are valid by "AND"ing together inumber lists for keywords
# create map from inumber to parent inumber
# create postings map (similar to invert.py)
# create filepaths by recursivly going up tree.

# prints a filepath by going up the tree
# inumber is inumber to start at.
# directory to parent is dictionary inumber -> parent inumber
# tree is xml tree object
def get_path(inumber, directory_to_parent, tree):
    if inumber == None or not (inumber in directory_to_parent):
        return ""

    path = '//INodeSection/inode[id="' + inumber + '"]'
    filename = ""
    for entry in tree.xpath(path):
        for child in entry:
            if child.tag == "name":
                filename = child.text 
    prefix_path = get_path(directory_to_parent[inumber], directory_to_parent, tree)
    return prefix_path + "/" + filename


# gets a dictionary for metadata associated with the inumber
def get_metadata(inumber, tree):
    metadata = {}
    path = '//INodeSection/inode[id="' + inumber + '"]'
    for entry in tree.xpath(path):
        for child in entry:
            if child.tag == "id":
                metadata["id"] = child.text
            elif child.tag == "type":
                metadata["type"] = child.text
            elif child.tag == "mtime":
                metadata["mtime"] = child.text
            elif child.tag == "blocks":
                blocks = []
                for child_block in child:
                    for block in child_block:
                        if block.tag == "id":
                            blocks.append(block.text)
                metadata["blocks"] = blocks
    return metadata
    

# prints the valid paths by starting at valid inumbers and going up the directory heirarchy.
# parses the xml_file to get the metadata associated with the file
def print_valid_paths(valid_inumbers, directory_to_parent, xml_file):
    tree = etree.parse(xml_file)
    for valid_inumber in valid_inumbers:
        path = get_path(valid_inumber, directory_to_parent, tree)
        print(path + "\n")
        metadata = get_metadata(valid_inumber, tree)
        print(str(metadata) + "\n")



# Gets valid inumbers from the index file by "AND"ing together inumber lists for every keyword.
# Note that the keywords must be lowercase
def get_valid_inumbers(index_file, query):
    tree = etree.parse(index_file)
    valid_numbers = set()
    tokens = re.split(r'[-\s]\s*', query)
    
    token_num = 0
    for token in tokens:
        path = '//postings[name="' + token + '"]'
        token_inumbers = set()
        for entry in tree.xpath(path):
            for child in entry:
                if child.tag == "inumber":
                    token_inumbers.add(child.text)
        if token_num == 0:
            valid_numbers = valid_numbers.union(token_inumbers)
        else:
            valid_numbers = valid_numbers.intersection(token_inumbers)
        token_num += 1
    valid_numbers = list(valid_numbers)
    valid_numbers.sort()
    return valid_numbers


# creates and returns a dictionary from the xml file using the inodedirectorysection
# dictionary is directory inumber -> parent inumber
def create_directory_heirarchy(xml_file):
    tree = etree.parse(xml_file)
    directory_to_parent = {}

    for entry in tree.xpath("//INodeDirectorySection/directory"):
        parent = None
        children = []
        for directory in entry:
            if str(directory.tag) == "parent":
                parent = directory.text
            elif str(directory.tag) == "child":
                children.append(directory.text)
            
        if parent is not None:
            for child in children:
                directory_to_parent[child] = parent 
    return directory_to_parent


def search_xml(args):
    if len(args) != 4:
        print("invalid execution")
        return
    xml_file = args[1]
    index_file = args[2]
    query = args[3]

    directory_to_parent = create_directory_heirarchy(xml_file)
    valid_inumbers = get_valid_inumbers(index_file, query)
    print_valid_paths(valid_inumbers, directory_to_parent, xml_file)

if __name__ == "__main__":
    search_xml(sys.argv)
