from pathlib import Path
import vibcor

hess_fchk = Path('3c1b/hessian.fchk').read_text()

hessian = vibcor.fchk.parse_hessian(hess_fchk)
print(hessian)
