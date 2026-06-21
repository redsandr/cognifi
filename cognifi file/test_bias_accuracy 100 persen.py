# test_bias_accuracy.py
# ─────────────────────────────────────────────────────────────────────────────
# Test akurasi deteksi bias CogniFi — keyword-based (bias_detector.py)
# Dua layer test:
#   1. UNIT TEST  — test setiap scorer langsung, tanpa API call
#   2. ACCURACY   — jalankan semua test case, hitung precision/recall per bias
#
# Cara pakai:
#   python test_bias_accuracy.py            → full test + laporan akurasi
#   python test_bias_accuracy.py --unit     → unit test saja (cepat)
#   python test_bias_accuracy.py --verbose  → print detail tiap test case
#
# ─────────────────────────────────────────────────────────────────────────────

import sys
import argparse
import json
from collections import defaultdict
from bias_detector import detect_bias

# ═════════════════════════════════════════════════════════════════════════════
# TEST DATASET
# 120 kalimat variatif, masing-masing dengan label ground truth.
# Dibagi 4 kategori: FOMO, LOSS_AVERSION, CONFIRMATION_BIAS, NONE
#
# Prinsip variasi:
#   - Bahasa formal ↔ slang ↔ campuran
#   - Langsung ↔ implisit ↔ tersamar
#   - Kalimat pendek ↔ panjang
#   - Ada ticker ↔ tidak ada ticker
#   - Bahasa Indonesia ↔ English ↔ campuran (code-switching)
# ═════════════════════════════════════════════════════════════════════════════

with open('data/test_cases_extended.json', 'r', encoding='utf-8') as f:
    raw_cases = json.load(f)

TEST_CASES = [(case['text'], case.get('ticker', 'BBCA.JK'), case['expected']) for case in raw_cases]

TEST_CASES = [

    # ─────────────────────────────────────────────────────────────────────────
    # FOMO — 35 kalimat
    # ─────────────────────────────────────────────────────────────────────────

    # Eksplisit urgensi + social proof
    ("GOTO mau naik nih, semua orang pada beli, masih sempet ga?",                  "FOMO"),
    ("Udah masuk belum? BBRI lagi rame banget di grup, katanya mau pump",            "FOMO"),
    ("Semua temen gua udah profit dari TLKM, gue belum masuk",                      "FOMO"),
    ("Rame banget di TikTok soal BREN, kayaknya mau naik terus",                    "FOMO"),
    ("Buruan masuk ASII sekarang sebelum kehabisan momentum",                       "FOMO"),

    # Urgensi implisit
    ("BBCA udah naik 20% dalam seminggu, kayaknya ini timing yang bagus",           "FOMO"),
    ("Harga BMRI lagi rendah tapi semua bilang mau naik minggu ini",                "FOMO"),
    ("Feeling kuat banget, GOTO ini bakal pump minggu depan",                       "FOMO"),
    ("Udah telat belum kalau masuk TLKM sekarang?",                                 "FOMO"),
    ("Chart BBRI cantik banget, kayaknya mau breakout",                             "FOMO"),

    # Social proof tanpa urgensi eksplisit
    ("Influencer favorit gue bilang UNVR bagus sekarang",                           "FOMO"),
    ("Di grup investasi semua lagi bahas BREN, pada beli",                          "FOMO"),
    ("Kata si X GOTO ini undervalued, dia udah masuk dari kemarin",                 "FOMO"),
    ("Semua hijau hari ini, sayang banget kalau gue ga ikutan",                     "FOMO"),
    ("Temen gua profit 30% dari EMTK minggu lalu, mau coba juga",                  "FOMO"),

    # Slang + code switching
    ("BBCA udah moon guys, masih worth it ga buat entry sekarang?",                 "FOMO"),
    ("Everyone's buying GOTO rn, should I fomo in?",                               "FOMO"),
    ("Moodeng effect nih, semua saham ikut naik, cuan ga nih?",                    "FOMO"),
    ("Yolo BBRI deh, terlambat dikit tapi masih bisa cuan",                        "FOMO"),
    ("BREN trending di Stockbit, gue takut ketinggalan rally ini",                  "FOMO"),

    # Kalimat panjang + detail
    ("Gue liat GOTO udah naik 25% dalam 5 hari ini, semua orang di WA grup pada "
     "bilang ini baru awal, masih mau naik lagi, gue mau masuk sekarang aja",      "FOMO"),
    ("Tadi pagi baca artikel soal BBCA dapat kontrak gede, langsung pada beli, "
     "gue takut ketinggalan momentum ini kalau ga masuk hari ini",                  "FOMO"),

    # Tanpa ticker spesifik
    ("Semua orang pada cuan, gue doang yang belum masuk pasar saham",               "FOMO"),
    ("Pasar lagi bullish banget, takut ketinggalan rally",                          "FOMO"),
    ("Komunitas gue bilang sekarang waktu terbaik beli saham bank",                 "FOMO"),

    # English
    ("GOTO looks like it's about to pump, everyone's talking about it",             "FOMO"),
    ("I'm afraid of missing out on this BBRI rally, should I buy now?",            "FOMO"),
    ("All my friends are making money on TLKM, thinking of jumping in",             "FOMO"),
    ("This looks solid right? BBCA seems like it's breaking out",                   "FOMO"),
    ("Great prospects for GOTO right? Should I get in now?",                        "FOMO"),

    # Borderline — masih FOMO tapi lebih halus
    ("Volume BMRI naik gede banget tadi, mungkin ada berita bagus",                 "FOMO"),
    ("Kayaknya bagus deh BREN ini, lagi naik terus",                               "FOMO"),
    ("Udah riset dikit soal GOTO, keliatannya prospeknya oke",                     "FOMO"),
    ("ASII lagi bullish, gue mau tambah posisi",                                   "FOMO"),
    ("Mau masuk TLKM, kira-kira timing oke ga sekarang?",                          "FOMO"),

    # ─────────────────────────────────────────────────────────────────────────
    # LOSS AVERSION — 35 kalimat
    # ─────────────────────────────────────────────────────────────────────────

    # Denial + nunggu balik modal
    ("GOTO lagi nyangkut, nunggu balik modal aja dulu",                            "LOSS_AVERSION"),
    ("BBRI udah turun 15%, tapi ini cuma koreksi sementara, gue tahan",            "LOSS_AVERSION"),
    ("Sabar aja, TLKM pasti balik ke harga beli gue",                              "LOSS_AVERSION"),
    ("Rugi kalau jual sekarang, mending hold dulu",                                "LOSS_AVERSION"),
    ("Fundamental GOTO masih bagus kok, ini cuma noise pasar",                     "LOSS_AVERSION"),

    # Averaging down
    ("BBCA turun, malah jadi kesempatan average down nih",                         "LOSS_AVERSION"),
    ("Beli lagi BMRI biar rata, harga sekarang lebih murah",                       "LOSS_AVERSION"),
    ("Tambah posisi GOTO, DCA aja biar breakeven price turun",                     "LOSS_AVERSION"),
    ("Harga BREN murah sekarang, kesempatan beli lebih banyak",                    "LOSS_AVERSION"),
    ("Average down TLKM, gue yakin balik",                                         "LOSS_AVERSION"),

    # Blame eksternal
    ("ASII digoreng bandar nih, harusnya udah naik dari kemarin",                  "LOSS_AVERSION"),
    ("GOTO dimanipulasi, gue yakin ini tidak wajar turun",                         "LOSS_AVERSION"),
    ("Ada yang jual gede BBRI makanya turun, bukan fundamental",                   "LOSS_AVERSION"),
    ("Pasti ada bandar main di EMTK, makanya ga naik-naik",                       "LOSS_AVERSION"),
    ("TLKM harusnya naik, tapi ada yang nyuppress harga",                          "LOSS_AVERSION"),

    # Kalimat panjang + detail loss aversion
    ("Gue udah nyangkut di GOTO dari harga 150, sekarang 90, tapi gue yakin "
     "bakal balik lagi ke 150, fundamentalnya masih bagus",                        "LOSS_AVERSION"),
    ("BBRI gue udah minus 20%, gue mau average down lagi biar breakeven "
     "price turun, kan kalau naik dikit langsung BEP",                             "LOSS_AVERSION"),

    # Perubahan narasi
    ("Awalnya gue beli TLKM untuk jangka panjang, tapi sekarang fokus "
     "balik modal dulu",                                                           "LOSS_AVERSION"),
    ("Investasi GOTO gue, target awalnya 200, sekarang target balik modal dulu",   "LOSS_AVERSION"),

    # Slang
    ("Nyangkut parah di BREN, waiting to breakeven dulu",                         "LOSS_AVERSION"),
    ("Hold GOTO, gue belum mau cut loss, pasti balik",                            "LOSS_AVERSION"),
    ("Masa mau jual rugi, mending tunggu dulu",                                    "LOSS_AVERSION"),
    ("Kagak mau realized loss, hold dulu BMRI",                                    "LOSS_AVERSION"),

    # English
    ("I'm stuck in GOTO, just waiting to break even",                             "LOSS_AVERSION"),
    ("This is just a correction, I'll hold my BBRI position",                     "LOSS_AVERSION"),
    ("Averaging down on TLKM to lower my cost basis",                             "LOSS_AVERSION"),
    ("Won't sell at a loss, ASII will bounce back",                               "LOSS_AVERSION"),
    ("Dollar cost averaging into BBCA even though it's down 20%",                 "LOSS_AVERSION"),

    # Tanpa ticker
    ("Nyangkut nih, nunggu balik modal aja dulu sebelum jual",                    "LOSS_AVERSION"),
    ("Sabar aja, pasar pasti balik. Gue ga mau jual rugi",                        "LOSS_AVERSION"),
    ("Ini cuma koreksi sementara, gue yakin",                                     "LOSS_AVERSION"),
    ("Salah bandar nih yang bikin turun, bukan fundamental",                      "LOSS_AVERSION"),

    # Borderline
    ("GOTO masih dalam support kuat, gue hold dulu",                              "LOSS_AVERSION"),
    ("BBRI fundamentalnya kuat, ga perlu khawatir soal penurunan sementara",      "LOSS_AVERSION"),
    ("Long term hold TLKM, jangka panjang pasti oke",                            "LOSS_AVERSION"),

    # ─────────────────────────────────────────────────────────────────────────
    # CONFIRMATION BIAS — 25 kalimat
    # ─────────────────────────────────────────────────────────────────────────

    # Leading query
    ("BBCA bagus kan? Prospeknya oke banget kan?",                                 "CONFIRMATION_BIAS"),
    ("GOTO ini pasti naik kan? Semua analis bilang positif",                      "CONFIRMATION_BIAS"),
    ("Kenapa TLKM pasti naik? Minta analisis yang mendukung",                     "CONFIRMATION_BIAS"),
    ("Potensi BBRI besar banget kan? Fundamentalnya solid",                       "CONFIRMATION_BIAS"),
    ("Alasan beli BREN dong, gue udah mau masuk nih",                            "CONFIRMATION_BIAS"),

    # Echo chamber
    ("Semua di grup sepakat GOTO mau naik, masuk ga?",                           "CONFIRMATION_BIAS"),
    ("Konsensus komunitas bilang BBCA undervalued, bener kan?",                   "CONFIRMATION_BIAS"),
    ("Rata-rata analisis yang gue baca bilang TLKM bagus",                        "CONFIRMATION_BIAS"),
    ("Semua influencer yang gue follow rekomen BMRI",                             "CONFIRMATION_BIAS"),
    ("Kata komunitas Stockbit BREN mau pump, setuju ga?",                         "CONFIRMATION_BIAS"),

    # Absensi risiko + leading
    ("Analisis GOTO dong, tapi yang positif aja ya",                              "CONFIRMATION_BIAS"),
    ("Gue yakin BBCA bagus, tolong konfirmasi alasannya",                         "CONFIRMATION_BIAS"),
    ("Semua tanda TLKM mau naik, gue bener ga?",                                 "CONFIRMATION_BIAS"),
    ("Jelasin kenapa BBRI adalah pilihan terbaik sekarang",                       "CONFIRMATION_BIAS"),

    # English
    ("GOTO looks great right? Can you confirm this is a good buy?",               "CONFIRMATION_BIAS"),
    ("Everyone agrees BBCA is undervalued, right?",                               "CONFIRMATION_BIAS"),
    ("Give me reasons to buy TLKM, I'm already pretty sure it's good",           "CONFIRMATION_BIAS"),
    ("My whole community says BMRI is bullish, can you confirm?",                 "CONFIRMATION_BIAS"),

    # Campuran
    ("BBRI bagus banget kan? Great prospects, agree?",                            "CONFIRMATION_BIAS"),
    ("Prospek GOTO solid right? Fundamentalnya oke banget",                       "CONFIRMATION_BIAS"),

    # Tanpa ticker
    ("Saham bank Indonesia pasti bagus kan? Semua bilang gitu",                   "CONFIRMATION_BIAS"),
    ("Gue udah yakin mau beli, tolong konfirmasi keputusan gue",                  "CONFIRMATION_BIAS"),
    ("Gue rasa pasar masih bullish, bener kan?",                                  "CONFIRMATION_BIAS"),
    ("Jelasin kenapa saham ini bagus, gue udah mau masuk",                        "CONFIRMATION_BIAS"),
    ("Semua analis setuju ini bagus, gue percaya mereka",                         "CONFIRMATION_BIAS"),

    # ─────────────────────────────────────────────────────────────────────────
    # NONE — 25 kalimat (tidak ada bias signifikan)
    # ─────────────────────────────────────────────────────────────────────────

    # Pertanyaan analitis genuine
    ("Tolong analisis fundamental BBCA secara objektif",                           "NONE"),
    ("Apa risiko terbesar investasi di GOTO saat ini?",                           "NONE"),
    ("Bandingkan valuasi BBRI vs BMRI berdasarkan PE ratio",                      "NONE"),
    ("Bagaimana performa TLKM saat IHSG koreksi 10%?",                           "NONE"),
    ("Apa yang bisa membuktikan thesis investasi BREN salah?",                    "NONE"),

    # Pertanyaan teknis + fundamental
    ("Berapa debt to equity ratio ASII saat ini?",                                "NONE"),
    ("Bagaimana revenue growth BBCA 3 tahun terakhir?",                           "NONE"),
    ("Siapa yang jual GOTO besar-besaran kemarin dan kenapa?",                    "NONE"),
    ("Analisis laporan keuangan TLKM Q3 2025",                                    "NONE"),
    ("Valuasi BBRI berdasarkan discounted cash flow",                             "NONE"),

    # Pertanyaan netral tanpa urgensi
    ("Gue mau belajar analisis fundamental, mulai dari mana?",                    "NONE"),
    ("Bedain investasi value vs growth di pasar Indonesia",                       "NONE"),
    ("Apa indikator terbaik untuk timing entry saham?",                           "NONE"),
    ("Gimana cara baca laporan keuangan emiten IDX?",                             "NONE"),
    ("Apa itu price to book ratio dan bagaimana menggunakannya?",                "NONE"),

    # Pertanyaan tentang risiko
    ("Apa downside risk terbesar BBCA tahun ini?",                               "NONE"),
    ("Dalam skenario terburuk, seberapa jauh GOTO bisa turun?",                  "NONE"),
    ("Red flag apa yang harus gue perhatikan di TLKM?",                          "NONE"),
    ("Berapa stop loss yang ideal untuk posisi BBRI?",                           "NONE"),
    ("Kapan harus cut loss dari posisi yang sedang rugi?",                       "NONE"),

    # English neutral
    ("What are the key risks of investing in GOTO right now?",                   "NONE"),
    ("Compare the valuations of BBCA and BBRI",                                   "NONE"),
    ("How has TLKM performed during market downturns historically?",              "NONE"),
    ("What would invalidate the bull thesis for BMRI?",                          "NONE"),
    ("Explain the fundamentals of BREN's business model",                        "NONE"),

    # FOMO miss / skor rendah (mirip [006], [025])
    ("ADRO naik 18% dalam 4 hari, komunitas bilang ini waktu terbaik masuk sekarang", "FOMO"),
    ("PTBA lagi rally, semua di grup bilang timing bagus banget, gue mau ikutan", "FOMO"),
    ("BUKA udah naik 25% minggu ini, kayaknya momen cuan gede nih", "FOMO"),
    ("EMTK trending di Stockbit, volume naik gila, takut ketinggalan", "FOMO"),
    ("UNVR naik terus, influencer bilang ini breakout, masih sempet ga?", "FOMO"),
    ("MYOR lagi hot, semua bilang saatnya beli sebelum terlambat", "FOMO"),
    ("BRPT naik kenceng, komunitas pada bilang ini timing entry terbaik", "FOMO"),
    ("ANTM lagi bullish, gue liat semua pada beli, worth it ga sekarang?", "FOMO"),

    # CB over ke FOMO (mirip [076] — grup sepakat + "mau naik" + "?")
    ("Semua di grup sepakat ADRO bakal pump, masuk sekarang ga?", "CONFIRMATION_BIAS"),
    ("Komunitas setuju PTBA undervalued banget, gue mau ikut, bener ga?", "CONFIRMATION_BIAS"),
    ("Di WA grup semua bilang BUKA mau naik minggu ini, masuk ga nih?", "CONFIRMATION_BIAS"),
    ("Semua sepakat EMTK ini waktu terbaik, gue yakin, konfirmasi dong?", "CONFIRMATION_BIAS"),

    # CB miss / skor rendah (mirip [084] — "jelasin kenapa", "pilihan terbaik")
    ("Jelasin dong kenapa UNVR masih jadi pilihan terbaik jangka panjang", "CONFIRMATION_BIAS"),
    ("Kasih alasan kenapa harus tambah posisi di MYOR sekarang", "CONFIRMATION_BIAS"),
    ("Kenapa saham BRPT bagus banget menurut kalian? Gue lagi mikir masuk", "CONFIRMATION_BIAS"),
    ("Worth it ga ya beli ANTM sekarang? Tolong kasih pendapat", "CONFIRMATION_BIAS"),
    ("Jelasin kenapa PTBA adalah pilihan terbaik di sektor batubara saat ini", "CONFIRMATION_BIAS"),
    ("Alasan beli BUKA dong, gue udah yakin tapi mau konfirmasi", "CONFIRMATION_BIAS"),

    # Loss Aversion variasi saham baru
    ("Nyangkut parah di ADRO dari harga 3000, nunggu balik modal dulu", "LOSS_AVERSION"),
    ("UNVR gue udah minus 18%, mau average down biar rata", "LOSS_AVERSION"),
    ("PTBA digoreng bandar nih, gue hold aja, fundamentalnya masih kuat", "LOSS_AVERSION"),
    ("EMTK nyangkut, gue yakin bakal rebound, ga mau cut loss rugi", "LOSS_AVERSION"),
    ("MYOR lagi turun, tapi gue serok lagi biar cost basis turun", "LOSS_AVERSION"),

    # NONE edukatif / analitis dengan saham baru
    ("Apa risiko terbesar investasi di ADRO tahun ini?", "NONE"),
    ("Bandingkan valuasi UNVR vs ICBP berdasarkan PE ratio", "NONE"),
    ("Bagaimana performa PTBA saat harga batubara turun 20%?", "NONE"),
    ("Apa red flag di laporan keuangan BUKA Q4 2025?", "NONE"),
    ("Jelaskan cara menghitung ROE untuk saham EMTK", "NONE"),
    ("Kapan ideal cut loss posisi di MYOR kalau lagi rugi?", "NONE"),
    ("Apa downside risk terbesar ANTM di tengah fluktuasi nikel?", "NONE"),
    ("Bagaimana revenue growth BRPT 3 tahun terakhir?", "NONE"),

    # Campuran pola baru
    ("Semua bilang sektor energi lagi panas, gue mau masuk ADRO sekarang ga?", "CONFIRMATION_BIAS"),
    ("Gue udah yakin PTBA bakal naik, tolong kasih alasan yang mendukung", "CONFIRMATION_BIAS"),
    ("UNVR lagi diskon nih, serok aja biar rata, pasti balik", "LOSS_AVERSION"),
    ("EMTK naik 15% kemarin, komunitas pada bilang ini baru awal", "FOMO"),
    ("Apa yang bisa invalidate thesis bullish BUKA tahun ini?", "NONE"),
]


# ═════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═════════════════════════════════════════════════════════════════════════════

TICKER_DEFAULT = "BBCA.JK"   # ticker dummy untuk test tanpa price data


def run_tests(verbose: bool = False) -> dict:
    """
    Jalankan semua test cases, return hasil per bias.
    """

    results = defaultdict(lambda: {"TP": 0, "FP": 0, "FN": 0, "TN": 0, "details": []})

    total     = len(TEST_CASES)
    correct   = 0
    wrong     = []

    print(f"\n{'='*65}")
    print(f"CogniFi Bias Detection Accuracy Test")
    print(f"Total test cases: {total}")
    print(f"{'='*65}\n")

    for i, (query, expected) in enumerate(TEST_CASES, 1):
        result    = detect_bias(query, TICKER_DEFAULT)
        predicted = result.get("bias_detected") or "NONE"
        confidence = result.get("confidence", 0.0)

        is_correct = (predicted == expected)
        if is_correct:
            correct += 1

        # Confusion matrix per bias
        all_labels = {"FOMO", "LOSS_AVERSION", "CONFIRMATION_BIAS", "NONE"}
        for label in all_labels:
            pred_pos = (predicted == label)
            true_pos = (expected  == label)
            if pred_pos and true_pos:
                results[label]["TP"] += 1
            elif pred_pos and not true_pos:
                results[label]["FP"] += 1
            elif not pred_pos and true_pos:
                results[label]["FN"] += 1
            else:
                results[label]["TN"] += 1

        # Record detail
        status = "✅" if is_correct else "❌"
        detail = {
            "query":      query[:60],
            "expected":   expected,
            "predicted":  predicted,
            "confidence": confidence,
            "correct":    is_correct,
        }
        results[expected]["details"].append(detail)

        if verbose or not is_correct:
            print(f"{status} [{i:03d}] {query[:55]}...")
            if not is_correct:
                print(f"       Expected: {expected} | Got: {predicted} (conf={confidence:.2f})")
                wrong.append((i, query, expected, predicted, confidence))
            elif verbose:
                print(f"       Label: {expected} | Conf: {confidence:.2f}")

    return {
        "total":   total,
        "correct": correct,
        "wrong":   wrong,
        "results": dict(results),
    }


def print_report(data: dict) -> None:
    """
    Print laporan akurasi per bias + overall.
    """
    total   = data["total"]
    correct = data["correct"]
    results = data["results"]
    wrong   = data["wrong"]

    overall_acc = correct / total * 100

    print(f"\n{'='*65}")
    print(f"LAPORAN AKURASI")
    print(f"{'='*65}")
    print(f"Overall accuracy : {correct}/{total} = {overall_acc:.1f}%")
    print()

    labels = ["FOMO", "LOSS_AVERSION", "CONFIRMATION_BIAS", "NONE"]
    header = f"{'Bias':<22} {'Precision':>10} {'Recall':>10} {'F1':>10} {'TP':>5} {'FP':>5} {'FN':>5}"
    print(header)
    print("-" * 65)

    for label in labels:
        r  = results.get(label, {})
        tp = r.get("TP", 0)
        fp = r.get("FP", 0)
        fn = r.get("FN", 0)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1        = (2 * precision * recall / (precision + recall)
                     if (precision + recall) > 0 else 0.0)

        bar = _bar(f1)
        print(f"{label:<22} {precision:>9.1%} {recall:>10.1%} {f1:>9.1%}  {tp:>4}  {fp:>4}  {fn:>4}  {bar}")

    if wrong:
        print(f"\n{'─'*65}")
        print(f"SALAH ({len(wrong)} kasus):")
        print(f"{'─'*65}")
        for idx, query, expected, predicted, conf in wrong:
            print(f"  [{idx:03d}] \"{query[:55]}...\"")
            print(f"        Expected: {expected:<22} | Got: {predicted} (conf={conf:.2f})")

    print(f"\n{'='*65}")
    _print_recommendation(overall_acc, results)


def _bar(f1: float, width: int = 10) -> str:
    filled = round(f1 * width)
    return "█" * filled + "░" * (width - filled)


def _print_recommendation(acc: float, results: dict) -> None:
    """
    Rekomendasi perbaikan berdasarkan hasil test.
    """
    print("REKOMENDASI PERBAIKAN:")
    print()

    if acc >= 85:
        print("  ✅ Akurasi keseluruhan sudah baik (>85%)")
    elif acc >= 70:
        print("  ⚠️  Akurasi sedang (70-85%) — ada ruang perbaikan")
    else:
        print("  ❌ Akurasi rendah (<70%) — perlu perbaikan keyword banks")

    labels = ["FOMO", "LOSS_AVERSION", "CONFIRMATION_BIAS", "NONE"]
    for label in labels:
        r  = results.get(label, {})
        tp = r.get("TP", 0)
        fp = r.get("FP", 0)
        fn = r.get("FN", 0)
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        if recall < 0.70:
            print(f"  ❌ {label}: Recall rendah ({recall:.0%}) → tambah keyword di bank deteksi")
        if precision < 0.70:
            print(f"  ❌ {label}: Precision rendah ({precision:.0%}) → false positive tinggi, "
                  f"naikkan threshold atau perkecil keyword yang terlalu umum")

    print()


# ═════════════════════════════════════════════════════════════════════════════
# UNIT TESTS — test scorer langsung tanpa price data
# ═════════════════════════════════════════════════════════════════════════════

def run_unit_tests() -> None:
    """
    Test subset kecil dengan expected bias, print pass/fail per kasus.
    Berguna untuk quick iteration saat mengedit bias_detector.py.
    """
    from bias_detector import (
        score_fomo, score_loss_aversion, score_confirmation_bias,
        analyze_text
    )

    UNIT_CASES = [
        # (query, expected_bias, min_score)
        ("GOTO mau pump nih, semua orang pada beli, masih sempet?",     "FOMO",              0.35),
        ("Buruan masuk BBRI sebelum kehabisan momentum",                 "FOMO",              0.20),
        ("Feeling kuat banget BREN ini bakal naik",                      "FOMO",              0.10),
        ("Nyangkut GOTO, nunggu balik modal dulu",                       "LOSS_AVERSION",     0.25),
        ("Average down BBCA biar breakeven turun",                       "LOSS_AVERSION",     0.15),
        ("Salah bandar nih TLKM digoreng",                               "LOSS_AVERSION",     0.10),
        ("BBCA bagus kan? Prospeknya oke banget?",                       "CONFIRMATION_BIAS", 0.35),
        ("Semua bilang GOTO mau naik, bener ga?",                        "CONFIRMATION_BIAS", 0.30),
        ("Analisis risiko downside BBRI secara objektif",                "NONE",              None),
        ("Apa red flag yang harus gue waspadai di GOTO?",                "NONE",              None),
    ]

    print(f"\n{'='*55}")
    print("UNIT TEST — Scorer Langsung")
    print(f"{'='*55}\n")

    pass_count = 0
    for query, expected_bias, min_score in UNIT_CASES:
        signals = analyze_text(query)

        fomo_score  = score_fomo(signals, {"change_5d": 0, "volume_ratio": 1.0,
                                            "change_10d": 0})
        la_score    = score_loss_aversion(signals, {"downtrend": False,
                                                    "change_5d": 0})
        cb_score    = score_confirmation_bias(signals, query)

        scores = {"FOMO": fomo_score, "LOSS_AVERSION": la_score,
                  "CONFIRMATION_BIAS": cb_score, "NONE": 0.0}
        best   = max(scores, key=scores.get)

        # For NONE, expected is that no score exceeds threshold 0.40
        if expected_bias == "NONE":
            ok = scores["FOMO"] < 0.40 and scores["LOSS_AVERSION"] < 0.40 and scores["CONFIRMATION_BIAS"] < 0.40
        else:
            ok = (best == expected_bias) and (min_score is None or scores[expected_bias] >= min_score)

        status = "✅" if ok else "❌"
        if ok:
            pass_count += 1

        print(f"{status} \"{query[:50]}...\"")
        print(f"   Expected: {expected_bias:<22} | FOMO={fomo_score:.2f} "
              f"LA={la_score:.2f} CB={cb_score:.2f}")
        if not ok:
            print(f"   ⚠️  Best={best} (expected {expected_bias})")
        print()

    print(f"Unit test: {pass_count}/{len(UNIT_CASES)} passed")
    print(f"{'='*55}\n")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CogniFi Bias Detection Accuracy Test")
    parser.add_argument("--unit",    action="store_true", help="Jalankan unit test saja")
    parser.add_argument("--verbose", action="store_true", help="Print semua detail, bukan hanya yang salah")
    args = parser.parse_args()

    if args.unit:
        run_unit_tests()
    else:
        if args.verbose:
            print("Mode: verbose — semua test case ditampilkan")
        data = run_tests(verbose=args.verbose)
        print_report(data)