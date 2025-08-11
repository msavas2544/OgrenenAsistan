"""
Öğrenen Asistan Test Scripti
Asistanın özelliklerini otomatik olarak test eder
"""

import sys
import time
from dil_isleme import TurkceDilIsleme
from ogrenme_modulu import OgrenmeModulu

def test_dil_isleme():
    """Dil işleme modülünü test et"""
    print("🧪 Dil İşleme Modülü Test Ediliyor...\n")
    
    dil = TurkceDilIsleme()
    
    test_metinleri = [
        "Merhaba, nasılsın?",
        "Python hakkında bilgi verebilir misin?",
        "Bugün hava çok güzel!",
        "Teşekkürler, görüşürüz!"
    ]
    
    for metin in test_metinleri:
        print(f"📝 Test Metni: '{metin}'")
        print(f"   🧹 Temiz: {dil.temizle_metin(metin)}")
        print(f"   📚 Kelimeler: {dil.kelimelere_ayir(metin)}")
        print(f"   ❓ Soru mu: {dil.soru_mu(metin)}")
        print(f"   � Selamlama: {dil.selamlasma_mi(metin)}")
        print(f"   💭 Duygu: {dil.duygu_analizi(metin)}")
        print(f"   🎯 Konu: {dil.konu_belirle(metin)}")
        print("-" * 40)

def test_ogrenme_modulu():
    """Öğrenme modülünü test et"""
    print("\n🧠 Öğrenme Modülü Test Ediliyor...\n")
    
    ogrenme = OgrenmeModulu()
    
    # Test öğrenmeleri
    test_veriler = [
        ("Python nedir?", "Python yüksek seviyeli bir programlama dilidir.", "teknoloji"),
        ("Nasıl öğrenebilirim?", "Sürekli pratik yaparak ve merak ederek öğrenebilirsin.", "eğitim"),
        ("Bugün nasılsın?", "İyiyim, teşekkür ederim! Sen nasılsın?", "kişisel")
    ]
    
    for soru, cevap, konu in test_veriler:
        print(f"📚 Öğrenilen: '{soru}' -> '{cevap}' [{konu}]")
        basarili = ogrenme.yeni_bilgi_ogren(soru, cevap, konu)
        print(f"   ✅ Başarılı: {basarili}")
    
    # Benzer bilgi arama testi
    print(f"\n🔍 Benzer bilgi arama testi:")
    benzer = ogrenme.benzer_bilgi_bul("Python programlama dili nedir?")
    if benzer:
        print(f"   💡 Bulundu: {benzer[0]['asistan_cevap']}")
        print(f"   📊 Benzerlik: {benzer[0]['benzerlik_skoru']:.2f}")
    else:
        print("   ❌ Benzer bilgi bulunamadı")
    
    # İstatistikler
    stats = ogrenme.ogrenme_istatistikleri_getir()
    print(f"\n📊 Öğrenme İstatistikleri:")
    print(f"   🧠 Toplam Bilgi: {stats['toplam_bilgi']}")
    print(f"   ✅ Başarılı: {stats['basarili_ogrenmeler']}")
    print(f"   � Başarı Oranı: %{stats['basari_orani']:.1f}")

def main():
    """Ana test fonksiyonu"""
    print("🚀 Öğrenen Asistan - Kapsamlı Test Süreci\n")
    print("=" * 50)
    
    try:
        # Dil işleme testleri
        test_dil_isleme()
        
        # Öğrenme modülü testleri  
        test_ogrenme_modulu()
        
        print("\n🎉 Tüm testler başarıyla tamamlandı!")
        print("✅ Öğrenen Asistan kullanıma hazır!")
        
    except Exception as e:
        print(f"❌ Test sırasında hata: {e}")
        return False
        
    return True

if __name__ == "__main__":
    main()
