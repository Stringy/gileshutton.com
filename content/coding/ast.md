---
title: "Abstract Syntax Trees"
date: 2021-04-07T17:15:50+01:00
draft: true
tags: ["coding", "wisdom"]
categories: ["code"]
summary: "Wisdom, expressions, and AST construction."
---

I've recently been working on a new side project to create a programming language called Wisdom[^1].
It'll eventually end up somewhere between the trifecta of Rust, Python, and Perl (of all things)
for a dynamic scripting language, that's good at text processing, but with readable, modern, syntax. 
In this post I'm going to talk about source code tokenization, and construction of the AST, all in our
favourite language: Rust.

## Tokenizing

Tokenizing is the process of splitting the source code into logical chunks, known as tokens. The goal of 
the tokenizer is not to identify meaningful syntactical constructions, but just turn the source into 
a stream of Tokens that can be interpreted by something that understands the language semantics.

For example, consider the following Wisdom snippet:

```
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

The cursor 


[^1]: https://github.com/Stringy/wisdom
[^2]: https://github.com/Stringy/wisdom/blob/develop/wisdom/tokenizer/src/cursor.rs#L306