#  Mini-LISP

`2023.01.13`

## Development Environment and Tools
- MacOS 12.6
- Python 3.10.9
- Python library
  - `os, sys` for code reading
  - `functools` for operators: `mul *`
  - `re` for syntax checking

## How to Use
Run the script by `python3 lisp.py <your test case file>`, then you can enter your `Lisp` program.

Ex: `python3 lisp.py 01_1.lsp`

If you want to test your cases line by line, you can just run the script by `python3 lisp.py`.

The interpreter will then print `lisp>` in terminal, and you can just enter `your code` after it.

## Type Definiation

* Boolean: `#t` for true and `#f` for false
* Number: Signed integer from $-2^{31} \text{ to } 2^{31}$
* Function: see below

## Operation Overview

| Name     | Symbol | Example             |
| -------- | ------ | ------------------- |
| Plus     | +      | `(+ 1 2) => 3`      |
| Minus    | -      | `(- 1 2) => -1`     |
| Multiply | *      | `(* 2 3) => 6`      |
| Divide   | /      | `(/ 6 3) => 2`      |
| Modulus  | mod    | `(mod 8 3) => 2`    |
| Greater  | >      | `(> 1 2) => #f`     |
| Smaller  | <      | `(< 1 2) => #t`     |
| Equal    | =      | `(= 1 2) => #f`     |
| And      | and    | `(and #t #f) => #f` |
| Or       | or     | `(or #t #f) => #t`  |
| Not      | not    | `(not #t) => #f`    |

#### Other operations: `define, fun, if`


## Lexical Details

```ebnf
separator  := [ \t\n\r]
letter     := [a-z]
digit      := [0-9]
number     := 0 | [1-9]digit* | -[1-9]digit*
ID         := letter(letter | digit | "-")*
bool-val   := #[t|f]
```

## Grammar and Behavior

1. ##### Program

``` ebnf
PROGRAM ::= STMT STMTS
STMTS   ::= STMT STMTS | {}
STMT    ::= EXP | DEF-STMT | PRINT-STMT
```

2. ##### Print

``` ebnf
PRINT_STMT ::= '(' print_num EXP ')' 
           | '(' print_bool EXP ')'
```

3. ##### Expression
   
``` ebnf
EXPS  ::= EXP EXPS | {}
EXP   ::= bool_val | number | VARIABLE | NUM_OP | LOGICAL_OP | FUN_EXP | FUN_CALL | IF_EXP 
```

4. ##### Numerical Operations 

``` ebnf
NUM_OP ::= PLUS | MINUS | MULTIPLY | DIVIDE | MODULES | GREATER | SMALLER | EQUAL
```

``` lisp
(+ 1 2 3 4) ; output: 10
```

5. ##### Logical Operations

``` ebnf
LOGICAL_OP ::= AND_OP | OR_OP | NOT_OP
```

``` lisp
(and #t (> 2 1)) ; output: #t
```

6. ##### Define statement

``` ebnf
DEF_STMT ::= '(' define VARIABLE EXP ')'
VARIABLE ::= id 
```

``` lisp
(define x 5)
(+ x 1) ; output: 6
```

7. ##### Function

``` ebnf
FUN_EXP  ::= '(' _fun FUN_ID FUN_BODY ')'
FUN_ID   ::= '(' VARIABLE VARIABLES ')'
FUN_BODY ::= EXP
FUN_CALL ::= '(' FUN_EXP PARAM PARAMS ')'
         | '(' FUN_NAME PARAM PARAMS ')'
PARAM    ::= EXP 
PARAMS   ::= PARAM PARAMS 
VARIABLES::= VARIABLE VARIABLES
LAST_EXP ::= EXP
FUN_NAME ::= id
```

``` lisp
(define bar (fun (x y) (+ x y)))
(bar 2 3) ; output: 5
```

8. ##### If Expression

``` ebnf
IF_EXP  ::= '(' _if TEST_EXP THAN_EXP ELSE_EXP ')' 
TEST_EXP::= EXP             
THAN_EXP::= EXP             
ELSE_EXP::= EXP 
```

``` lisp
(if(= 1 0) 1 2) ; output: 2
```

9.  ##### Recursion
    
    Able to handle recursive function call

``` lisp
(define f
  (fun (x) (if (= x 1)
              1
              (* x (f (- x 1))))))
(f 4) ; output: 24
```

10.  ##### Type Checking

    For type specifications of operations, please check out the table below:

  |            Op             |      Parameter Type       |             Output Type             |
  | :-----------------------: | :-----------------------: | :---------------------------------: |
  | `+`, `-`, `*`, `/`, `mod` |         Number(s)         |               Number                |
  |       `<`, `>`, `=`       |         Number(s)         |               Boolean               |
  |    `and`, `or`, `not`     |        Boolean(s)         |               Boolean               |
  |           `if`            | Boolean(s) for `test-exp` | Depend on `then-exp` and `else-exp` |
  |           `fun`           |            Any            |              Function               |
  |       Function call       |            Any            | Depend on `fun-body` and parameters |

``` lisp
(> 1 #t)    ; Type Error: Expect 'number' but got 'boolean'.
```

11.  ##### Nested Function

   There could be a function inside another function. The inner one is able to access the local variables of the outer function. The syntax rule of fun-body should be redefined to:

``` ebnf
fun-body ::= def-stmt* exp
```

``` lisp
(define dist-square
  (fun (x y)
    (define square (fun (x) (* x x)))
    (+ (square x) (square y))))

(print-num (dist-square 3 4)) ; output: 25
```

12. ##### First-class Function
    
    Functions can be passed like other variables. Furthermore, it can keep its environment. (like lambda in Python)

``` lisp
(define foo
  (fun (f x) (f x)))

(print-num
  (foo (fun (x) (- x 1)) 10)) ; output: 9
```
