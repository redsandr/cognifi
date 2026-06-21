# CogniFi Bias Detection: Accuracy Evaluation Report

## Experiment Overview

Model: CogniFi Bias Detector (Rule Based NLP)  
Dataset size: **495 test cases**  
Bias classes:

- FOMO
- LOSS_AVERSION
- CONFIRMATION_BIAS
- NONE

Evaluation dilakukan untuk mengukur akurasi klasifikasi bias psikologis dalam teks investasi.

# Accuracy Results

**Overall Accuracy**
468 / 495 = 94.5%

Progress iterasi model:

| Iteration   | Accuracy  |
| ----------- | --------- |
| Iteration 1 | 78.8%     |
| Iteration 2 | 84.6%     |
| Iteration 3 | 91.9%     |
| Iteration 4 | **94.5%** |

Total improvement: **+15.7%**

# Per-Class Performance

| Bias              | Precision | Recall | F1 Score | TP  | FP  | FN  |
| ----------------- | --------- | ------ | -------- | --- | --- | --- |
| FOMO              | 97.2%     | 92.8%  | 94.9%    | 141 | 4   | 11  |
| LOSS_AVERSION     | 95.8%     | 95.0%  | 95.4%    | 115 | 5   | 6   |
| CONFIRMATION_BIAS | 94.4%     | 91.9%  | 93.2%    | 102 | 6   | 9   |
| NONE              | 90.2%     | 99.1%  | 94.4%    | 110 | 12  | 1   |

Observations:

- **FOMO detection sangat presisi (97.2%)**    
- **Loss Aversion recall tinggi (95%)**
- **Confirmation Bias masih sedikit overlap dengan FOMO**
- **NONE memiliki recall hampir sempurna (99.1%)**    

# Error Analysis

Total misclassification:
27 / 495 cases
Distribusi error menunjukkan beberapa pola utama.

## 1. Loss Aversion → NONE

Contoh:
Tambah posisi GOTO, DCA biar breakeven price turun  
Add posisi 3x di saham yang terus turun  
Beli lagi biar HPP makin turun

Masalah:
- sistem belum cukup kuat mengenali **DCA / averaging down behavior**

Kategori:
Still solvable via rule

## 2. Confirmation Bias → NONE

Contoh:
Potensi BBRI besar kan? Fundamentalnya solid  
Semua analisis yang gue baca positif  
Yang bilang jelek pasti ga paham fundamental

Masalah:
- frasa **seeking validation** belum ter-cover semua.

Kategori:
Rule improvement possible


## 3. FOMO ↔ Loss Aversion confusion

Contoh:
ANTM naik 22% 3 hari ini, kayaknya momen serok  
Saham lagi digoreng bandar, gue mau ikut cuan  
Harga ga bakal balik ke level ini lagi

Masalah:
- beberapa kalimat punya **campuran urgency + justification**

Kategori:
Ambiguous cases


## 4. FOMO ↔ Confirmation Bias overlap

Contoh:
Semua orang bullish  
Teman analis bilang target harga naik  
Trending di semua platform

Masalah:
- social proof bisa masuk dua kategori

Kategori:
Ambiguous labeling

# Error Solvability Classification

Dari **27 error** yang tersisa:

| Category                     | Estimated Cases |
| ---------------------------- | --------------- |
| Fixable via rule improvement | ~20             |
| Genuinely ambiguous          | ~7              |

Ambiguous cases adalah kalimat yang bahkan manusia bisa berbeda pendapat tentang labelnya.

# Estimated Performance Ceiling

Rule-based system memiliki batas performa.

Estimated ceiling:
96% – 97%
Alasan:
1. dataset mengandung beberapa label ambigu
2. menambah keyword berlebihan bisa merusak generalisasi
3. semakin tinggi akurasi → semakin tinggi risiko overfitting rule

# Recommended Next Steps

## 1. Fix Remaining Rule Gaps
Prioritas:
- DCA / averaging down detection
- stronger social proof signals
- keyword coverage untuk confirmation bias

Potensi peningkatan:
94.5% → ~96%

## 2. Audit Ambiguous Labels
Beberapa contoh kemungkinan mislabel:
"GOTO trending di semua platform, gue masuk karena analisis gue"

Sistem mendeteksi FOMO, tapi label dataset adalah confirmation bias.
Perlu verifikasi ulang.
Potensi gain:
+0.5% – 1%

## 3. Hybrid Model Strategy

Gunakan AI hanya pada kasus **low confidence**.
Contoh:
confidence < 0.40
Pipeline:
Rule-based classifier  
        ↓  
confidence check  
        ↓  
AI fallback (LLM)

Keuntungan:
- tetap cepat
- API cost rendah
- meningkatkan akurasi kasus edge

# Final Conclusion

Current model performance:
Accuracy: 94.5%  
Dataset size: 495  
Errors remaining: 27

Interpretation:
- Rule-based system sudah **sangat kuat**
- Mayoritas error masih dapat diperbaiki
- Batas realistis sistem rule-based sekitar **96–97%**

Strategi terbaik:
1. Fix rule gaps  
2. Audit ambiguous labels  
3. Deploy hybrid AI fallback

Dengan pendekatan ini, sistem dapat mencapai **~97–98% effective accuracy** tanpa membuat rule engine terlalu kompleks.