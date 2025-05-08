import nfc
import re
import customtkinter as ctk
import time
import threading

def extract_student_id(tag_data):
    pattern = re.compile(r"[A-Za-z]?\d{6,10}")  # 6～10桁の学籍番号のパターン
    for line in tag_data:
        match = pattern.search(line)
        if match:
            return match.group()  # 最初に見つかった学籍番号を返す
    return "未登録"  # 学籍番号が見つからなかった場合

class NFCWelcomeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("NFC 学籍番号表示システム")
        self.geometry("1920x1080")  # フルHDサイズに設定

        # アニメーション用の after ID を初期化
        self.animation_id = None
        
        # フォントサイズやパディングを大きくして見やすく調整
        self.label = ctk.CTkLabel(self, text="学生証をかざしてください", font=("Arial", 48, "bold"))
        self.label.pack(expand=True, pady=50)
        
        # NFCスレッドの開始
        self.start_nfc_thread()
    
    def update_display(self, student_id):
        self.animate_text(f"いらっしゃい！ {student_id}")
        self.after(10000, self.reset_display)
    
    def reset_display(self):
        # 表示リセット時もアニメーション中ならキャンセル
        if self.animation_id is not None:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        self.label.configure(text="学生証をかざしてください")
    
    def animate_text(self, text):
        # 既存のアニメーションがあればキャンセル
        if self.animation_id is not None:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        
        self.label.configure(text="")  # ラベルをクリア
        
        def display_letter(i=0):
            if i < len(text):
                # 現在のテキストに1文字ずつ追加
                current_text = self.label.cget("text")
                self.label.configure(text=current_text + text[i])
                # 次の文字表示のための after を登録し、その ID を保存
                self.animation_id = self.after(100, lambda: display_letter(i+1))
            else:
                self.animation_id = None  # 終了時は ID をリセット
        
        display_letter()
    
    def start_nfc_thread(self):
        thread = threading.Thread(target=self.nfc_reader, daemon=True)
        thread.start()
    
    def nfc_reader(self):
        with nfc.ContactlessFrontend("usb") as clf:
            while True:
                clf.connect(rdwr={"on-connect": self.on_connect})
                time.sleep(2)  # 読み取り後に2秒待機
    
    def on_connect(self, tag):
        try:
            tag_data = tag.dump()
            # ファイルに保存
            with open("nfc_dump.txt", "a", encoding="utf-8") as file:
                file.write(f"学籍番号: {extract_student_id(tag_data)}\n")
                file.write("---- NFC Dump ----\n")
                file.write("\n".join(tag_data))  # 各行を書き込み
                file.write("\n------------------\n\n")
                
            with open("student_id.txt", "a", encoding="utf-8") as file:
                file.write(f"学籍番号: {extract_student_id(tag_data)}\n")
            
        except Exception as e:
            print("タグ読み取りエラー:", e)
            tag_data = []
        
        student_id = extract_student_id(tag_data)
        print("学籍番号:", student_id)
        self.update_display(student_id)

if __name__ == "__main__":
    app = NFCWelcomeApp()
    app.mainloop()
