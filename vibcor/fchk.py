"""
Wrappings around the Gaussian Program.
"""
import re
from pathlib import Path
import numpy as np

from .constants import physconst

def freq_conv_au_nm(freq_au):
    "convert a field energy in [Eh] to a field wl in nm"
    freq_J = freq_au * physconst['hartree2J']
    freq_m = physconst['h'] * physconst['c'] / freq_J
    return int(round(freq_m * 1e9))

def compute_opt_rot(Gprime, f_au, mw):
    hbar = physconst['h'] / (2*np.pi)
    prefactor = -72e6 * (hbar**2) * physconst['na'] / physconst['c']**2 / physconst['me']**2
    return prefactor * (f_au**2) * np.trace(Gprime) / mw / 3.0


def parse_fchk_array(fchk_text, array_name):
    """Find/read an array from the fchk file"""
    matcher = re.compile(r'\A(?P<title>{})\s+R\s+N=\s+(?P<nele>\d+)\Z'.format(array_name), re.IGNORECASE)
    fchk_lines = fchk_text.split('\n')
    start_line = 0
    nline = 0
    found_match = False
    for i, line in enumerate(fchk_lines):
        match = matcher.match(line)
        if match is not None:
            found_match = True
            start_line = i +1
            nline = int(match.group('nele'))//5 + (1 * bool(int(match.group('nele'))%5))
    if found_match:
        data = np.array([float(x) for x in " ".join(fchk_lines[start_line:start_line+nline]).split()])
        return data
    else:
        raise Exception("Could not find array {}".format(array_name))

def parse_fchk_val(fchk_text, val_name):
    """Parses a scalar from the fchk file"""
    matcher = re.compile(
            r'\A(?P<title>{})\s+(?P<dtype>[IR])\s+(?P<val>[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[EedD][+-]?\d+)?)'.format(val_name),
            re.IGNORECASE)
    for line in fchk_text.split('\n'):
        match = matcher.match(line)
        if match is not None:
            t = int if match.group('dtype') == 'I' else float
            return t(match.group('val'))
    raise Exception("Count not find value {}".format(val_name))

def parse_optical_rotation(fchk_text):
    """Get FD property tensors from the fchk file and compute optical rotations.

    Returns
    -------
    The specific rotations as a dictionary.
        Keys are field wavelengths in nm.
        Values have standard units [deg cm^3 dm^-1 g^1 mol]

    .. note:: Gaussian only prints optical rotation to two decimal places in the output so we use the property tensors in the
    fchk file to compute them manually.  Rather than parsing from output

    .. note:: Gaussian actually does not compute optical rotations correctly anyway, so this is how they should be
    gotten in order to obtain accurate values.
    """
    mw = np.sum(parse_fchk_array(fchk_text, array_name="Real atomic weights"))
    au_freqs = parse_fchk_array(fchk_text, array_name="Frequencies for FD properties")
    nm_freqs = [freq_conv_au_nm(f_au) for f_au in au_freqs]
    n_freq = len(au_freqs)
    rot_tensors = parse_fchk_array(fchk_text, array_name="FD Optical Rotation Tensor").reshape(-1, 3,3)
    rotations = {}
    for Gprime, f_au, f_nm in zip(rot_tensors, au_freqs, nm_freqs):
        rotations[f_nm] = compute_opt_rot(Gprime, f_au, mw)
    return rotations

def parse_gradient(fchk_text):
    """Parses the gradient from the fchk file.

    .. note:: It seems that this entry is _always_ writen, but is filled with zeros when it is not actually calculated.
    User should be wary.
    """
    grad = parse_fchk_array(fchk_text, array_name="Cartesian Gradient")
    return grad

def parse_hessian(fchk_text):
    """Parses the hessian from the fchk file.

    .. note:: The hessian is symmetric so only the upper/lower triage is stored and we have to reconstruct it. Yet
    another terrible design choice...

    """
    hess_dat = parse_fchk_array(fchk_text, array_name="Cartesian Force Constants")
    natom = parse_fchk_val(fchk_text, val_name="Number of atoms")
    hess = np.zeros((3*natom, 3*natom))
    hess[np.tril_indices_from(hess)] = hess_dat
    hess[tuple(reversed(np.tril_indices_from(hess)))] = hess_dat
    return hess

# def find_or_build_fchk(hint):
#     if not hint.exists():
#         raise CantFindFchk("The hint: {} does not exist".format(str(hint)))
#     if not hint.is_dir():
#         if hint.suffix == '.fchk':
#             return hint
#         elif hint.suffix == '.chk':
#             fchk = executables.formchk(hint)
#             return fchk
#         else:
#             raise CantFindFchk("The hint: {} is file but does not have the correct extension".format(str(hint)))

#     fchk_list = list(sorted(hint.glob('*.fchk'), key=lambda p: p.stat().st_mtime, reverse=True))
#     if len(fchk_list) > 0:
#         return fchk_list[0]

#     chk_list = list(sorted(hint.glob("*.chk"), key=lambda p: p.stat().st_mtime, reverse=True))
#     if len(chk_list) > 0:
#         return executables.formchk(chk_list[0])

#     raise CantFindFchk("Could not find fchk with hint: {}".format(str(hint)))

# class FchkParser(object):
#     def __init__(self, hint = Path.cwd()):
#         """Fchk Parser

#         Parameters
#         ----------
#         hint : str {pathlike}, optional {cwd}
#             Where to search for the .chk/.fchk file

#         .. note:: If a fchk file exists it will be used. So be sure to remove old ones if re-using a work directory.
#         .. note:: If no fchk can be found, but a chk is. The fchk will be generated.
#         """
#         hint = Path(hint)
#         self.fchk = find_or_build_fchk(hint).read_text()

#     def get(self, what, category=None):
#         """Get a datum from the parser.

#         what : str {gradient, rotations, hessian, or any other name in the fchk file}
#             The quantity to obtain. Special values "gradient", "rotations", "hessian" are allowed. Any other quantity
#             requires the category kwarg and must be exactly the key in the fchk file.
#         category : str {'array', 'value'}, optional when `what` is one of {'gradient', 'rotation', 'hessian'}
#             If the quantity is an array or value set this option accordingly.
#         """
#         what = what.lower()
#         if what == 'gradient':
#             return parse_gradient(self.fchk)
#         elif what == 'hessian':
#             return parse_hessian(self.fchk)
#         elif what in ('rotation', 'rotations'):
#             return parse_rotation(self.fchk)
#         else:
#             if category == 'array':
#                 return parse_fchk_array(self.fchk, array_name=what)
#             elif category == 'value':
#                 return parse_fchk_array(self.fchk, val_name=what)
#             else:
#                 raise ParseError("Can't parse {} with category: {}".format(what, category))

