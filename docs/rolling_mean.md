### 📈 Rolling Mean

**Công thức:**
$$
RM_t = \frac{1}{k} \sum_{i=0}^{k-1} x_{t-i}
$$
trong đó \(k\) là kích thước cửa sổ.

**Ý nghĩa:**
Làm mượt chuỗi thời gian để giảm nhiễu, giúp mô hình tập trung vào xu hướng dài hạn.

**Ví dụ:**
Với k=3 và chuỗi [1,2,3,4], giá trị rolling mean tại bước 4:
$$
RM_4 = \frac{2+3+4}{3} = 3
$$
