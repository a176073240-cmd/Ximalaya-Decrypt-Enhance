import os
import re
import tkinter as tk
from tkinter import filedialog

def main():
    root = tk.Tk()
    root.withdraw()
    print("==================================================")
    print(" 强迫症专属重命名工具 (终极版：无视旧前缀，强制清理)")
    print("==================================================")
    print("请在弹出的窗口中选择你的音频文件夹...")
    folder_path = filedialog.askdirectory()

    if not folder_path:
        print("已取消操作：未选择文件夹。")
        input("\n按回车键退出窗口...")
        return

    # 只处理音频文件
    valid_exts = ['.mp3', '.m4a', '.flac', '.wav']
    files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in valid_exts]

    if not files:
        print("没有在选择的文件夹里找到音频文件哦！")
        input("\n按回车键退出窗口...")
        return

    success_list = []
    fail_list = []

    print(f"\n扫描到 {len(files)} 个文件，开始强制清洗...\n")

    for filename in files:
        name_without_ext, ext = os.path.splitext(filename)
        
        # 1. 无论有没有 [0001] 这种旧前缀，先把它扒掉，还原成最原始的名字
        # 比如 "[0001] 末世大回炉001" 会被还原成 "末世大回炉001"
        raw_name = re.sub(r'^\[\d+\]\s*', '', name_without_ext)

        # 2. 从原始名字里找到真正的集数数字
        match = re.search(r'\d+', raw_name)
        if not match:
            continue # 如果连原本名字里都没数字，就跳过
            
        ep_num = int(match.group())

        # 3. 核心步骤：把原始名字里的这个数字（以及前后的空格）删掉
        clean_name = re.sub(r'\s*\d+\s*', ' ', raw_name, count=1).strip()
        
        # 4. 组装新名字：全新的补零前缀 + 干净名字 + 后缀
        new_filename = f"[{ep_num:04d}] {clean_name}{ext}"

        # 如果清洗后发现名字没变，说明已经是最完美的状态了，跳过
        if filename == new_filename:
            continue

        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_filename)

        try:
            os.rename(old_path, new_path)
            success_list.append(f"{filename}  ==>  {new_filename}")
        except Exception as e:
            fail_list.append(f"{filename} (原因: {e})")

    # ---------------- 打印结果汇总 ----------------
    print("="*50)
    print(f"处理完成！共成功修改 {len(success_list)} 个文件。")
    print("="*50)
    
    if success_list:
        print("\n【成功清单】:")
        for item in success_list:
            print("  ✓ " + item)
            
    if fail_list:
        print("\n【失败清单】:")
        for item in fail_list:
            print("  × " + item)

    # 结束拦截，等待用户按回车关闭窗口
    input("\n任务结束，请按回车键退出窗口...")

if __name__ == "__main__":
    main()