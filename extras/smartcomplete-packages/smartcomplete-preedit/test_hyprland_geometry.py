#!/usr/bin/env python3
"""Test the real popup Y-placement block, not a running compositor.
Usage: python3 test_hyprland_geometry.py /path/to/Hyprland/src/managers/input/InputMethodPopup.cpp
Requires a C++ compiler. Temporary compilation stays under .temp_files and is removed.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

source = Path(sys.argv[1]).read_text()
start = source.index('Vector2D   popupOffset(0, 0);') + len('Vector2D   popupOffset(0, 0);')
end = source.index('double popupOverflow', start)
block = source[start:end]
wrapper = r'''
#include <iostream>
#include <cmath>
struct V { double y; };
struct B { double y, height; };
struct M { V m_position, m_size; };
double place(double mt, double mh, double py, double cy, double ch, double ph) {
    M monitor{{mt}, {mh}};
    auto* pMonitor = &monitor;
    B parentBox{py, 0}, cursorBoxParent{cy, ch};
    V currentPopupSize{ph}, popupOffset{0};
''' + block + r'''
    return py + cy + popupOffset.y;
}
int main() {
    // monitor top/height, parent/caret Y, caret/popup height, expected popup Y.
    const double cases[][7] = {
        {0,600,0,200,20,60,140},
        {0,600,0,580,20,60,520},
        {0,600,0,10,20,60,30},
        {0,600,0,60,20,60,0},
        {-1080,1080,-1080,280,20,60,-860},
        {0,600,100,50,20,60,90},
        {0,300,0,140,20,500,0},
        {0,300,0,140,20,180,0},
        {0,600,0,100.5,18.5,32.25,68.25}
    };
    int failures = 0;
    for (const auto& c : cases) {
        const double got = place(c[0],c[1],c[2],c[3],c[4],c[5]);
        if (std::abs(got-c[6]) > 0.00001) {
            std::cerr << "Expected " << c[6] << ", got " << got << '\n';
            ++failures;
        }
    }
    std::cout << "9 geometry cases, " << failures << " failures\n";
    return failures ? 1 : 0;
}
'''
root = Path.cwd() / '.temp_files'
root.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='popup-geometry-', dir=root) as tmp:
    cpp, binary = Path(tmp) / 'test.cpp', Path(tmp) / 'test'
    cpp.write_text(wrapper)
    subprocess.run(['c++', '-std=c++17', str(cpp), '-o', str(binary)], check=True, timeout=30)
    result = subprocess.run([str(binary)], timeout=5, check=False)
    sys.exit(result.returncode)
