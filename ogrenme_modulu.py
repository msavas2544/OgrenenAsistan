"""
Öğrenme Modülü
Bu modül asistanın öğrenme yeteneklerini sağlar: bilgi depolama, analiz, bağlantı kurma
"""

import json
import datetime
from typing import Dict, List, Any, Optional
from dil_isleme import TurkceDilIsleme

class OgrenmeModulu:
    def __init__(self, 
                 bilgi_tabani_dosya: str = "veri/bilgi_tabani.json",
                 ogrenme_gecmisi_dosya: str = "veri/ogrenme_gecmisi.json",
                 ayarlar_dosya: str = "yapilandirma/ayarlar.json"):
        
        self.bilgi_tabani_dosya = bilgi_tabani_dosya
        self.ogrenme_gecmisi_dosya = ogrenme_gecmisi_dosya
        self.ayarlar_dosya = ayarlar_dosya
        
        # Dil işleme modülünü başlat
        self.dil_isleme = TurkceDilIsleme()
        
        # Verileri yükle
        self.bilgi_tabani = self._yukle_json(bilgi_tabani_dosya)
        self.ogrenme_gecmisi = self._yukle_json(ogrenme_gecmisi_dosya)
        self.ayarlar = self._yukle_json(ayarlar_dosya)
        
        # Öğrenme parametreleri
        self.ogrenme_hizi = self.ayarlar.get("ogrenme_hizi", 0.8)
        self.ogrenme_esigi = self.ayarlar.get("ogrenme_esigi", 0.7)
        self.benzerlik_esigi = self.ayarlar.get("benzerlik_esigi", 0.6)
    
    def _yukle_json(self, dosya_yolu: str) -> Dict:
        """JSON dosyasını yükle"""
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Dosya bulunamadı: {dosya_yolu}")
            return {}
        except json.JSONDecodeError:
            print(f"⚠️ JSON formatı hatalı: {dosya_yolu}")
            return {}
    
    def _kaydet_json(self, veri: Dict, dosya_yolu: str) -> bool:
        """JSON dosyasına kaydet"""
        try:
            with open(dosya_yolu, 'w', encoding='utf-8') as f:
                json.dump(veri, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Kaydetme hatası {dosya_yolu}: {e}")
            return False
    
    def yeni_bilgi_ogren(self, kullanici_mesaj: str, asistan_cevap: str, konu: str = None) -> bool:
        """Yeni bilgiyi öğren ve sakla"""
        try:
            # Konuyu belirle
            if not konu:
                konu = self.dil_isleme.konu_belirle(kullanici_mesaj)
            
            # Anahtar kelimeleri çıkart
            anahtar_kelimeler = self.dil_isleme.anahtar_kelimeleri_cikart(kullanici_mesaj)
            
            # Benzersiz ID oluştur
            bilgi_id = f"{konu}_{len(self.bilgi_tabani.get('bilgiler', {}))}"
            
            # Yeni bilgi objesi oluştur
            yeni_bilgi = {
                "id": bilgi_id,
                "kullanici_mesaj": kullanici_mesaj,
                "asistan_cevap": asistan_cevap,
                "konu": konu,
                "anahtar_kelimeler": anahtar_kelimeler,
                "ogrenme_tarihi": datetime.datetime.now().isoformat(),
                "kullanim_sayisi": 1,
                "basari_skoru": 0.0,
                "guncelleme_tarihi": datetime.datetime.now().isoformat()
            }
            
            # Bilgi tabanına ekle
            if "bilgiler" not in self.bilgi_tabani:
                self.bilgi_tabani["bilgiler"] = {}
            
            self.bilgi_tabani["bilgiler"][bilgi_id] = yeni_bilgi
            
            # Konu kategorisine ekle
            if "konular" not in self.bilgi_tabani:
                self.bilgi_tabani["konular"] = {}
            
            if konu not in self.bilgi_tabani["konular"]:
                self.bilgi_tabani["konular"][konu] = []
            
            self.bilgi_tabani["konular"][konu].append(bilgi_id)
            
            # İstatistikleri güncelle
            self._istatistikleri_guncelle()
            
            # Öğrenme geçmişini kaydet
            self._ogrenme_gecmisine_ekle("yeni_bilgi", bilgi_id, True)
            
            # Dosyaya kaydet
            if self.ayarlar.get("otomatik_kaydet", True):
                self._kaydet_json(self.bilgi_tabani, self.bilgi_tabani_dosya)
                self._kaydet_json(self.ogrenme_gecmisi, self.ogrenme_gecmisi_dosya)
            
            return True
            
        except Exception as e:
            print(f"❌ Öğrenme hatası: {e}")
            self._ogrenme_gecmisine_ekle("yeni_bilgi", "hata", False)
            return False
    
    def benzer_bilgi_bul(self, kullanici_mesaj: str, limit: int = 5) -> List[Dict]:
        """Kullanıcı mesajına benzer bilgileri bul"""
        benzer_bilgiler = []
        
        if "bilgiler" not in self.bilgi_tabani:
            return benzer_bilgiler
        
        for bilgi_id, bilgi in self.bilgi_tabani["bilgiler"].items():
            # Benzerlik hesapla
            benzerlik = self.dil_isleme.benzerlik_hesapla(
                kullanici_mesaj, 
                bilgi["kullanici_mesaj"]
            )
            
            # Eşiği geçenler
            if benzerlik >= self.benzerlik_esigi:
                bilgi_kopyasi = bilgi.copy()
                bilgi_kopyasi["benzerlik_skoru"] = benzerlik
                benzer_bilgiler.append(bilgi_kopyasi)
        
        # Benzerlik skoruna göre sırala
        benzer_bilgiler.sort(key=lambda x: x["benzerlik_skoru"], reverse=True)
        
        return benzer_bilgiler[:limit]
    
    def en_iyi_cevap_bul(self, kullanici_mesaj: str) -> Optional[str]:
        """Kullanıcı mesajı için en iyi cevabı bul"""
        benzer_bilgiler = self.benzer_bilgi_bul(kullanici_mesaj, 1)
        
        if benzer_bilgiler and benzer_bilgiler[0]["benzerlik_skoru"] > 0.8:
            # En benzer bilgiyi kullan
            en_iyi_bilgi = benzer_bilgiler[0]
            
            # Kullanım sayısını artır
            bilgi_id = en_iyi_bilgi["id"]
            if bilgi_id in self.bilgi_tabani["bilgiler"]:
                self.bilgi_tabani["bilgiler"][bilgi_id]["kullanim_sayisi"] += 1
                self.bilgi_tabani["bilgiler"][bilgi_id]["guncelleme_tarihi"] = datetime.datetime.now().isoformat()
            
            return en_iyi_bilgi["asistan_cevap"]
        
        return None
    
    def konu_bazli_bilgi_getir(self, konu: str, limit: int = 3) -> List[Dict]:
        """Belirli bir konuya ait bilgileri getir"""
        if "konular" not in self.bilgi_tabani or konu not in self.bilgi_tabani["konular"]:
            return []
        
        bilgi_idleri = self.bilgi_tabani["konular"][konu]
        bilgiler = []
        
        for bilgi_id in bilgi_idleri[:limit]:
            if bilgi_id in self.bilgi_tabani["bilgiler"]:
                bilgiler.append(self.bilgi_tabani["bilgiler"][bilgi_id])
        
        return bilgiler
    
    def bilgi_guncelle(self, bilgi_id: str, yeni_cevap: str) -> bool:
        """Mevcut bilgiyi güncelle"""
        if "bilgiler" not in self.bilgi_tabani or bilgi_id not in self.bilgi_tabani["bilgiler"]:
            return False
        
        self.bilgi_tabani["bilgiler"][bilgi_id]["asistan_cevap"] = yeni_cevap
        self.bilgi_tabani["bilgiler"][bilgi_id]["guncelleme_tarihi"] = datetime.datetime.now().isoformat()
        
        # Kaydet
        if self.ayarlar.get("otomatik_kaydet", True):
            self._kaydet_json(self.bilgi_tabani, self.bilgi_tabani_dosya)
        
        return True
    
    def _istatistikleri_guncelle(self):
        """Bilgi tabanı istatistiklerini güncelle"""
        if "istatistikler" not in self.bilgi_tabani:
            self.bilgi_tabani["istatistikler"] = {}
        
        self.bilgi_tabani["istatistikler"]["toplam_bilgi"] = len(self.bilgi_tabani.get("bilgiler", {}))
        self.bilgi_tabani["istatistikler"]["son_guncelleme"] = datetime.datetime.now().isoformat()
        self.bilgi_tabani["istatistikler"]["version"] = "1.0"
    
    def _ogrenme_gecmisine_ekle(self, islem_tipi: str, bilgi_id: str, basarili: bool):
        """Öğrenme geçmişine yeni kayıt ekle"""
        if "ogrenme_kayitlari" not in self.ogrenme_gecmisi:
            self.ogrenme_gecmisi["ogrenme_kayitlari"] = []
        
        kayit = {
            "tarih": datetime.datetime.now().isoformat(),
            "islem_tipi": islem_tipi,
            "bilgi_id": bilgi_id,
            "basarili": basarili
        }
        
        self.ogrenme_gecmisi["ogrenme_kayitlari"].append(kayit)
        
        # İstatistikleri güncelle
        if basarili:
            self.ogrenme_gecmisi["basarili_ogrenmeler"] = self.ogrenme_gecmisi.get("basarili_ogrenmeler", 0) + 1
        else:
            self.ogrenme_gecmisi["basarisiz_ogrenmeler"] = self.ogrenme_gecmisi.get("basarisiz_ogrenmeler", 0) + 1
        
        self.ogrenme_gecmisi["son_ogrenme"] = datetime.datetime.now().isoformat()
    
    def ogrenme_istatistikleri_getir(self) -> Dict:
        """Öğrenme istatistiklerini getir"""
        toplam_bilgi = len(self.bilgi_tabani.get("bilgiler", {}))
        basarili = self.ogrenme_gecmisi.get("basarili_ogrenmeler", 0)
        basarisiz = self.ogrenme_gecmisi.get("basarisiz_ogrenmeler", 0)
        toplam_ogrenme = basarili + basarisiz
        
        return {
            "toplam_bilgi": toplam_bilgi,
            "basarili_ogrenmeler": basarili,
            "basarisiz_ogrenmeler": basarisiz,
            "basari_orani": (basarili / toplam_ogrenme * 100) if toplam_ogrenme > 0 else 0,
            "son_ogrenme": self.ogrenme_gecmisi.get("son_ogrenme", "Henüz öğrenme yok")
        }
    
    def verileri_kaydet(self):
        """Tüm verileri manuel olarak kaydet"""
        bilgi_kaydedildi = self._kaydet_json(self.bilgi_tabani, self.bilgi_tabani_dosya)
        gecmis_kaydedildi = self._kaydet_json(self.ogrenme_gecmisi, self.ogrenme_gecmisi_dosya)
        
        return bilgi_kaydedildi and gecmis_kaydedildi
