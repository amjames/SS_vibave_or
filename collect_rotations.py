"""
collects the optical rotation for each mode/{+,-}/wavelength + the eq_geom
"""

from pathlib import Path

def ensure_d_exists(p):
    if p.exists():
        if p.is_dir():
            return p
        else:
            raise Exception("{} is not a directory".format(p))
    else:
        raise Exception("{} does not exist".format(p))

def ensure_f_exists(p):
    if p.exists():
        if p.is_file():
            return p
        else:
            raise Exception("{} is not a file")
    else:
        raise Exception("{} does not exist".format(p))


def get_mode_rot_fchk(mol, mode_index, direction):
    # start from the current directory
    tmp = Path.cwd()
    # next part is mol_name
    tmp = ensure_d_exists(tmp / mol)
    # next part is vibave
    tmp = ensure_d_exists(tmp / 'vibave')
    # next part is mode+(number)
    tmp = ensure_d_exists(tmp / "mode{}".format(mode_index))
    # next part is step1 if direction is + and step2 if direction is -
    if direction == '+':
        d_num = 1
    elif direction == '-':
        d_num = 2
    elif direction in (1,2):
        d_num = direction
    else:
        raise Exception("Invalid direction {}".format(direction))
    tmp = ensure_d_exists(tmp / "step{}".format(d_num))
    # finally we can append rot.fchk and we have the full path
    tmp = ensure_f_exists(tmp / "rot.fchk")
    # then we read the file and return the contents
    return tmp.read_text()

def get_ref_rot_fchk(mol):
    tmp = Path.cwd()
    tmp = ensure_d_exists(tmp / mol / 'vibave')
    tmp = ensure_d_exists(tmp / 'refgeom')
    tmp = ensure_f_exists(tmp / 'rot.fchk')
    return tmp.read_text()

def get_all_rotations():
    pass

if __name__ == "__main__":
    # This code will only be run when the file is executed like `python this_file.py`
    # and not when imported `import this_file`

    # we are going to collect the rotations in a dictionary so we create a dictionary to hold them
    rots = {}

    # in this example I have hard coded the number of modes here, but we could accept it as a command line argument
    nmode = 30
    # same with the mol name, here we only have one, but I could have tons and want to let myself specify the mol name
    # as an argument
    mol_name = '3c1b'

    # we are going to need to use the tools in our `vibcor` module from here out so we import it.
    import vibcor
    # first we grab the equilibrium geometry values.
    rots['eq'] = vibcor.fchk.parse_optical_rotation(get_ref_rot_fchk(mol_name))
    # now we can loop over the modes since all of them will work the same way
    for i in range(nmode):
        # we will have a nesting layer for each mode since we have mode[i][+/-] to store
        rots[i] = {}
        for sign in {'+','-'}:
            rots[i][sign] = vibcor.fchk.parse_optical_rotation(get_mode_rot_fchk(mol_name, i, sign))

    # Now we can look up stuff
    print("rotations for eq geom:")
    # The stored value is a dict {wavelengh: value}
    for k,v in rots['eq'].items():
        print('{}nm:         {:5.6f}'.format(k, v))

    # for a mode we have to look one layer deeper
    print("rotations for mode1+")
    for k,v in rots[1]['+'].items():
        print("{}nm:         {:5.6f}".format(k,v))

    # but we want to use these later when we compute derivatives. So we need to store them the dictionary can be dumped
    # and read in later using json. Python has a nice interface to json through the json module so we import it.

    import json

    # we need to tell the json module to dump our data into a file. So we need to open one first. When ever you open a
    # file you need to make sure you close it, so we use a python context manager to ensure that happens for us.
    with Path("{}_rotations.json".format(mol_name)).open('w') as dump_file:
        # above we opened a file "{mol_name}_rotations.json" in (w)riting mode giving it a handle dump_file inside this
        # block
        json.dump(rots, dump_file, indent=4)

    # now we are done!

