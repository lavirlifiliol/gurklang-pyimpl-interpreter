"""
Standard library modules that aren't built-ins
"""
from typing import List
from ..builtin_utils import Module
from . import math, inspect



modules: List[Module] = [math.module, inspect.module]
