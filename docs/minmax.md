### 🔢 MinMax Scaler

**Công thức:**
$$
x_{scaled} = \frac{x - x_{min}}{x_{max} - x_{min}}
$$

**Ý nghĩa:**
Đưa dữ liệu về khoảng [0, 1] để giúp mô hình học hiệu quả hơn, tránh lệch tỉ lệ giữa các đặc trưng.

**Ví dụ:**

Giả sử:
- \(x = 150\)
- \(x_{min} = 100\), \(x_{max} = 200\)

Khi đó:
$$
x_{scaled} = \frac{150 - 100}{200 - 100} = 0.5
$$
