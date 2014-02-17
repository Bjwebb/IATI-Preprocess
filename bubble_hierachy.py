import os
from lxml import etree
import hashlib

"""
The purpose of this code is to "bubble" all fields down to the deepest hierarchy.

E.g.

    <iati-activity hierarchy="1">
        <reporting-org ref="PUB">
        <iati-identifier>PUB-1</iati-identifier>
        <sector code="13040"/>
    </iati-activity>
    <iati-activity hierarchy="2">
        <iati-identifier>PUB-2</iati-identifier>
        <related-activity type="1" ref="PUB-1" />
    </iati-activity>

becomes:

    <iati-activity hierarchy="1">
        <reporting-org ref="PUB">
        <iati-identifier>PUB-1</iati-identifier>
        <sector code="13040"/>
    </iati-activity>
    <iati-activity hierarchy="2">
        <iati-identifier>PUB-2</iati-identifier>
        <related-activity type="1" ref="PUB-1" />
        <sector code="13040"/>
    </iati-activity>

This code was created by Ben Webb, and is released under CC0
http://creativecommons.org/publicdomain/zero/1.0/

"""

activity_dict = {}

hash = lambda x: hashlib.sha1(x.encode('utf-8')).hexdigest()

try:
    os.makedirs(os.path.join('out','activities'))
except FileExistsError:
    pass

for root, dirs, files in os.walk('./data-annualreport'):
    for fname in files:
        try:
            tree = etree.parse(os.path.join(root,fname))
        except etree.XMLSyntaxError:
            continue
        for activity in tree.getroot().findall('iati-activity'):
            try:
                identifier = activity.find('iati-identifier').text 
                with open(os.path.join('out','activities',hash(identifier)), 'wb') as fp:
                    fp.write(etree.tostring(activity))
            except AttributeError:
                pass

for root, dirs, files in os.walk('./data-annualreport'):
    try:
        os.makedirs(os.path.join('out',root))
    except FileExistsError:
        pass
    for fname in files:
        try:
            tree = etree.parse(os.path.join(root,fname))
        except etree.XMLSyntaxError:
            continue
        for activity in tree.getroot().findall('iati-activity'):
            parents = activity.xpath('related-activity[@type=1]')
            if parents:
                try:
                    parent = etree.parse(os.path.join('out', 'activities', hash(parents[0].attrib.get('ref')))).getroot()
                except OSError:
                    continue
                activity_elements = set(x.tag for x in activity)
                parent_elements = set(x.tag for x in parent)
                diff = parent_elements.difference(activity_elements)
                for tagname in diff:
                    for element in parent.findall(tagname):
                        activity.append(element)
        tree.write(os.path.join('out',root,fname))
