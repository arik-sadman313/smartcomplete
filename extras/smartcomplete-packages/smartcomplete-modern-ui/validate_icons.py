#!/usr/bin/env python3
"""Check icon structure, unsafe references, and exact raster export sizes."""
from pathlib import Path
import struct
import xml.etree.ElementTree as ET

base = Path(__file__).resolve().parent / 'icons/hicolor'
svg = base / 'scalable/apps/linuxcomplete.svg'
root = ET.parse(svg).getroot()
assert root.attrib['viewBox'] == '0 0 32 32'
assert root.attrib['width'] == root.attrib['height'] == '32'
assert root.find('{http://www.w3.org/2000/svg}title').text == 'SmartComplete'
for element in root.iter():
    assert element.tag.rsplit('}', 1)[-1] not in ('script', 'foreignObject', 'image', 'use')
    assert not any('href' in key or key.startswith('on') for key in element.attrib)
for size in (16, 22, 24, 32, 48, 64):
    image = base / f'{size}x{size}/apps/linuxcomplete.png'
    data = image.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', image
    assert struct.unpack('>II', data[16:24]) == (size, size), image
print('Tray icon: safe SVG and 6 correctly sized PNG exports verified.')
