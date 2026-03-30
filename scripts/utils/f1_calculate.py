precision = 0.9532
recall = 0.8797

f1 = 2 * precision * recall / (precision + recall + 1e-16)
print(f"F1: {f1:.4f}")