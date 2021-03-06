"""
Utilities for creating built-in modules
"""

from dataclasses import field, dataclass
from immutables import Map
from typing import Callable,  NoReturn, Optional, TypeVar, Dict, Tuple
from .vm_utils import repr_stack, stringify_value
from gurklang.types import Code, CodeFlags, Instruction, Scope, Stack, Value, NativeFunction

Z = TypeVar("Z", bound=Stack, contravariant=True)


def _fail(name: str, reason: str, stack: Stack, scope: Scope):
    print("Failure in function", name)
    print("Reason:", reason)
    print("> Stack: ", "[" + " ".join(map(stringify_value, repr_stack(stack))) + "]")
    raise RuntimeError(name, reason)


Fail = Callable[[str], NoReturn]


@dataclass
class Module:
    name: str
    members: Dict[str, Value] = field(init=False)

    def __post_init__(self):
        self.members = {}

    def add(self, member_name: str, value: Value):
        self.members[member_name] = value

    def register(self, name: Optional[str] = None):
        def inner(fn: Callable[[Z, Scope, Fail], Tuple[Stack, Scope]]) -> NativeFunction:
            native_fn = make_function(name)(fn)  # type: ignore
            self.add(native_fn.name, native_fn)
            return native_fn
        return inner

    def make_scope(self, id: int, parent: Optional[Scope]=None):
        return Scope(parent=parent, id=id, values=Map(self.members))


def make_function(name: Optional[str] = None):
    # Z is contravariant because a function should accept a subset of
    # stacks (e.g. only stacks with at least 2 elements)
    def inner(fn: Callable[[Z, Scope, Fail], Tuple[Stack, Scope]]) -> NativeFunction:
        fn_name = name or fn.__name__.replace("_", "-")
        def new_fn(stack, scope):
            local_fail: Fail = lambda reason: _fail(fn_name, reason, stack, scope)
            try:
                return fn(stack, scope, local_fail)
            except Exception as e:
                local_fail(f"uncaught exception {type(e)}: {' '.join(e.args)}")
        native_fn = NativeFunction(new_fn, fn_name)
        return native_fn
    return inner


def raw_function(*instructions: Instruction, name: str = "<raw>", source_code: Optional[str] = None):
    """
    Create `Code` with no closure and flags set to PARENT_SCORE
    """
    return Code(
        instructions,
        closure=None,
        flags=CodeFlags.PARENT_SCOPE,
        name=name,
        source_code=source_code
    )

R"""saybegin
!gurklang

:math ( + ) import

1 :x var
x println

{ x 1 + :x var } parent-scope :x++ jar

x++
x println

x++ x++
x println
sayend"""