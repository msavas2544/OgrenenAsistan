"""
Öğrenen Asistan - Basit Kullanım Örneği
Bu dosya asistanın nasıl kullanılacağını gösterir
"""

from dil_isleme import TurkceDilIsleme
from ogrenme_modulu import OgrenmeModulu

def basit_kullanim():
    """Asistanın temel özelliklerini göster"""
    print("🤖 Öğrenen Asistan - Basit Kullanım Örneği\n")
    
    # 1. Dil işleme modülünü kullan
    print("1️⃣ Dil İşleme Özellikleri:")
    dil = TurkceDilIsleme()
    
    metin = "Merhaba! Python öğrenmek istiyorum."
    print(f"   📝 Orijinal: '{metin}'")
    print(f"   🧹 Temiz: '{dil.temizle_metin(metin)}'")
    print(f"   ❓ Soru mu: {dil.soru_mu(metin)}")
    print(f"   👋 Selamlama: {dil.selamlasma_mi(metin)}")
    print(f"   🎯 Konu: {dil.konu_belirle(metin)}")
    
    # 2. Öğrenme modülünü kullan
    print("\n2️⃣ Öğrenme Özellikleri:")
    ogrenme = OgrenmeModulu()
    
    # Yeni bilgi öğret
    soru = "Python nasıl öğrenilir?"
    cevap = "Python öğrenmek için önce temel syntax'ı öğren, sonra projeler yap!"
    
    print(f"   📚 Öğretilen: '{soru}' -> '{cevap}'")
    basarili = ogrenme.yeni_bilgi_ogren(soru, cevap, "eğitim")
    print(f"   ✅ Öğrenme durumu: {basarili}")
    
    # Benzer soru sor
    benzer_soru = "Python öğrenme yöntemleri nedir?"
    bulunan = ogrenme.en_iyi_cevap_bul(benzer_soru)
    print(f"   🔍 Benzer soru: '{benzer_soru}'")
    print(f"   💡 Bulunan cevap: '{bulunan}'")
    
    # 3. İstatistikler
    print("\n3️⃣ İstatistikler:")
    stats = ogrenme.ogrenme_istatistikleri_getir()
    for anahtar, deger in stats.items():
        print(f"   📊 {anahtar}: {deger}")

def interaktif_ornek():
    """İnteraktif kullanım örneği"""
    print("\n🎯 İnteraktif Örnek (Simülasyon):")
    
    # Simüle edilmiş konuşma
    konusmalar = [
        ("Kullanıcı", "Merhaba!"),
        ("Asistan", "👋 Merhaba! Ben Öğrenen Asistan. Nasılsın?"),
        ("Kullanıcı", "Python hakkında bilgi verebilir misin?"),
        ("Asistan", "💻 Tabii! Python hakkında ne öğrenmek istiyorsun?"),
        ("Kullanıcı", "Python web geliştirme için nasıl?"),
        ("Asistan", "🌐 Python web geliştirme için harika! Django ve Flask gibi framework'ler var."),
    ]
    
    for konusan, mesaj in konusmalar:
        if konusan == "Kullanıcı":
            print(f"👤 {konusan}: {mesaj}")
        else:
            print(f"🤖 {konusan}: {mesaj}")

if __name__ == "__main__":
    basit_kullanim()
    interaktif_ornek()
    print("\n🎉 Basit kullanım örneği tamamlandı!")
    print("💡 Tam sürüm için 'python asistan.py' komutunu çalıştırın!")
