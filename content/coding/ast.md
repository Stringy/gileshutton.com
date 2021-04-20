---
title: "Abstract Syntax Trees"
date: 2021-04-18T17:15:50+01:00
draft: false
tags: ["coding", "wisdom"]
categories: ["code"]
summary: "Wisdom, expressions, and AST construction."
---

Step one to building a language, as it turns out, is parsing text. Tokenizing and AST creation are 
at the core of interpreter design. In this post I'll talk a bit about how that works and what it looks
like in my Wisdom interpreter.

## Tokenizing

Tokenizing is the process of splitting the source code into logical chunks, known as tokens. The goal of 
the tokenizer is not to identify meaningful syntactical constructions, but just turn the source into 
a stream of Tokens that can be interpreted by something that understands the language semantics.

For example, consider the following Wisdom snippet:

```rust
let a = foo() + 5;
```

Which of the above is syntactically interesting at this level? You could be forgiven for thinking
that `foo()` is a single token, but in fact it is treated as three separate tokens: `foo`, an identifier, 
`(` the left parenthesis, and `)` the right parenthesis. As I said before, the tokenizer doesn't know 
about the language itself, and only knows about splitting a string into bits.

How do we go about tokenizing in Rust? One of the cool Rust features that I've used a lot in the tokenizer
is closures. In particular, having a function that accepts a closure and consumes characters from the input
string, passing each character into the closure, which can then return whether to continue processing[^2]:

```rust
fn consume_until<F: FnOnce(char) -> bool + Copy>(&self, func: F) {
    let mut c = self.first(); // peek the next character
    loop {
        if func(c) {
            break;
        }
        
        // consume the character
        self.next(); 
        // peek the next character
        c = self.first();
    }
}
```

This is a very simple pattern, but in practice is extremely powerful. Consider processing
whitespace: 

```rust
self.consume_until(|c| !c.is_whitespace());
``` 

Or consuming a base-10 integer:

```rust
self.consume_until(|c| c.is_numeric());
```

Combining these closures makes the tokenizer extremely simple to reason about and extend.

Another extremely useful feature I've taken advantage of is iterators (combined with some other closure
excellence.) I wanted an iterator over all tokens in a source file, partly for simplicity, and partly for
the power of the iterator ecosystem within rust. In practice, I ended up just immediately `collect()`ing
the iterator but it's still useful!

```rust
pub fn tokenize(input: &str, with_whitespace: bool) -> impl Iterator<Item=Token> + '_ {
    let mut c = Cursor::new(input, with_whitespace);
    std::iter::from_fn(move || {
        if c.is_eof() {
            None
        } else {
            Some(c.next_token())
        }
    })
}
```

## Abstract Syntax Trees

An abstract syntax tree is a data structure used to store and process the semantic meaning behind
source code. Using the tokenizer, the wisdom interpreter provides meaning to the tokens and produces
a simplified representation of the source, which can then be interpreted during execution. 

Tree structures in Rust are not as simple as they are in other languages. Of course, in Rust you get significantly
more assurance about the safety of the data and the memory use in the tree. In C[^3], you might have something like
this:

```cpp
typedef struct {
    size_t num_children;
    node *children;
} AST;

typedef struct _node {
    struct _node *children;
    enum node_type type;
    // this could contain data specific to the node type.
    void *metadata;
} node;

enum node_type {
    Call,
    Expression,
    // ...
};
```

There's lots of lovely raw pointers in there, and difficult-to-verify state. It can be managed very effectively, but
you as the programmer have to do all that work yourself. If you get it wrong, nothing is going to tell you about it 
(until it segfaults of course!) Not to mention the lack of type safety.

Now, in Rust you can probably do something similar, but the `void*` doesn't translate very well. Using generics doesn't 
necessarily work because then your AST can only contain nodes of the same generic type. When you're having to implement
dozens of different node types for a full AST, then this system just doesn't work. I'm sure someone more versed with Rust
than me could come up with a way of doing it like that, but I sought a simpler solution: enums[^4]. 

Enums encode variance in a type. Immediately this looks like a perfect fit for our different node types. At this point
I tried to consider all the different nodes that I'd need and how to encode them. First I had a grand `NodeKind` enum
with everything encoded within that, but it didn't make sense because you can categorise langauge constructions into
different categories, primarily statements and expressions. A statement is something that does not return a value, and 
is used for high-level language constructs like function declarations and imports. An expression is the opposite and 
encapsulates parts of the language that can return values, like a simple mathematical expression (e.g. `1 + 2 * 3`) or
even loops and if/else blocks. Not only do Rust enums allow us to encode variance, it also allows us to add state to 
enum values! Using this state, we can encode the entire tree. For example, a local variable declaration (`let a = 1;`) 
needs to be encoded with the name of the variable as well as the expression for its value: 

```rust
enum Expr {
    // ...
    Assign(String, Box<Expr>),
    // ...
}
```

Notice how we needed to `Box` the `Expr`. This is because Rust disallows recursive types because the size of the type
becomes unknown. Behind a `Box` the size is known, because it is the equivalent to a pointer to a heap allocation.

For example, consider a function call: `foo()`. This will be tokenized into `foo` (an identifier) `(`, and `)`.
Construction of the AST for this expression is simple. The parser knows that an identifier followed
by an opening parenthesis is a function call, so creates a `Call` AST node, noting the name of the function
so it can be looked up later on.

Of course, that's a very simple example, so let's look at something a little more complex:

```rust
let a = 256 * b + 6;
```

Reading that as humans, we can see that it's a local variable declaration, called `a`, and the 
right-hand-side is the expression `256 * b + 6`, and using BODMAS, or PEMDAS or however you learned
precedence in school, we know this actually means `(256 * b) + 6`.

How does wisdom make that same construction?

From the top, we get the `let` identifier. The interpreter knows that this is a keyword and knows what 
it expects following that keyword, namely an identifier. We find one, `a`, so we're all good at this point.
Next, there's an optional equals sign (`let a;` is valid, it will just declare the variable as having no value)
and, since an equals sign is provided, it expects an expression, which in our case is the `256 * b + 6`.

We're halfway there. We know that we have a variable declaration for the variable called `a`, and that there is
an expression to calculate its value. But how do we parse the expression such that operator precedence is followed
and the result is as expected? 

## The Shunting Yard Algorithm[^5].

Invented by Edsgar Dijkstra, the algorithm uses stacks to process operands and operators to parse complex expressions.
It has also been generalised to parse operator precedence. Ideal for this use case! In terms of wisdom, operands are 
defined as distinct `Expr`s and operators are `BinOp` (which is another enum that encapsulates the operators.)

There are two stacks. One for operands, and one for operators. Depending on a set of rules, operands and operators
are pushed into or popped from the relevant stacks. The rules can be summarised as follows:

1. If the symbol is an operand, push it into the operands stack.
2. If the symbol is an operator, and the operator stack is empty, push it into the operator stack.
3. If the symbol is an operator, and has higher precedence than the operator at the top of the stack, or 
   it has the same precedence as the operator at the top of the stack but it is right-associative, push it on the stack.
4. If the symbol is an operator, and has lower precedence than the operator at the top of the stack, or
   it has the same precedence as the operator at the top of the stack but it is left-associative, pop operators
   and operands off the stacks until this is no longer true and then push the operator.
5. After processing all symbols, pop operators and operands off the stacks, combining each operator with
   two operands, until the stacks are empty.
   
I've shamelessly ~~stolen~~ borrowed the operator precedence from C++[^6]:

```rust
impl BinOp {
   pub fn precedence(self) -> usize {
      use BinOp::*;
      match self {
         Mul | Div | Mod => 3,
         Add | Sub => 4,
         Lt | LtEq | Gt | GtEq => 6,
         EqEq | NotEq => 7,
         BinAnd => 8,
         Xor => 9,
         BinOr => 10,
         And => 11,
         Or => 12,
         Eq => 14,
      }
   }
}
```

So lets consider the example from before: `256 * b + 6;`

1. First symbol is a literal `256` it's an operand so push it to the stack.
2. `*` is an operator, but there are no operators in the stack so push it.
3. `b` is another operands, push it to the stack.
4. `+` is an operator, and looking at the stack it has lower precedence than `*`.
   a. Since the precedence is lower, we must pop `*` as well as the two operands `256` and `b`, combine them and then 
      push the result back on the stack `(256 * b)`. `+` is now pushed to the stack since it is empty.
5. Final symbol, `6` is an operand so push it to the stack.
6. No more symbols, so we pop an operator and two operands off the stack: `(256 * b)`, `6` are the operands, and the
   only operator is `+`.
   
Result: `(256 * b) + 6`

If that wall of text wasn't descriptive enough, here's a handy table:

| Symbol | Operands | Operators | Notes |
| :------------ | :------------: | :------------: | :--- |
| `256` | - | - | `256` is an operand, so just push it to the operand stack | 
| `*` | `256` | - | `*` is an operator, and the operator stack is empty, so push it. |
| `b` | `256` | `*` | `b` is an operand, so just push it to the operand stack |
| `+` | `b` <br/> `256` | `*` | `+` is an operator. Its precendence is lower than *, so pop *, and pop both 256 and b. Combine into an operand (256 * b) and push to the operands stack. Push + to operators stack. |
| `6` | `(256*b)` | `+` | `6` is an operand, so just push it to the operand stack |
| None | `6` <br/> `(256*b)` | `+` | No more symbols. Pop operators and operands (in pairs) until the stacks are empty.|

Result: `(256 * b) + 6`

## Interpreting

Once we have a tree, we now have something that is mostly interpretable. With gratuitous [mis]use of the Visitor Pattern[^7],
the first implementation I've written (affectionately called `SlowInterpreter`) passes through the AST, visiting each 
node and recursing as necessary until the end of the program. Rust's match expression really helps in achieving this aim,
since we can both match on all enum variants (i.e. Node types in this case) and also deconstruct the internals of those variants. 

```rust
fn visit_expr(&self, expr: &Expr) -> Result<Value, Error> {
   match &expr.kind {
      Block(block) => self.visit_block(&block)?,
      Ret(expr) => return self.visit_expr(&expr)?,
      // .. etc
   }
}
```

--- 

Off the back of all this, I've been able to build a surprisingly well featured language with modern (and admittedly Rust-like)
syntax. Going forward I'm going to add more features and then work on performance with the ultimate aim of turning the
`SlowInterpreter` into the `SlightlyQuickerInterpreter`

Eventually I want to lower the AST into some sort of intermediate representation so that I can then build some sort of JIT
(which will, of course, be finally known as the `FastInterpreter`.) I was also discussing with a friend today that it'd 
be fun to compile wisdom down to JVM class files and then just run it like Java! Who knows. I'll probably do all of this
eventually.

[^1]: https://github.com/Stringy/wisdom
[^2]: https://github.com/Stringy/wisdom/blob/develop/wisdom/tokenizer/src/cursor.rs#L306
[^3]: I'd say C++ here but I'm not nearly well versed enough in C++ to make a decent example. 
I'm sure you could use some fun templates to make it better, but I'm far more experienced with plain C.
[^4]: https://doc.rust-lang.org/rust-by-example/custom_types/enum.html
[^5]: https://en.wikipedia.org/wiki/Shunting-yard_algorithm
[^6]: https://en.cppreference.com/w/cpp/language/operator_precedence
[^7]: https://en.wikipedia.org/wiki/Visitor_pattern