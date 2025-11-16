import tkinter as tk
from tkinter import messagebox, simpledialog
import random


# Oyun içinde sorulan kelimelerin kütüphanesi

kelime_kategorileri = {
    "meyve": ["elma", "muz", "çilek", "kiraz", "portakal"],
    "hayvan": ["kedi", "köpek", "aslan", "fil", "zürafa"],
    "teknoloji": ["bilgisayar", "telefon", "robot", "yazılım", "internet"]
}

# HATA SAYISAL LİMİTÖRÜ
max_hata = 6


# Uygulama Tasarım Alanı
class HarfKurtarmaOyunu:
    def __init__(self, master):
        self.master = master
        self.master.title("Calc & Hang — İşlem Yap, Harfi Kurtar")
        self.master.geometry("550x530") #UYGULAMA BÜYÜKLÜĞÜNÜ AYARLADIĞIMIZ KISIM DİKEY/YATAY
        self.master.config(bg="#e8eef1")

        self.reset_oyun()

        # Başlık
        self.lbl_baslik = tk.Label(master, text=" Calc & Hang — İşlem Yap, Harfi Kurtar",
                                   font=("Arial", 18, "bold"),
                                   fg="#2c3e50", bg="#e8eef1")
        self.lbl_baslik.pack(pady=10)

        # Kelime alanı
        self.lbl_kelime = tk.Label(master, text=self.gizli_kelime(),
                                   font=("Consolas", 24),
                                   fg="#0a3d62", bg="#e8eef1")
        self.lbl_kelime.pack(pady=10)

        ###DURUM GÖSTERGESİ
        self.lbl_durum = tk.Label(master, text="", font=("Arial", 12),
                                  fg="#2c3e50", bg="#e8eef1")
        self.lbl_durum.pack()

        # Harf tahmin alanı
        frame_tahmin = tk.Frame(master, bg="#e8eef1")
        frame_tahmin.pack(pady=10)

        self.entry_harf = tk.Entry(frame_tahmin, width=5, font=("Arial", 16),
                                   bg="#ffffff", fg="#2c3e50")
        self.entry_harf.grid(row=0, column=0, padx=5)

        tk.Button(frame_tahmin, text="Harf Tahmini", command=self.harf_tahmin, #TAHMİN BUTONU
                  bg="#6ab0de", fg="white").grid(row=0, column=1, padx=5)

        # İşlem / ipucu / yeni oyun
        frame_ops = tk.Frame(master, bg="#e8eef1")
        frame_ops.pack(pady=10)

        tk.Button(frame_ops, text=" İşlem Çöz (Rastgele)", command=self.islem_coz, #İŞLEM ÇÖZ BUTONU
                  bg="#7ed6a8", fg="#2c3e50").grid(row=0, column=0, padx=5)

        tk.Button(frame_ops, text=" İpucu Al", command=self.ipucu_al,        #İPUCU AL BUTONU
                  bg="#f7d794", fg="#2c3e50").grid(row=0, column=1, padx=5)

        tk.Button(frame_ops, text="Yeni Oyun", command=self.yeni_oyun,    #YENİ OYUN BUTONU
                  bg="#e77f89", fg="white").grid(row=0, column=2, padx=5)

        # Çizim alanı
        self.canvas = tk.Canvas(master, width=200, height=220,
                                bg="#fdfdfd", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.adam_ciz()
        self.guncelle_durum()

    # Oyun startup ve resetlenme alanı
    def reset_oyun(self):
        self.kategori = random.choice(list(kelime_kategorileri.keys()))
        self.kelime = random.choice(kelime_kategorileri[self.kategori])
        self.dogru_harfler = set()
        self.yanlis_harfler = set()
        self.bonus = 0
        self.hata = 0
        self.puan = 0

    def gizli_kelime(self):
        return " ".join([harf if harf in self.dogru_harfler else "_" for harf in self.kelime])

    def guncelle_durum(self):
        self.lbl_kelime.config(text=self.gizli_kelime())
        self.lbl_durum.config(
            text=f"Hata hakkı: {max_hata - self.hata} | Bonus: {self.bonus} | Puan: {self.puan}"
        )
        self.adam_ciz()

    # Harf tahmini
    def harf_tahmin(self):
        harf = self.entry_harf.get().lower()
        self.entry_harf.delete(0, tk.END)

        if not harf or len(harf) != 1 or not harf.isalpha():
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir harf gir!")
            return

        if harf in self.dogru_harfler or harf in self.yanlis_harfler:
            messagebox.showinfo("Bilgi", "Bu harfi zaten denedin.")
            return

        if harf in self.kelime:
            self.dogru_harfler.add(harf)
            self.puan += 10
        else:
            self.yanlis_harfler.add(harf)
            self.hata += 1
            self.puan -= 5

        self.kontrol_et()

    # İşlem çözme — tam sayı + negatif yok
    def islem_coz(self):
        islemler = ["+", "-", "*", "/"]
        islem = random.choice(islemler)

        if islem == "/":
            # Tam sayı çıkması için a = b * k
            b = random.randint(1, 10)
            k = random.randint(1, 10)
            a = b * k
            sonuc = a // b

        elif islem == "-":
            # Negatif çıkmaması için a >= b
            a = random.randint(1, 20)
            b = random.randint(1, a)  # b her zaman a’dan küçük/eşit
            sonuc = a - b

        else:
            a = random.randint(1, 20)
            b = random.randint(1, 20)

            if islem == "+":
                sonuc = a + b
            elif islem == "*":
                sonuc = a * b

        cevap = simpledialog.askfloat(" Rastgele İşlem", f"{a} {islem} {b} = ?")

        if cevap is None:
            return
        if abs(cevap - sonuc) < 0.01:
            self.bonus += 1
            self.puan += 20
            kalan_harfler = [h for h in self.kelime if h not in self.dogru_harfler]
            if kalan_harfler:
                acilacak = random.choice(kalan_harfler)
                self.dogru_harfler.add(acilacak)
                messagebox.showinfo(" Doğru!", f"Doğru cevap! '{acilacak}' harfi açıldı ")
        else:
            self.hata += 1
            self.puan -= 5
            messagebox.showerror(" Yanlış", f"Yanlış cevap! Doğru sonuç {sonuc}")

        self.kontrol_et()

    # İpucu
    def ipucu_al(self):
        if self.bonus > 0:
            self.bonus -= 1
            messagebox.showinfo("İpucu", f"Kelimenin kategorisi: {self.kategori.upper()}")
        else:
            messagebox.showwarning("Yetersiz Bonus", "Yeterli bonusun yok!")
        self.guncelle_durum()

    # Yeni oyun
    def yeni_oyun(self):
        self.reset_oyun()
        self.guncelle_durum()

    # Oyun kontrol
    def kontrol_et(self):
        self.guncelle_durum()
        if all(harf in self.dogru_harfler for harf in self.kelime):
            self.puan += 50
            messagebox.showinfo(" Kazandın!", f"Tebrikler! Kelime: {self.kelime.upper()}\nToplam Puan: {self.puan}")
            self.reset_oyun()
            self.guncelle_durum()
        elif self.hata >= max_hata:
            self.puan -= 20
            messagebox.showerror(" Kaybettin!", f"Doğru Kelime: {self.kelime.upper()}\nToplam Puan: {self.puan}")
            self.reset_oyun() #PANEL KENDİNİ RESETLER BAŞTAN RANDOM KELİME İLE OYUNA BAŞLARSIN
            self.guncelle_durum()

    # Adamın asılma anismasyonu gerçekleşmesi
    def adam_ciz(self):
        self.canvas.delete("all")
        renk = "#2c3e50"
       #zemin ve direk için(x1 x2 y1 y2)
        self.canvas.create_line(20, 200, 180, 200, width=3, fill=renk)
        self.canvas.create_line(50, 200, 50, 40, width=3, fill=renk)
        self.canvas.create_line(50, 40, 130, 40, width=3, fill=renk)
        self.canvas.create_line(130, 40, 130, 60, width=3, fill=renk)
     #Adam figürü için (x1 x2 y1 y2
        if self.hata >= 1:
            self.canvas.create_oval(115, 60, 145, 90, width=2, outline=renk)
        if self.hata >= 2:
            self.canvas.create_line(130, 90, 130, 140, width=2, fill=renk)
        if self.hata >= 3:
            self.canvas.create_line(130, 100, 110, 120, width=2, fill=renk)
        if self.hata >= 4:
            self.canvas.create_line(130, 100, 150, 120, width=2, fill=renk)
        if self.hata >= 5:
            self.canvas.create_line(130, 140, 115, 170, width=2, fill=renk)
        if self.hata >= 6:
            self.canvas.create_line(130, 140, 145, 170, width=2, fill=renk)



# Uygulama çalıştırma bölümü

root = tk.Tk()
app = HarfKurtarmaOyunu(root)
root.mainloop()
