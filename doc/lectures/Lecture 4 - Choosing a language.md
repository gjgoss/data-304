- Imperative vs declarative
- Package management and ecosystems
- Notebooks vs traditional scripts with I/O
- Practical choices
	- Plotting
	- Advanced (applied) statistics
	- C++ acceleration
	- Modern APIs
- SQL and database specific languages
- R, matlab, and data/computational specific languages
- Haskell
```r
> library(functional)
> p <- Curry(paste, collapse="")
> p(letters[1:10])
```

```r
> Compose(function(x) x[length(x):1], Curry(paste, collapse=""), toupper)(letters)
[1] "ZYXWVUTSRQPONMLKJIHGFEDCBA"
```
- Provability
![[Pasted image 20241023105311.png]]