"""
Türkçe Dil İşleme Modülü
Bu modül Türkçe metinlerin işlenmesi, analizi ve anlaşılması için gerekli fonksiyonları içerir.
"""

import json
import re
from typing import List, Dict, Tuple
from fuzzywuzzy import fuzz
import string

class TurkceDilIsleme:
    def __init__(self, dil_kurallari_dosya: str = "yapilandirma/dil_kurallari.json"):
        """Türkçe dil işleme sınıfını başlat"""
        self.dil_kurallari = self._yukle_dil_kurallari(dil_kurallari_dosya)
        self.turkce_karakterler = self.dil_kurallari.get("turkce_karakterler", {})
        
    def _yukle_dil_kurallari(self, dosya_yolu: str) -> Dict:
        """Dil kurallarını JSON dosyasından yükle"""
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Dil kuralları dosyası bulunamadı: {dosya_yolu}")
            return {}
    
    def temizle_metin(self, metin: str) -> str:
        """Metni temizle ve normalize et"""
        if not metin:
            return ""
        
        # Başta ve sonda boşlukları kaldır
        metin = metin.strip()
        
        # Fazla boşlukları tek boşluğa indir
        metin = re.sub(r'\s+', ' ', metin)
        
        # Noktalama işaretlerini temizle
        metin = metin.translate(str.maketrans('', '', string.punctuation.replace('?', '').replace('!', '')))
        
        return metin.lower()
    
    def kelimelere_ayir(self, metin: str) -> List[str]:
        """Metni kelimelere ayır"""
        temiz_metin = self.temizle_metin(metin)
        kelimeler = temiz_metin.split()
        
        # Durdurma kelimelerini filtrele
        durdurma_kelimeleri = self.dil_kurallari.get("durdurma_kelimeleri", [])
        return [kelime for kelime in kelimeler if kelime not in durdurma_kelimeleri]
    
    def soru_mu(self, metin: str) -> bool:
        """Metnin soru olup olmadığını kontrol et"""
        soru_kelimeleri = self.dil_kurallari.get("soru_kelimeleri", [])
        kelimeler = self.kelimelere_ayir(metin)
        
        # Soru işareti var mı?
        if '?' in metin:
            return True
        
        # Soru kelimeleri var mı?
        for kelime in kelimeler:
            if kelime in soru_kelimeleri:
                return True
        
        return False
    
    def selamlasma_mi(self, metin: str) -> bool:
        """Metnin selamlama olup olmadığını kontrol et"""
        selamlasmalar = self.dil_kurallari.get("selamlasmalar", [])
        kelimeler = self.kelimelere_ayir(metin)
        
        for kelime in kelimeler:
            for selamlasma in selamlasmalar:
                if fuzz.ratio(kelime, selamlasma) > 80:
                    return True
        return False
    
    def vedalasma_mi(self, metin: str) -> bool:
        """Metnin vedalaşma olup olmadığını kontrol et"""
        vedalasmalar = self.dil_kurallari.get("vedalasmalar", [])
        kelimeler = self.kelimelere_ayir(metin)
        
        for kelime in kelimeler:
            for vedalasma in vedalasmalar:
                if fuzz.ratio(kelime, vedalasma) > 80:
                    return True
        return False
    
    def duygu_analizi(self, metin: str) -> str:
        """Basit duygu analizi yap"""
        olumlu_ifadeler = self.dil_kurallari.get("olumlu_ifadeler", [])
        olumsuz_ifadeler = self.dil_kurallari.get("olumsuz_ifadeler", [])
        
        kelimeler = self.kelimelere_ayir(metin)
        olumlu_skor = 0
        olumsuz_skor = 0
        
        for kelime in kelimeler:
            for olumlu in olumlu_ifadeler:
                if fuzz.ratio(kelime, olumlu) > 70:
                    olumlu_skor += 1
            
            for olumsuz in olumsuz_ifadeler:
                if fuzz.ratio(kelime, olumsuz) > 70:
                    olumsuz_skor += 1
        
        if olumlu_skor > olumsuz_skor:
            return "olumlu"
        elif olumsuz_skor > olumlu_skor:
            return "olumsuz"
        else:
            return "notr"
    
    def anahtar_kelimeleri_cikart(self, metin: str) -> List[str]:
        """Metinden anahtar kelimeleri çıkart"""
        kelimeler = self.kelimelere_ayir(metin)
        
        # En az 3 karakterli kelimeleri al
        anahtar_kelimeler = [kelime for kelime in kelimeler if len(kelime) >= 3]
        
        # Frekansa göre sırala (basit implementasyon)
        return list(set(anahtar_kelimeler))[:5]  # En fazla 5 anahtar kelime
    
    def benzerlik_hesapla(self, metin1: str, metin2: str) -> float:
        """İki metin arasındaki benzerliği hesapla"""
        return fuzz.ratio(self.temizle_metin(metin1), self.temizle_metin(metin2)) / 100.0
    
    def konu_belirle(self, metin: str) -> str:
        """Metnin konusunu belirlemeye çalış"""
        anahtar_kelimeler = self.anahtar_kelimeleri_cikart(metin)
        
        # Basit konu tespiti (geliştirilmesi gerekir)
        teknoloji_kelimeleri = ["python", "kod", "program", "bilgisayar", "yazılım", "uygulama"]
        egitim_kelimeleri = ["öğren", "ders", "kitap", "okul", "öğretmen", "öğrenci"]
        kisisel_kelimeler = ["ben", "sen", "biz", "hayat", "aile", "arkadaş"]
        
        teknoloji_skor = sum(1 for kelime in anahtar_kelimeler if kelime in teknoloji_kelimeleri)
        egitim_skor = sum(1 for kelime in anahtar_kelimeler if kelime in egitim_kelimeleri)
        kisisel_skor = sum(1 for kelime in anahtar_kelimeler if kelime in kisisel_kelimeler)
        
        if teknoloji_skor > 0:
            return "teknoloji"
        elif egitim_skor > 0:
            return "eğitim"
        elif kisisel_skor > 0:
            return "kişisel"
        else:
            return "genel"
