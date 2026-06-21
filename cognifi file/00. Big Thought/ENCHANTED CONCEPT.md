# Strategi Pengembangan CogniFi v1.1: Intelligent Orchestration

## 1. Evolusi Input: Dari Ticker Manual ke Entity Recognition

Agar sistem tidak "manual", kita menambahkan layer **Automatic Ticker Extraction** di awal setiap input.

- **Langkah 1 (The Matcher):** Sistem melakukan scan input user menggunakan kamus (_Mapping_) nama populer saham ke ticker (misal: "Ratu" → `RAJA.JK`).
    
- **Langkah 2 (The Fallback):** Jika nama tidak ada di kamus, Gemini bertugas mencari ticker yang paling relevan dari teks tersebut.
    
- **Status:** Jika ticker ditemukan, lanjut ke analisis bias. Jika tidak, sistem masuk ke mode edukasi umum.
    

## 2. Dynamic Router: Bias Detector vs. Learning Hub

Ini menjawab poin kamu tentang orang yang ingin "nanya dan belajar". Sistem tidak boleh memaksa deteksi bias jika user hanya ingin tahu konsep.

- **Logic Check:** Sebelum klasifikasi bias, Gemini melakukan **Intent Classification**.
    
    - _Intent A (Intervention):_ User menunjukkan urgensi/niat transaksi (Misal: "Beli GOTO sekarang?") → **Output:** Deteksi Bias + Counter-Evidence.
        
    - _Intent B (Educational):_ User bertanya konsep (Misal: "Apa itu Price to Earning ratio?") → **Output:** Penjelasan singkat + data fundamental riil tanpa intervensi emosional.
        
    - _Intent C (Hybrid):_ User nanya dan ada indikasi emosi (Misal: "SIDO lagi murah ya? Bagus gak buat masuk?") → **Output:** Penjelasan fundamental + _Soft-warning_ tentang potensi Loss Aversion.
        

## 3. Arsitektur Output: The 3-Layer Response

Untuk membuat AI yang optimal dan solutif, output dibagi menjadi tiga bagian tetap:

1. **Direct Answer (Konteks):** Jawaban langsung atas pertanyaan user (baik itu definisi atau data harga).
    
2. **Behavioral Layer (Jika terdeteksi):** Jika ada indikasi FOMO/Bias, tampilkan statistik historis dan _Friction Question_.
    
3. **Actionable Knowledge (Edukasi):** Satu fakta fundamental atau tips riset yang relevan agar user belajar cara menganalisis sendiri di masa depan.
    

## 4. RAG Integration (The Brain)

Agar AI tidak "halusinasi", semua jawaban edukatif harus menarik data dari:

- **Vector Database:** Berisi buku _Behavioral Finance_ dan aturan bursa (IDX).
    
- **Live API (yfinance):** Memberikan data harga dan statistik riil.
    

---

### Apa yang Perlu Kita Tambahkan Lagi? (Kolaborasi Pikiran)

Menurut saya, supaya **CogniFi** benar-benar optimal, kita butuh satu fitur lagi: **"The Sovereign Checkpoint"**.

- **Ide:** Jika user bersikeras mau beli setelah melihat bukti (karena itu hak otonomi mereka), AI jangan cuma diam. AI bisa memberikan **"Pre-Mortem"**.
    
- **Eksekusi:** AI bertanya: _"Oke, jika kamu beli sekarang dan besok harganya turun 10% (seperti kejadian di 2024), apa rencana kamu? Jual atau tambah muatan?"_ * **Tujuan:** Ini memaksa user punya _Trading Plan_ sebelum klik tombol beli di broker.
















# Dokumen Pengembangan: CogniFi v1.1 - Intelligent Orchestration

## 1. Alur Kerja Sistem (The Pipeline)

Sistem tidak lagi menunggu input manual ticker, melainkan bekerja dalam rantai otomatis:

1. **Input Raw Text:** User mengetik bebas (misal: _"Ratu gimana ya, kok orang-orang pada bilang mau to the moon?"_)
    
2. **Entity & Intent Extraction (Otomatis):**
    
    - **NER:** Sistem mendeteksi entitas `"Ratu"` dan mencocokkannya ke ticker `RAJA.JK`.
        
    - **Intent:** Sistem mendeteksi apakah user ingin **Analisis Cepat (Bias)** atau **Edukasi (Learning)**.
        
3. **Dynamic Routing:**
    
    - **Jalur A (High Urgency):** Jika ada indikasi emosi/niat beli → Jalankan _Rule-based_ + _Counter-Evidence_ (Data Historis).
        
    - **Jalur B (Low Urgency/Learning):** Jika user bertanya konsep → Jalankan _RAG_ (Penjelasan Teoretis).
        
4. **Integrated Output:** Memberikan jawaban yang menggabungkan fakta harga, deteksi bias, dan intervensi edukatif.
    

---

## 2. Struktur Baru Output (The 3-Pillar Response)

Agar AI optimal dan solutif, setiap jawaban harus mengandung tiga unsur:

|**Pilar**|**Fungsi**|**Isi Contoh**|
|---|---|---|
|**Pilar 1: Contextual Data**|Menjawab pertanyaan dasar.|"Harga saham RAJA saat ini Rp..., naik 12% dalam 3 hari."|
|**Pilar 2: Behavioral Friction**|Mengintervensi bias.|"Terdeteksi pola FOMO. Secara historis, kondisi ini diikuti koreksi rata-rata 15%."|
|**Pilar 3: Growth Mindset**|Memberikan edukasi.|"Tahukah kamu? Membeli saat harga ATH tanpa volume tinggi seringkali menjebak retail."|

---

## 3. Penambahan Fitur "Pre-Mortem" (Friction by Design)

Ini adalah kolaborasi pikiran kita untuk memperkuat aspek _Sovereign Node_:

- **Mekanisme:** Jika deteksi bias tinggi, AI wajib memunculkan satu pertanyaan reflektif sebelum menutup percakapan.
    
- **Contoh Pertanyaan:** _"Jika kamu masuk sekarang dan harga berbalik turun 10% besok, apakah kamu punya rencana exit, atau kamu hanya berharap harga naik kembali?"_
    

---

## 4. Optimalisasi AI (The Hybrid Brain)

Untuk mencapai performa optimal tanpa membengkakkan biaya:

- **Rule-Based:** Menangani 80% kasus standar (typo nama saham, deteksi kata kunci "beli", "takut", "ketinggalan").
    
- **LLM (Gemini):** Menangani semantik yang rumit dan memberikan "nuansa" pada jawaban edukatif agar tidak kaku.
    
- **RAG (Retrieval):** Mengambil data dari dokumen _Behavioral Finance 101_ milikmu agar AI tidak memberikan saran keuangan sembarangan.











## Analisis Jujur: Konsep vs Realita Kodebase

### 1. Auto Ticker Extraction (NER) — Prioritas #1

**Kondisi sekarang:** `app.py` sudah punya fallback scan 40 ticker hardcoded, tapi masih butuh input manual di sidebar.

**Gap nyata:** Nama seperti `"Ratu"` → `RAJA.JK`, `"Tele"` → `TLKM.JK` belum ada mapping-nya. Ini bisa diselesaikan dengan dua layer:

- **Layer 1:** Dict mapping nama populer → ticker (cepat, deterministik)
- **Layer 2:** Gemini fallback kalau tidak ada di dict

Ini **paling achievable** dan memberikan UX impact terbesar — user tidak perlu isi sidebar sama sekali.

---

### 2. Intent Router A/B/C — Prioritas #2

**Kondisi sekarang:** `llm.py` punya pre-classification tapi hasilnya hanya dipakai untuk konteks RAG, bukan untuk _routing_ yang benar-benar mengubah jalur output.

**Gap nyata:** Tidak ada "Educational mode" yang berbeda. Semua input diperlakukan sama — masuk ke bias detection pipeline, meski inputnya murni pertanyaan seperti _"Apa itu PER?"_.

**Diskusi dulu soal Intent B (Educational mode):**

Ini yang perlu kita pikirkan bersama. Ada dua filosofi yang berbeda:

**Opsi A — Conversational:** Output seperti ChatGPT. Jawab _"PER adalah rasio harga saham dibagi earnings per share..."_ dengan bahasa natural, tanpa card/struktur kaku. Cocok untuk pertanyaan konsep murni.

**Opsi B — Structured Card:** Output berbentuk kartu dengan komponen tetap — definisi, contoh angka riil dari saham IDX, dan satu tip praktis. Lebih "on-brand" dengan identitas CogniFi yang data-driven.

**Opsi C — Hybrid smart:** Sistem deteksi dulu — kalau pertanyaan ada ticker (`"PER BBCA berapa?"`), tampilkan data riil + penjelasan. Kalau murni konsep (`"Apa itu PER?"`), jawab conversational. Kalau hybrid (`"SIDO lagi murah ya?"`), gabungkan data + soft-warning.

Menurutku **Opsi C** paling sesuai dengan konsep ENCHANTED kamu — tapi paling kompleks juga untuk dieksekusi.

---

### 3. Pre-Mortem — Prioritas #3

**Kondisi sekarang:** Belum ada sama sekali.

**Yang menarik:** Ini sebenarnya bisa diimplementasi sebagai **extension dari intervention yang sudah ada** — hanya perlu satu kondisi tambahan: kalau bias detected + confidence tinggi → append satu pertanyaan pre-mortem di akhir output.

Tidak perlu arsitektur baru, cukup tambah ke `intervention.py` dan tampilkan di `app.py`.