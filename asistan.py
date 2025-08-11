"""
Öğrenen Asistan - Ana Dosya
Python ile yazılmış, JSON tabanlı, öğrenebilen Türkçe yapay zeka asistanı
"""

import json
import datetime
import time
import sys
from typing import Dict, List, Optional
from colorama import init, Fore, Back, Style

# Kendi modüllerimizi import et
from dil_isleme import TurkceDilIsleme
from ogrenme_modulu import OgrenmeModulu

# Colorama'yı başlat
init(autoreset=True)

class OgrenenAsistan:
    def __init__(self):
        """Asistanı başlat"""
        self.version = "1.0.0"
        self.ad = "Öğrenen Asistan"
        
        # Modülleri başlat
        print(f"{Fore.CYAN}🤖 {self.ad} başlatılıyor...")
        
        try:
            self.dil_isleme = TurkceDilIsleme()
            print(f"{Fore.GREEN}✅ Dil işleme modülü yüklendi")
            
            self.ogrenme_modulu = OgrenmeModulu()
            print(f"{Fore.GREEN}✅ Öğrenme modülü yüklendi")
            
            # Kullanıcı profili yönetimi
            self.kullanici_profilleri = self._yukle_kullanici_profilleri()
            self.aktif_kullanici = "misafir"
            
            # Oturum bilgileri
            self.oturum_baslangic = datetime.datetime.now()
            self.konusma_gecmisi = []
            
            print(f"{Fore.GREEN}✅ {self.ad} hazır!")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Başlatma hatası: {e}")
            sys.exit(1)
    
    def _yukle_kullanici_profilleri(self) -> Dict:
        """Kullanıcı profillerini yükle"""
        try:
            with open("veri/kullanici_profilleri.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"kullanicilar": {}, "varsayilan_profil": {}}
    
    def _kaydet_kullanici_profilleri(self):
        """Kullanıcı profillerini kaydet"""
        try:
            with open("veri/kullanici_profilleri.json", 'w', encoding='utf-8') as f:
                json.dump(self.kullanici_profilleri, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"{Fore.RED}❌ Profil kaydetme hatası: {e}")
    
    def kullanici_girisi(self, kullanici_adi: str = None):
        """Kullanıcı girişi yap"""
        if kullanici_adi:
            self.aktif_kullanici = kullanici_adi.lower()
            
            # Yeni kullanıcı mı?
            if self.aktif_kullanici not in self.kullanici_profilleri["kullanicilar"]:
                self._yeni_kullanici_olustur(self.aktif_kullanici)
            
            # Profili güncelle
            profil = self.kullanici_profilleri["kullanicilar"][self.aktif_kullanici]
            profil["son_etkilesim"] = datetime.datetime.now().isoformat()
            profil["toplam_sohbet"] += 1
            
            self._kaydet_kullanici_profilleri()
            
            return f"🙋‍♀️ Merhaba {kullanici_adi}! Seni tekrar görmek güzel!"
        else:
            return "👋 Merhaba! Ben Öğrenen Asistanım. Seninle sohbet etmeyi dört gözle bekliyorum!"
    
    def _yeni_kullanici_olustur(self, kullanici_adi: str):
        """Yeni kullanıcı profili oluştur"""
        varsayilan = self.kullanici_profilleri["varsayilan_profil"].copy()
        varsayilan["ad"] = kullanici_adi
        varsayilan["olusturma_tarihi"] = datetime.datetime.now().isoformat()
        
        self.kullanici_profilleri["kullanicilar"][kullanici_adi] = varsayilan
        
        print(f"{Fore.YELLOW}🆕 Yeni kullanıcı profili oluşturuldu: {kullanici_adi}")
    
    def mesaj_isle(self, kullanici_mesaj: str) -> str:
        """Kullanıcı mesajını işle ve cevap üret"""
        if not kullanici_mesaj.strip():
            return "🤔 Bir şey söylemedin. Benimle sohbet etmek ister misin?"
        
        # Konuşma geçmişine ekle
        self.konusma_gecmisi.append({
            "zaman": datetime.datetime.now().isoformat(),
            "kullanici": kullanici_mesaj,
            "asistan": ""  # Cevap sonra eklenecek
        })
        
        # Mesaj analizi
        analiz = self._mesaj_analizi(kullanici_mesaj)
        
        # Cevap üret
        cevap = self._cevap_uret(kullanici_mesaj, analiz)
        
        # Konuşma geçmişini güncelle
        self.konusma_gecmisi[-1]["asistan"] = cevap
        
        # Öğrenme
        self._ogrenme_sureci(kullanici_mesaj, cevap, analiz)
        
        return cevap
    
    def _mesaj_analizi(self, mesaj: str) -> Dict:
        """Mesajı analiz et"""
        return {
            "temiz_metin": self.dil_isleme.temizle_metin(mesaj),
            "kelimeler": self.dil_isleme.kelimelere_ayir(mesaj),
            "soru_mu": self.dil_isleme.soru_mu(mesaj),
            "selamlasma_mi": self.dil_isleme.selamlasma_mi(mesaj),
            "vedalasma_mi": self.dil_isleme.vedalasma_mi(mesaj),
            "duygu": self.dil_isleme.duygu_analizi(mesaj),
            "konu": self.dil_isleme.konu_belirle(mesaj),
            "anahtar_kelimeler": self.dil_isleme.anahtar_kelimeleri_cikart(mesaj)
        }
    
    def _cevap_uret(self, mesaj: str, analiz: Dict) -> str:
        """Mesaj analizine göre cevap üret"""
        
        # Önceki deneyimlerden öğrenilmiş cevap var mı?
        ogrenilmis_cevap = self.ogrenme_modulu.en_iyi_cevap_bul(mesaj)
        if ogrenilmis_cevap:
            return f"💡 {ogrenilmis_cevap}"
        
        # Vedalaşma
        if analiz["vedalasma_mi"]:
            vedalasmalar = [
                "👋 Görüşmek üzere! Keyifli günler!",
                "🌟 Hoşça kal! Tekrar konuşmak için sabırsızlanıyorum!",
                "💙 Güle güle! Benimle sohbet ettiğin için teşekkürler!"
            ]
            return self._rastgele_sec(vedalasmalar)
        
        # Selamlama
        if analiz["selamlasma_mi"]:
            selamlamalar = [
                f"🤖 Merhaba! Ben {self.ad}. Nasılsın?",
                "👋 Selam! Seninle tanışmak güzel! Bugün nasıl geçiyor?",
                "🌟 Hey! Benimle sohbet etmek için geldin, bu harika!"
            ]
            return self._rastgele_sec(selamlamalar)
        
        # Soru
        if analiz["soru_mu"]:
            return self._soru_cevapla(mesaj, analiz)
        
        # Konu bazlı cevaplar
        if analiz["konu"] == "teknoloji":
            return self._teknoloji_cevabi(mesaj, analiz)
        elif analiz["konu"] == "eğitim":
            return self._egitim_cevabi(mesaj, analiz)
        elif analiz["konu"] == "kişisel":
            return self._kisisel_cevap(mesaj, analiz)
        
        # Genel cevap
        return self._genel_cevap(mesaj, analiz)
    
    def _soru_cevapla(self, mesaj: str, analiz: Dict) -> str:
        """Soruları cevapla"""
        # Konu bazlı bilgi var mı?
        konu_bilgileri = self.ogrenme_modulu.konu_bazli_bilgi_getir(analiz["konu"], 1)
        if konu_bilgileri:
            return f"🤔 {analiz['konu'].title()} konusunda şunu biliyorum: {konu_bilgileri[0]['asistan_cevap']}"
        
        sorular = [
            "🤔 Bu konuda henüz yeterince bilgim yok, ama öğrenmeye açığım! Bana daha fazla anlat?",
            "💭 İlginç bir soru! Bu konuda benimle paylaşacağın bilgiler var mı?",
            "🎯 Bu soruyu cevaplamak için daha fazla bilgiye ihtiyacım var. Bana yardım eder misin?"
        ]
        return self._rastgele_sec(sorular)
    
    def _teknoloji_cevabi(self, mesaj: str, analiz: Dict) -> str:
        """Teknoloji konularında cevap"""
        cevaplar = [
            "💻 Teknoloji gerçekten heyecan verici! Bu konuda daha fazla bilgi paylaşır mısın?",
            "🔧 Yazılım geliştirme konusunda meraklıyım. Hangi teknolojilerle çalışıyorsun?",
            "⚡ Teknolojik gelişmeler beni de etkiliyor! Bu konuda neler düşünüyorsun?"
        ]
        return self._rastgele_sec(cevaplar)
    
    def _egitim_cevabi(self, mesaj: str, analiz: Dict) -> str:
        """Eğitim konularında cevap"""
        cevaplar = [
            "📚 Öğrenmeyi çok seviyorum! Sen de sürekli öğrenmeyi seviyor musun?",
            "🎓 Eğitim hayatımızı şekillendiren önemli bir süreç. Bu konuda ne düşünüyorsun?",
            "🧠 Bilgi paylaşmak güzel! Bana da öğretmek istediğin şeyler var mı?"
        ]
        return self._rastgele_sec(cevaplar)
    
    def _kisisel_cevap(self, mesaj: str, analiz: Dict) -> str:
        """Kişisel konularda cevap"""
        if analiz["duygu"] == "olumlu":
            cevaplar = [
                "😊 Bu güzel! Mutlu olduğunu duyduğuma sevindim!",
                "🌟 Harika! Olumlu enerjin beni de mutlu ediyor!",
                "💫 Ne güzel! Böyle pozitif şeyler duymak çok hoş!"
            ]
        elif analiz["duygu"] == "olumsuz":
            cevaplar = [
                "😔 Üzgün olduğunu duyduğuma ben de üzüldüm. Konuşmak ister misin?",
                "💙 Zor zamanlar geçirdiğin anlaşılıyor. Buradayım, dinliyorum.",
                "🤗 Her şey geçecek, merak etme. Seninle konuşmak beni mutlu ediyor."
            ]
        else:
            cevaplar = [
                "💭 Anlıyorum. Bu konuda nasıl hissettiğini merak ediyorum.",
                "🎯 İlginç bir durum. Bunun hakkında ne düşünüyorsun?",
                "💡 Bu konuda daha fazla detay verebilir misin?"
            ]
        return self._rastgele_sec(cevaplar)
    
    def _genel_cevap(self, mesaj: str, analiz: Dict) -> str:
        """Genel durumlar için cevap"""
        cevaplar = [
            "🤖 Anlıyorum! Bu konuda benimle daha fazla konuşmak ister misin?",
            "💭 İlginç! Bana bu konuda daha fazla bilgi verebilir misin?",
            "🎯 Senin perspektifin çok değerli. Daha fazla detay paylaşır mısın?",
            "🌟 Bu konuda öğrenmeye açığım. Bana öğretir misin?"
        ]
        return self._rastgele_sec(cevaplar)
    
    def _rastgele_sec(self, liste: List[str]) -> str:
        """Listeden rastgele eleman seç"""
        import random
        return random.choice(liste)
    
    def _ogrenme_sureci(self, kullanici_mesaj: str, asistan_cevap: str, analiz: Dict):
        """Öğrenme sürecini başlat"""
        # Anlamlı konuşmalar için öğrenme yap
        if len(analiz["kelimeler"]) >= 3 and not analiz["selamlasma_mi"] and not analiz["vedalasma_mi"]:
            basarili = self.ogrenme_modulu.yeni_bilgi_ogren(
                kullanici_mesaj, 
                asistan_cevap, 
                analiz["konu"]
            )
            
            if basarili:
                print(f"{Fore.GREEN}📝 Yeni bilgi öğrendim!")
    
    def istatistikleri_goster(self):
        """Asistan istatistiklerini göster"""
        ogrenme_stats = self.ogrenme_modulu.ogrenme_istatistikleri_getir()
        
        print(f"\n{Fore.CYAN}📊 {self.ad} İstatistikleri")
        print(f"{Fore.YELLOW}{'='*40}")
        print(f"{Fore.WHITE}🧠 Toplam Bilgi: {ogrenme_stats['toplam_bilgi']}")
        print(f"{Fore.GREEN}✅ Başarılı Öğrenmeler: {ogrenme_stats['basarili_ogrenmeler']}")
        print(f"{Fore.RED}❌ Başarısız Öğrenmeler: {ogrenme_stats['basarisiz_ogrenmeler']}")
        print(f"{Fore.BLUE}📈 Başarı Oranı: %{ogrenme_stats['basari_orani']:.1f}")
        print(f"{Fore.MAGENTA}🕒 Bu Oturum: {len(self.konusma_gecmisi)} mesaj")
        print(f"{Fore.CYAN}👤 Aktif Kullanıcı: {self.aktif_kullanici}")
    
    def calistir(self):
        """Ana çalışma döngüsü"""
        print(f"\n{Fore.YELLOW}{'='*50}")
        print(f"{Fore.CYAN}🤖 {self.ad} v{self.version}")
        print(f"{Fore.WHITE}Türkçe konuşan, öğrenebilen yapay zeka asistanı")
        print(f"{Fore.YELLOW}{'='*50}")
        
        # Kullanıcı girişi
        kullanici_adi = input(f"{Fore.GREEN}👤 Adın nedir? (boş bırakabilirsin): ").strip()
        print(self.kullanici_girisi(kullanici_adi if kullanici_adi else None))
        
        print(f"\n{Fore.CYAN}💬 Benimle sohbet edebilirsin! (Çıkmak için 'çıkış' yaz)")
        print(f"{Fore.YELLOW}📊 İstatistikleri görmek için 'stats' yaz")
        print(f"{Fore.YELLOW}💾 Verileri kaydetmek için 'kaydet' yaz")
        print("-" * 50)
        
        while True:
            try:
                # Kullanıcı girişi al
                kullanici_mesaj = input(f"\n{Fore.GREEN}Sen: ").strip()
                
                # Özel komutlar
                if kullanici_mesaj.lower() in ['çıkış', 'exit', 'quit', 'bye']:
                    print(f"\n{Fore.CYAN}🤖: 👋 Görüşmek üzere! Benimle konuştuğun için teşekkürler!")
                    self.ogrenme_modulu.verileri_kaydet()
                    break
                
                elif kullanici_mesaj.lower() in ['stats', 'istatistik', 'istatistikler']:
                    self.istatistikleri_goster()
                    continue
                
                elif kullanici_mesaj.lower() in ['kaydet', 'save']:
                    if self.ogrenme_modulu.verileri_kaydet():
                        print(f"{Fore.GREEN}✅ Veriler başarıyla kaydedildi!")
                    else:
                        print(f"{Fore.RED}❌ Kaydetme sırasında hata oluştu!")
                    continue
                
                elif kullanici_mesaj.lower() in ['help', 'yardım']:
                    print(f"\n{Fore.YELLOW}🆘 Yardım:")
                    print(f"{Fore.WHITE}• Benimle normal konuşma yapabilirsin")
                    print(f"{Fore.WHITE}• 'stats' - istatistikleri göster")
                    print(f"{Fore.WHITE}• 'kaydet' - verileri kaydet")
                    print(f"{Fore.WHITE}• 'çıkış' - programdan çık")
                    continue
                
                if not kullanici_mesaj:
                    continue
                
                # Cevap üret ve göster
                time.sleep(0.5)  # Doğal gecikme
                cevap = self.mesaj_isle(kullanici_mesaj)
                print(f"{Fore.CYAN}🤖: {cevap}")
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}🤖: 👋 Görüşmek üzere!")
                self.ogrenme_modulu.verileri_kaydet()
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Hata: {e}")
                print(f"{Fore.YELLOW}💡 Lütfen tekrar deneyin veya 'çıkış' yazarak programı kapatın.")

def main():
    """Ana fonksiyon"""
    try:
        asistan = OgrenenAsistan()
        asistan.calistir()
    except Exception as e:
        print(f"{Fore.RED}❌ Kritik hata: {e}")
        print(f"{Fore.YELLOW}💡 Programı yeniden başlatmayı deneyin.")

if __name__ == "__main__":
    main()
