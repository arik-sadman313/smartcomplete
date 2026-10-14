#!/usr/bin/env python3
"""Validate bundled theme assets and text contrast without changing Fcitx5."""
import configparser
from pathlib import Path
import struct
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent


def luminance(color):
    rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return sum(v * w for v, w in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(a, b):
    x, y = sorted((luminance(a), luminance(b)))
    return (y + 0.05) / (x + 0.05)


for mode, background, selection in [
    ('light', '#FAFAFC', '#185ABD'), ('dark', '#242830', '#9CC8FF')
]:
    directory = ROOT / 'themes' / ('smartcomplete-modern-' + mode)
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str
    with (directory / 'theme.conf').open() as source:
        config.read_file(source)
    for section in config.sections():
        if 'Image' not in config[section]:
            continue
        image = directory / config[section]['Image']
        assert image.parent == directory and image.is_file(), image
        png = image.read_bytes()
        assert png[:8] == b'\x89PNG\r\n\x1a\n', image
        width, height = struct.unpack('>II', png[16:24])
        margin = section + '/Margin'
        if margin in config:
            m = config[margin]
            assert int(m['Left']) + int(m['Right']) < width, image
            assert int(m['Top']) + int(m['Bottom']) < height, image
        ET.parse(image.with_suffix('.svg'))
    normal = contrast(config['InputPanel']['NormalColor'], background)
    selected = contrast(config['InputPanel']['HighlightCandidateColor'], selection)
    assert normal >= 4.5 and selected >= 4.5, (mode, normal, selected)
    print(f'{mode}: image references/margins valid; contrast normal={normal:.2f}, selected={selected:.2f}')
