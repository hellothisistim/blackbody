# -*- coding: utf-8 -*-
#from pprint import pprint

# blackbody.py
#
# Tim BOWMAN [puffy@netherlogic.com]

"""
Mapping hotness to color values.

Build ColorLookups in Nuke that map degrees Kelvin to useable color values.

Data sourced from this excellent datafile:
http://www.vendian.org/mncharity/dir3/blackbody/
"""

import nuke


def load_data():

    data_file = 'bbr_color.txt'

    fields = ('kelvin', 'kelvin_abbr', 'cmf', 'chromaticity_x', 
        'chromaticity_y', 'power', 'log_r', 'log_g', 'log_b', 'r', 
        'g', 'b', 'hex')

    data = []

    count = 0
    for line in open(data_file).readlines():
        #print count, line
        count += 1
        #if count % 10 == 1:
        #    print "Reading line", count
        if line.startswith('#'):
            # it's a comment
            pass
        else:
            one_entry = {}
            chunks = line.split()
            #print "there are", len(chunks), "chunks"
            for index, field in enumerate(fields):
                #print index, field, chunks[index]
                one_entry[field] = chunks[index]
            data.append(one_entry)
            #pprint(one_entry)

    return data
        

def filter_yxy(data, cmf='2deg'):
    """Take data dictionary and return tuples of floats for Kelvin, power,
    X chromaticity and Y chromaticity. Use only the requested color matching
    function.

    Note: The stunningly high power values are unruly in Nuke.

    data: list of dicts from load_data method
    cmf: color matching function. either '2deg' (default) or '10deg'
    """

    assert type(data) == list
    assert type(cmf) == str
    assert cmf in ['2deg', '10deg']
    
    kxy = []
    for data_point in data:
        if data_point['cmf'] == cmf:
            kxy.append((float(data_point['kelvin']),
                        float(data_point['power']), 
                        float(data_point['chromaticity_x']),
                        float(data_point['chromaticity_y'])))
    return kxy
    
def filter_logrgb(data):
    """Accept dictionary of data and return tuples of floats for Kelvin, log
    red, log green, and log blue.

    data: list of dicts from load_data method
    """

    assert type(data) == list

    logrgb = []
    for data_point in data:
        logrgb.append((float(data_point['kelvin']),
                       float(data_point['log_r']),
                       float(data_point['log_g']),
                       float(data_point['log_b'])))
    return logrgb


def filter_srgb(data):
    """Accept dictionary of data and return tuples of floats for Kelvin, sRGB
    red, sRGB green, and sRGB blue.

    data: list of dicts from load_data method
    """

    assert type(data) == list

    logrgb = []
    for data_point in data:
        logrgb.append((float(data_point['kelvin']),
                       float(data_point['r']) / 255.0,
                       float(data_point['g']) / 255.0,
                       float(data_point['b']) / 255.0))
    return logrgb


def build_lookup(filtered_data):
    """Accept filtered data (list of tuples) from one of the filter methods
    and create a ColorLookup Node in Nuke using the filtered data  Kelvin input
    mapped to whatever the filter provides."""
    
    lookup = nuke.createNode('ColorLookup')
    # Keys at 0 and 1 in red, green, and blue are problematic. Get rid of them.
    for channel in range(1,4):
        lookup.knob('lut').clearAnimated(channel)
    lookup.knob('source').setSingleValue(True)
    for point in filtered_data:
        #print point
        source, dest_r, dest_g, dest_b = point
        lookup.knob('source').setValue(source, 0)
        lookup.knob('target').setValue(dest_r, 0)
        lookup.knob('target').setValue(dest_g, 1)
        lookup.knob('target').setValue(dest_b, 2)
        lookup.knob('setRGB').execute()
    return lookup


def yxy_lookup():
    """Build a ColorLookup using the chromaticity and power data."""

    note_message = """
    Blackbody color lookup with input in degrees Kelvin (data ranges from 1000
    to 40000 degrees) mapped to chromaticity data (Y is power in semi-arbitrary
    units, x and y are chromaticity coordinates.

    Note: This lookup requires a bit of massaging pre- and post-lookup. Your
    input heat map (which is probably in the 0-1 range) will need to be
    remapped to your desired heat level in Kelvin. The lookup outputs in the
    CIE-Yxy colorspace and will need to be converted back to your working
    colorspace. It is also likely to be massively overexposed (50 stops or so --
    yikes!)
    
    Data sourced from this excellent datafile:
    http://www.vendian.org/mncharity/dir3/blackbody/
    """

    data = load_data()
    yxy = build_lookup(filter_yxy(data))
    yxy.setName('Blackbody_Yxy_Lookup')
    a = nuke.Text_Knob('note', 'Note')
    yxy.addKnob(a)
    yxy.knob('note').setValue(note_message)

    return yxy


def srgb_lookup():
    """Build a ColorLookup using the srgb data."""

    note_message = """
    Blackbody color lookup with input in degrees Kelvin (data ranges from 1000
    to 40000 degrees) mapped to sRGB color values.

    Note: This lookup requires a bit of massaging pre- and post-lookup. Your
    input heat map (which is probably in the 0-1 range) will need to be
    remapped to your desired heat level in Kelvin. The lookup outputs in 
    sRGB colorspace and will need to be converted back to your working
    colorspace. 
    
    Data sourced from this excellent datafile:
    http://www.vendian.org/mncharity/dir3/blackbody/
    """

    data = load_data()
    srgb = build_lookup(filter_srgb(data))
    srgb.setName('Blackbody_sRGB_Lookup')
    a = nuke.Text_Knob('note', 'Note')
    srgb.addKnob(a)
    srgb.knob('note').setValue(note_message)

    return srgb

def logrgb_lookup():
    """Build a ColorLookup using the logrgb data."""

    note_message = """
    Blackbody color lookup with input in degrees Kelvin (data ranges from 1000
    to 40000 degrees) mapped to logrithmic RGB color values.

    Note: This lookup requires a bit of massaging pre- and post-lookup. Your
    input heat map (which is probably in the 0-1 range) will need to be
    remapped to your desired heat level in Kelvin. The lookup outputs in some
    weird logrithmic RGB colorspace, so you may need to do some massaging to
    make things look right.
    
    Data sourced from this excellent datafile:
    http://www.vendian.org/mncharity/dir3/blackbody/
    """

    data = load_data()
    logrgb = build_lookup(filter_logrgb(data))
    logrgb.setName('Blackbody_logRGB_Lookup')
    a = nuke.Text_Knob('note', 'Note')
    logrgb.addKnob(a)
    logrgb.knob('note').setValue(note_message)

    return logrgb

def addMenu(dest = nuke.menu('Nodes')):
    """
    Add a "Blackbody" menu to the desired destination (default: Nodes) menu
    which allows access to the lookups in the Nuke GUI.
    
    """

    bb_menu = dest.addMenu('Blackbody')
    bb_menu.addCommand('Yxy Lookup', "blackbody.yxy_lookup()")
    bb_menu.addCommand('sRGB Lookup', "blackbody.srgb_lookup()")
    bb_menu.addCommand('log RGB Lookup', "blackbody.logrgb_lookup()")
    
