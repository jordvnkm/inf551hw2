import sys
import re
import os
from lxml import etree
from io import StringIO, BytesIO


# postings dict is dict inode name (already split by space and hyphen) -> inode id
# names is list of names to associate with inode_id
# inode_id is inode to associate with names
def add_names_to_postings_dict(postings_dict, names, inode_id):
    for name in names:
        name = name.lower()
        if not (name in postings_dict):
            postings_dict[name] = set()
        postings_dict[name].add(inode_id)


def parseINodeSection(inode_section, postings_dict):
    for inode in inode_section.findall("inode"):
        if inode.find("name").text:
            name = inode.find("name").text
            name = os.path.splitext(name)[0]
            names = re.split(r'[-\s]\s*', name)
            inode_id = inode.find("id").text
            add_names_to_postings_dict(postings_dict, names, inode_id) 
            #postings_dict[inode.find("name").text] = inode.find("id").text
    

def write_postings(postings_dict, output_file):
    root_el = etree.Element("index")
    for name in postings_dict:
        postings_el = etree.Element("postings")

        inumber_list = postings_dict[name]
        name_el = etree.Element("name")
        name_el.text = name
        postings_el.append(name_el)

        for inumber in inumber_list:
            inumber_el = etree.Element("inumber")
            inumber_el.text = inumber
            postings_el.append(inumber_el)

        root_el.append(postings_el)

    output_file = open(output_file, "wb")
    output_string = etree.tostring(root_el, pretty_print=True)
    output_file.write(output_string)
    output_file.close()




def create_index(args):
    if len(args) != 3:
        print("invalid execution")
        return
    #input_file = open(args[1], 'r') 
    input_file = args[1]
    output_file = args[2]

    parser = etree.XMLParser()
    tree = etree.parse(input_file, parser)
    postings_dict = {}
    for child in tree.getroot():
        if child.tag == "INodeSection":
            parseINodeSection(child, postings_dict) 

    write_postings(postings_dict, output_file)



if __name__ == "__main__":
    create_index(sys.argv)
