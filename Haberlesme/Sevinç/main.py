import sympy as sp

fon_expr = '(z+1)/(z**2+2*z)'
z = sp.Symbol('z')
fon = sp.sympify(fon_expr)
a = sp.Symbol("-2")
n = sp.Symbol('n')

limit_al = (z - a)**n * fon

# Simplify the expression before taking the limit
limit_al_simplified = sp.simplify(limit_al)

# Calculate the limit
R = sp.limit(limit_al_simplified, z, a) / sp.factorial(n-1)

# n'i 1 azaltarak faktöriyeli hesapla
R = R.subs(n, n-1)

print(R)
