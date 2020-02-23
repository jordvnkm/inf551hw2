import re
import sys
from lxml import etree
from io import StringIO, BytesIO

# find which inumbers are valid by "AND"ing together inumber lists for keywords
# create map from inumber to parent inumber
# create postings map (similar to invert.py)
# create filepaths by recursivly going up tree.
