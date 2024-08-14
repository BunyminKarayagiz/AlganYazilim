import sympy as sp

# Çemberin merkezi (h, k) ve yarıçapı r
h, k, r = 0, 0, 5
# Doğrunun denklemi y = mx + c
m, c = 1, -10

# Çemberin denklemi: (x-h)^2 + (y-k)^2 = r^2
x, y = sp.symbols('x y')
circle_eq = sp.Eq((x - h)**2 + (y - k)**2, r**2)

# Doğrunun denklemi: y = mx + c
line_eq = sp.Eq(y, m*x + c)

# Kesişim noktalarını bul
intersection_points = sp.solve((circle_eq, line_eq), (x, y))

# Kesişim durumunu kontrol et
if len(intersection_points) == 0:
    print("Doğru çemberi kesmez.")
elif len(intersection_points) == 1:
    print("Doğru çembere teğettir.")
else:
    print("Doğru çemberi iki noktada keser.")
