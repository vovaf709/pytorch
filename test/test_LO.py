import torch
from typing import Iterator
import functools
import contextlib

# TODO: move this into library proper
@contextlib.contextmanager
def no_dispatch() -> Iterator[None]:
    guard = torch._C._DisableTorchDispatch()
    try:
        yield
    finally:
        del guard

HANDLED_FUNCTIONS_RECTANGULAR = {}

def implements(torch_aten_function, HANDLES_DICT):
    """Register a torch function override for RectangularTensor.

    This decorator takes a function in the torch API as a
    parameter. Applying this decorator to a function adds that function
    as the registered override for the torch function passed as a
    parameter to the decorator.
    """
    @functools.wraps(torch_aten_function)
    def decorator(func):
        HANDLES_DICT[torch_aten_function] = func
        return func
    return decorator

class RectangularTensor(torch.Tensor):
    handled_functions = HANDLED_FUNCTIONS_RECTANGULAR
    __slots__ = "full_rank", "well_cond"

    @staticmethod
    def __new__(cls, elem, *args, **kwargs):
        # The wrapping tensor (RectangularTensor) is just a meta tensor, so it
        # doesn't hold any memory (meta tensor is generally the preferred type
        # of tensor you want to make a subclass from)...
        r = torch.Tensor._make_subclass(cls, elem.to('meta'), elem.requires_grad)
        # ...the real tensor is held as an element on the tensor.
        r.elem = elem
        r.full_rank = kwargs['full_rank'] if 'full_rank' in kwargs else True
        r.well_cond = kwargs['well_cond'] if 'well_cond' in kwargs else True
        r.rcond = kwargs['rcond'] if 'rcond' in kwargs else None
        return r

    def __repr__(self):
        return f"RectangularTensor({self.elem})"

    def tensor(self):
        return self.elem

    @classmethod
    def __torch_dispatch__(self, func, types, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        if func not in self.handled_functions:
            return NotImplemented
        return self.handled_functions[func](*args, **kwargs)

@implements(torch.ops.aten.linalg_solve, HANDLED_FUNCTIONS_RECTANGULAR)
def solve(A, B):
    A_tensor = A.elem
    # As per https://github.com/pytorch/pytorch/issues/54151
    rcond = A.rcond if A.rcond is not None else \
        torch.finfo(A_tensor.dtype).eps * max(A_tensor.size(-2), A_tensor.size(-1))
    if A.full_rank:  # QR
        return torch.linalg.lstsq(A_tensor, B, driver="gels").solution
    else:
        if self.well_cond:  # PQR
            return torch.linalg.lstsq(A_tensor, B, rcond=rcond, driver="gelsy").solution
        else:  # SVD
            return torch.linalg.lstsq(A_tensor, B, rcond=rcond, driver="gelsd").solution

HANDLED_FUNCTIONS_SQUARE = {}
class Square(RectangularTensor):
    handled_functions = HANDLED_FUNCTIONS_SQUARE

    def __new__(cls, elem, *args, **kwargs):
        invertible = kwargs['invertible'] if 'invertible' in kwargs else True
        well_cond = kwargs['well_cond'] if 'well_cond' in kwargs else True
        r = super().__new__(cls, elem, invertible=invertible, well_cond=well_cond)
        return r

    def __repr__(self):
        return f"Square({self.elem})"

    def tensor(self):
        return self.elem

@implements(torch.ops.aten.linalg_solve, HANDLED_FUNCTIONS_SQUARE)
def solve(A, B):
    if A.full_rank:  # PLU
        return torch.linalg.solve(A.elem, B)
    else:
        return super().solve(A.elem, B)

if __name__ == "__main__":
    A = torch.randn(3, 3, requires_grad=True).clone()
    b = torch.randn(3, 2, requires_grad=True)
    # Make A not invertible
    A[2] = 2.4 * A[0] + 3 * A[1]

    A_sqr = Square(A, invertible=False)
    X = torch.linalg.solve(A_sqr, b)
    print(type(X), X.__dict__)
    # # torch.autograd.gradcheck(torch.solve, [A, b])
    # # B is not in the image of A, so there is no solution
    # # solve returns the vectors X that minimize ||AX - B|| (least squares solution)
    # assert not torch.allclose(A @ X.elem, b, atol=1e-6)

    # # "Project" B onto the image of A
    # b = A @ A.T @ b
    # A_sqr = Square(A, invertible=False)
    # X = torch.linalg.solve(A_sqr, b)
    # # B is now on the image of A, so there is a solution and solve finds it
    # assert torch.allclose(A @ X.elem, b, atol=1e-6)