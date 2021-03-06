from typing import List
from gurklang.types import Atom, Instruction, Int, Stack, Value
import pprint
import gurklang.vm as vm
from gurklang.vm_utils import repr_stack
from gurklang.parser import parse


source1 = R"""
{ :b var :a var b a } :my_swap jar
1 2 3 4 my_swap
"""

source2 = R"""
:math ( + ) import

{ :x var { x + } } :make_adder jar
5 make_adder :add5 jar

"Answer:" print
37 add5 print
37 { add5 } ! print
"""

source3 = R"""
{1} {2} :true if print

{1} {2} :false if print
"""

source4 = r"""
:math :qual import

160 15 :%make math   # 160 15 %make      ~  (32 3)
4 10 :%make math     # 4 10 %make        ~  (2 5)
:%+ math print       # (23 3) (4 10) %+  ~  (166 15)
"""


source5 = r"""
# 1. Only import certain names (from math import %make)
:math (%make) import
4 2 %make print

# 2. Import all the names (from math import *)
:math :all import
4 2 %make print

# 3. Qualified import (import math)
:math :qual import
4 2 :%make math print

# 4. Renaming qualified import (import math as shmath)
:math :as:shmath import
4 2 :%make shmath print

# 5. Prefixed import (from math import * as "math_*")
:math :prefix import
4 2 math.%make print

# 6. Custom prefixed import (from math import * as "math_*")
:math :prefix:shmath import
4 2 shmath.%make print
"""


source6 = R"""
:math ( + ) import
:inspect ( code-dump ) import

{ :f var :x var { x f ! } } :my-close jar

{ { + } my-close } :make-adder jar

5 make-adder :add5 jar

37 add5 print  #=> 42
40 add5 print  #=> 45
"""


source7 = R"""
:math ( + - < * ) import

{ dup 2 <
  { drop 1 } parent-scope
  { dup 1 - n! * } parent-scope
  if !
} parent-scope :n! jar

10000 n! println
"""


source8 = R"""
:math ( + - < * ) import

{
  dup 2 <
    { }
    { dup 1 - rot3 * swap n!-impl } parent-scope
    if !
} parent-scope :n!-impl jar

{ 1 swap n!-impl drop } parent-scope :n! jar

100000 n! drop
"""


source9 = R"""
:inspect :prefix import
:math ( + - < * ) import

{
  dup 2 <
  { drop 1 } parent-scope
  { dup 1 - n! * } parent-scope
  if !
} parent-scope :n! jar

:n! inspect.dis
"""


source10 = R"""
:math ( +       ) import
:coro ( iterate ) import

{ dup println 1 + } (1 ())
iterate
iterate
iterate
iterate

"""


source11 = R"""
:math ( +       ) import
:coro ( iterate ) import

#########################################

{ swap parent-scope swap jar }
parent-scope :pjar jar

#########################################

{ { } parent-scope close close }
:--make-generator pjar

{ rot3 swap --make-generator swap jar }
:generator pjar

{ iterate forever }
:forever pjar

#########################################

{
  swap dup
  println
  (1 100) sleep
  swap dup rot3 +
}
parent-scope
(1 (1 ()))
:fib generator

fib forever
"""

source12 = R"""
:math (* -) import
{ { (. .) { dup 1 - rot3 * swap n! }
    (1) {}
  } case
} :n! jar
1 10 n!
"""

stack, scope = vm.run(parse(source12))

print("\n----------------")
print("Resulting stack:")
pprint.pprint(repr_stack(stack))