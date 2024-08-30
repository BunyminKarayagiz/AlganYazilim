def matrix_multiply(A, B):
    """
    İki matrisi çarpar.
    
    :param A: Matris A
    :param B: Matris B
    :return: A ve B'nin çarpımı
    """
    # A'nın sütun sayısı B'nin satır sayısına eşit olmalı
    if len(A[0]) != len(B):
        raise ValueError("Matrislerin boyutları uyumsuz.")
    
    # Çarpım işlemi
    result = [[sum(x * y for x, y in zip(A_row, B_col)) for B_col in zip(*B)] for A_row in A]
    
    return result

# Test
A = [[1, 2, 3], [4, 5, 6]]
B = [[7, 8], [9, 10], [11, 12]]

print("Matris A:")
for row in A:
    print(row)

print("\nMatris B:")
for row in B:
    print(row)

result = matrix_multiply(A, B)

print("\nMatris A ve B'nin çarpımı:")
for row in result:
    print(row)
