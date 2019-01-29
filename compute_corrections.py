import json
from pathlib import Path
import vibcor
import pandas as pd
import numpy as np
import unicodedata

def load_rotations(mol_name):
    "returns the dictionary that our collect_rotations script wrote to disk"
    with Path("{}_rotations.json".format(mol_name)).open('r') as f:
        rots = json.load(f)
    return rots

def compute_alpha_ii(eq_val, mode_vals, dxs):
    "returns a vector with each element being the second derivative of rotation withrespect to a mode"
    ret = []
    for dx, (a_p, a_m) in zip(dxs, mode_vals):
        val = (a_p -(2*eq_val)+ a_m)/dx**2
        ret.append(val)
    return ret

def extract_modes(rots, wavelength):
    "returns a list of tuples where each element is (rotation[mode][+][wavelength], rotation[mode][-][wavelength]"
    modes = sorted([k for k in rots if k != 'eq'])
    ret = []
    for i in modes:
        print(i)
        mode_vals = (rots[i]['+'][wavelength], rots[i]['-'][wavelength])
        print(mode_vals)
        ret.append(mode_vals)
    return ret

def compute_correction(alpha_ii, dxs):
    "computes the seccond term in the second to last equation on pg 1892 of wiberg"
    dx2 = dxs**2
    return np.sum(alpha_ii * dx2)



# need the hessian, geom, masses!
def get_hessian_geom_mass(mol_name):
    hess_fchk_file = Path() / mol_name / 'hessian.fchk'
    hess = vibcor.fchk.parse_hessian(hess_fchk_file.read_text())
    geom = vibcor.fchk.parse_fchk_array(hess_fchk_file.read_text(), 'Current cartesian coordinates').reshape(-1, 3)
    masses = vibcor.fchk.parse_fchk_array(hess_fchk_file.read_text(), 'Real atomic weights')
    return hess, geom, masses

def compute_displacement_sizes(omegas, temp):
    return vibcor.findif.wiberg_displacement_sizes(omegas, temp)

def print_centered(text, line_width):
    print("{text:<{lw}}".format(text=text, lw=line_width))

def print_box_title(title, line_width, marker="*"):
    lw = line_width - line_width %3
    tw = (lw // 3) - 2
    line = marker*tw
    def text_centered(text):
        return "{marker}{marker}{text:^{tw}}{marker}{marker}".format(marker=marker, tw=tw, text=text)
    def line_centered(text):
        return "{text:^{lw}}".format(text=text_centered(text), lw=lw)
    #print(line_centered(marker*tw))
    #print(line_centered(title))
    #print(line_centered(marker*tw))
    print_centered(title, line_width)




if __name__ == "__main__":
    hess, geom, masses = get_hessian_geom_mass('3c1b')
    rots = load_rotations('3c1b')
    vibinfo = vibcor.findif.get_vibinfo(hess, geom, masses)

    alpha = unicodedata.lookup("GREEK SMALL LETTER ALPHA")
    delta = unicodedata.lookup("GREEK CAPITAL LETTER DELTA")
    partial = unicodedata.lookup("PARTIAL DIFFERENTIAL")
    sigma = unicodedata.lookup("GREEK CAPITAL LETTER SIGMA")
    lamb_char = unicodedata.lookup("GREEK SMALL LETTER LAMDA")
    #line_width = pd.io.formats.terminal.get_terminal_size()[0]
    line_width = 40

    print_box_title("Optical Rotation @ Reference Geometry", line_width=line_width)
    ex_freqs = [str(x) for x in sorted([int(f) for f in rots['eq'].keys()], reverse=True)]
    for ex_f in ex_freqs:
        wl = float(ex_f)
        val = rots['eq'][ex_f]
        line = "{wl:<5.1f} nm {val: >14.8f}".format(wl=float(ex_f), val=rots['eq'][ex_f])
        print_centered(line, line_width)
    print("\n")

    print_box_title("Optical rotation at displaced geometry", line_width=line_width)
    for i in range(3*len(masses) - 6):
        print_centered("Mode {} A   {:>5.2f} cm-1".format(i, vibinfo['omega'][i]), line_width)
        for ex_f in ex_freqs:
            wl = float(ex_f)
            pval = rots[str(i)]['+'][ex_f]
            mval = rots[str(i)]['-'][ex_f]
            print_centered(f"{wl:<5.1f} nm (+)   {pval: >14.8f} (-)   {mval: >14.8f}", line_width)
        print("")

    print_box_title("Harmonic Correction per mode", line_width=line_width)
    for i in range(3*len(masses) - 6):
        print_centered("Mode {} A {:>5.2f} cm-1".format(i, vibinfo['omega'][i]), line_width)
        for ex_f in ex_freqs:
            wl = float(ex_f)
            pval = rots[str(i)]['+'][ex_f]
            mval = rots[str(i)]['-'][ex_f]
            eq_val = rots['eq'][ex_f]
            c = 0.5 * (pval + (2 * eq_val) - mval)
            print_centered(f"{wl:<5.1f} nm      {c: >5.2f}", line_width)

    print_box_title("Vibrationally-Averaged Optical Rotation", line_width=line_width)
    print_centered("{:^10} {:^10} {:^10} {:^10}".format(
        lamb_char,
        alpha+'(0)',
        delta+'(vib)'+alpha,
        "<"+alpha+">"), line_width)
    for ex_f in ex_freqs:
        P0 = rots['eq'][ex_f]
        P2 = 0
        for i in range(3*len(masses) - 6):
            pval = rots[str(i)]['+'][ex_f]
            mval = rots[str(i)]['-'][ex_f]
            P2 += 0.5 * (pval + (2 * P0) - mval)
        PTOT = P0 + P2
        wl=float(ex_f)
        print_centered(f"{wl:^10.1f} {P0: ^10.2f} {P2: ^10.2f} {PTOT: ^10.2f}", line_width)







    # output should be
    # wavelength | eq_val | correction | corrected_val |
    # 355        | xxx    |  yyy       | xxx + yyy     |
    # other wavelengths


