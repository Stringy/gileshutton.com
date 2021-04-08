---
title: "Wisdom"
date: 2021-04-08T19:19:25+01:00
draft: false
tags: ["coding", "wisdom", "rust"]
categories: ["code"]
summary: "My latest side project; a new programming language"
---

In a fit of misguided optimism I've recently started a new project to create a programming language.
This is something I've always wanted to try (and have attempted it on more than a few occasions) and 
this time I have an idea and I want to follow it through until it's "useful". The idea is to combine 
the syntax of Rust with the dynamic typing of Python and the regex support of Perl. The hope is that 
that will combine into a pretty excellent text-processing language, but avoid some of the readability
pitfalls that Perl falls into.

I get that it's a pretty weird combination of languages, but each have their benefits, at least in my 
opinion. Rust's syntax is incredibly well thought-out, and lends itself to a really ergonomic experience.
Python is incredibly flexible and powerful in its type system, which can be used to great effect. I've read
many blog posts (and listened to many of my colleagues) ranting about the lack of type system, but I think
it just gets out of the programmer's way and lets you do what you need to do. Also, the idiom that it's "better
to ask forgiveness than ask for permission" makes for very clean code and I tend to use it in code reviews
to push back on code with gratuitous use of `isinstance()`. 

Perl is probably the most surprising language to be inspired by. It has a horrible reputation
for being an archaic, write-only language that is a relic from another time. Honestly, I'd agree with
most of that. I've done more than my fair share of Perl scripting over the years and it's a very rough
language to work with, but there's one thing it does extremely well and that's *text processing.* Having regexes
as first class citizens in the language was a stroke of genius and is something I want to emulate within
Wisdom.

So what is Wisdom going to look like? Hopefully a little like this[^1]:

```
use std::fs;

fn filter(path: str, re: regex) -> bool {
    return path ~= re;
}

let root = "/some/path";

for path in std::fs::walk(root) {
    if filter(path, r"^[foo].*$") {
        print("Matched ${path}");
    }
}
```

I currently have a fairly basic language working, including a large number of the syntactical features
you can see above, and I'm adding more and more as the weeks go by.  

Here's the current feature list:
- Variable declarations.
- Functions (including arguments, return values, etc.)
- Recursive expressions, including a whole raft of binary operators.
- While loops (with continue and break, constructs.)
- If expressions (including else if, else, etc.)
- A handful of built-in functions.

Perhaps it doesn't sound like much, but using just these features I've been able to implement some non-trivial
programs:

### Fibonacci Sequence
```
fn fib(n: int) {
    let a = 1;
    let b = 1;

    while n > 0 {
        let tmp = a + b;
        a = b;
        b = tmp;
        n = n - 1;
    }

    return b;
}

print(fib(10));
print(fib(20));
```

### Prime number counter[^2]
```
fn primes_slow(limit: int) {
    let count = 2;
    let result = 0;
    while count < limit {
        let top = count / 2;
        let n = 2;
        while n < top {
            if count % n == 0 {
                break;
            }
            n = n + 1;
        }
        if n > top {
            result = result + 1;
        }
        count = count + 1;
    }
    return result;
}

print("found: ", primes_slow(10000), " primes");
```

Progress so far has been surprisingly quick, particularly over Easter where I had plenty of time
to churn out new features. It's probably the most satisfying project I've worked on so far, particularly
because I can now use it to actually write useful programs. It started life as a glorified calculator,
supporting single-line mathematical expressions, and has already grown into something general purpose.

Next on the feature list is probably the loose type system and casting, starting with the addition of lists.
They'll be sparse lists like Python, and once they're finished I'm hoping I can introduce Python2-style 
for loops. Perhaps I'll add iterators at a later date, but for now I think we can deal with the performance
of simple lists.

In the next few weeks I want to write about tokenizing source code, constructing the AST[^3], and expression parsing
using the shunting yard algorithm[^4], but for now I'm going to get stuck in to fleshing out the language
so I can get a bit closer to my original vision for the language. I just need to avoid the endless temptation
to over-engineer everything!

[^1]: One day I'll figure out how to make my own Wisdom syntax highlighting on here (and in the IDE!)
[^2]: It's dead slow at the moment, but it's still accurate. The Python equivalent runs in less than a second
      but mine runs in just over 5 seconds. Performance can come later! I'll just keep adding language features first.
[^3]: https://en.wikipedia.org/wiki/Abstract_syntax_tree
[^4]: https://en.wikipedia.org/wiki/Shunting-yard_algorithm