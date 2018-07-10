
def load_rotations(mol_name):
    "returns the dictionary that our collect_rotations script wrote to disk"
    pass

def compute_alpha_ii(eq_val, mode_vals):
    "returns a vector with each element being the second derivative of rotation withrespect to a mode"
    pass

def extract_modes(rots, wavelength):
    "returns a list of tuples where each element is (rotation[mode][+][wavelength], rotation[mode][-][wavelength]"
    pass

def compute_correction(alpha_ii):
    "computes the seccond term in the second to last equation on pg 1892 of wiberg"
    pass

# How to get displacement sizes!

# need the hessian, geom, masses!

# need to use the vibcor.findif module!
if __name__ == "__main__":
    # put all the pieces together!

    # output should be
    # wavelength | eq_val | correction | corrected_val |
    # 355        | xxx    |  yyy       | xxx + yyy     |
    # other wavelengths


