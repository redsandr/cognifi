Strategi dari **Claude itu benar secara engineering**. Kalau langsung lompat ke 4000 data, biasanya yang terjadi:
- kamu menambah **banyak data yang tidak memperbaiki error**
- waktu labeling jadi lama
- pattern miss tidak pernah benar benar dipahami

Jadi pipeline yang sehat memang **iteratif seperti ini**.

# Posisi kamu sekarang

Dataset: **274**
Target akhir: **4000**
Roadmap:
```
274 → 500 → 1000 → 4000
```
Sekarang kamu ada di **fase 1**.
# Fokus fase 1 (274 → 500)
Yang harus kamu lakukan **bukan tambah data random**, tapi tambah **edge cases**.
Target:
```
+226 samples
```
Distribusi yang disarankan:

| tipe data         | jumlah |
| ----------------- | ------ |
| FOMO              | 60     |
| LOSS_AVERSION     | 50     |
| CONFIRMATION_BIAS | 50     |
| NONE              | 40     |
| AMBIGUOUS / MIXED | 26     |

Kenapa begitu?
Karena error kamu sekarang **bukan distribusi**, tapi **ambiguity**.
# Jenis data yang harus kamu tambah
## 1. FOMO implisit
Sekarang dataset kamu banyak yang eksplisit.
Contoh eksplisit:
```
semua orang beli
takut ketinggalan
```
Tambahkan **yang lebih halus**:
```
BBCA naik terus, kayaknya telat kalau ga masuk sekarang
```
```
Harga udah jauh naik, tapi kalau masih lanjut gimana?
```
## 2. Confirmation bias halus
Contoh sekarang biasanya:

```
semua bilang bagus
```

Tambahkan:

```
Aku sudah analisis dan menurutku ini pasti naik
```

```
Banyak analis bullish kan?
```

---

## 3. NONE yang tricky

Ini sangat penting supaya sistem tidak over-detect bias.

Contoh bagus:

```
berapa persen cut loss yang sehat?
```

```
strategi DCA untuk market volatile?
```

```
apakah volume bisa jadi indikator breakout?
```

---

## 4. Mixed bias (yang bikin sistem bingung)

Contoh:

```
Teman teman banyak masuk saham ini dan analis juga bilang bagus.
```

Ini sebenarnya:

```
FOMO + confirmation bias
```

Label tetap **FOMO** karena trigger utama **social influence**.

---

## 5. Bahasa pasar saham

Tambahkan bahasa real:

```
pump
cuan
nyangkut
averaging
gorengan
bandar
```

Contoh:

```
udah nyangkut di GOTO, mending hold aja ya?
```

---

# Setelah dataset 500

Lakukan lagi **test akurasi**.

Target:

```
Accuracy > 97%
```

Kalau turun:

berarti dataset baru membuat **rule engine konflik**.

---

# Fase 2 (500 → 1000)

Di fase ini fokus:

```
real world language
```

Ambil contoh dari:

- Stockbit
    
- Telegram
    
- X
    
- TikTok
    

Biasanya muncul bentuk seperti:

```
bbca gila naiknya
telat ga masuk sekarang?
```

atau

```
udah minus 20%, tahan dulu lah
```

---

# Fase 3 (1000 → 4000)

Baru scale besar.

Disini biasanya:

```
synthetic + real data mix
```

rasio:

```
60% synthetic
40% real user text
```

---

# Saran paling penting

Sekarang **jangan langsung buat 226 data random**.

Lakukan ini dulu:

### Audit 5 error kamu

Yang kamu tulis tadi:

```
4 FOMO → confirmation
1 confirmation → loss aversion
```

Buat **20 variasi kalimat dari setiap error pattern**.

Total:

```
5 pattern × 20 = 100 data baru
```

Ini akan memperbaiki **weak spot model**.

---

# Kesimpulan

Sekarang langkah yang benar:

```
1. Analisis 5 error pattern
2. Buat 20 variasi tiap pattern
3. Tambah edge case language
4. Scale dataset ke 500
5. Test ulang akurasi
```

Jangan buru buru ke 4000.

---

Kalau kamu mau, aku juga bisa bantu satu hal yang **sangat membantu di fase 274 → 500**:

Aku bisa buatkan **100 edge-case dataset paling berbahaya untuk bias detection** yang biasanya bikin model salah klasifikasi. Ini biasanya yang dipakai untuk **stress test NLP classifier**.