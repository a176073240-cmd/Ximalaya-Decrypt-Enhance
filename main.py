import base64
import io
import sys
import magic
import pathlib
import os
import glob
import mutagen
import tkinter as tk
from tkinter import filedialog
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from mutagen.easyid3 import ID3
from wasmer import Store, Module, Instance, Uint8Array, Int32Array, engine
from wasmer_compiler_cranelift import Compiler


class XMInfo:
    def __init__(self):
        self.title = ""
        self.artist = ""
        self.album = ""
        self.tracknumber = 0
        self.size = 0
        self.header_size = 0
        self.ISRC = ""
        self.encodedby = ""
        self.encoding_technology = ""

    def iv(self):
        if self.ISRC != "":
            return bytes.fromhex(self.ISRC)
        return bytes.fromhex(self.encodedby)


def get_str(x):
    if x is None:
        return ""
    return x


def read_file(x):
    with open(x, "rb") as f:
        return f.read()


def get_xm_info(data: bytes):
    id3 = ID3(io.BytesIO(data), v2_version=3)
    id3value = XMInfo()
    id3value.title = str(id3["TIT2"])
    id3value.album = str(id3["TALB"])
    id3value.artist = str(id3["TPE1"])
    # 提取官方文件头里自带的真实集数序号
    try:
        id3value.tracknumber = int(str(id3["TRCK"]))
    except:
        id3value.tracknumber = 0
        
    id3value.ISRC = "" if id3.get("TSRC") is None else str(id3["TSRC"])
    id3value.encodedby = "" if id3.get("TENC") is None else str(id3["TENC"])
    id3value.size = int(str(id3["TSIZ"]))
    id3value.header_size = id3.size
    id3value.encoding_technology = str(id3["TSSE"])
    return id3value


def get_printable_count(x: bytes):
    i = 0
    for i, c in enumerate(x):
        if c < 0x20 or c > 0x7e:
            return i
    return i


def get_printable_bytes(x: bytes):
    return x[:get_printable_count(x)]


def xm_decrypt(raw_data):
    wasm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xm_encryptor.wasm")
    xm_encryptor = Instance(Module(
        Store(engine.Universal(Compiler)),
        open(wasm_path, "rb").read()
    ))
    
    xm_info = get_xm_info(raw_data)
    encrypted_data = raw_data[xm_info.header_size:xm_info.header_size + xm_info.size:]

    # Stage 1 aes-256-cbc
    xm_key = b"ximalayaximalayaximalayaximalaya"
    cipher = AES.new(xm_key, AES.MODE_CBC, xm_info.iv())
    de_data = cipher.decrypt(pad(encrypted_data, 16))
    
    # Stage 2 xmDecrypt
    de_data = get_printable_bytes(de_data)
    track_id = str(xm_info.tracknumber).encode()
    stack_pointer = xm_encryptor.exports.a(-16)
    assert isinstance(stack_pointer, int)
    de_data_offset = xm_encryptor.exports.c(len(de_data))
    assert isinstance(de_data_offset, int)
    track_id_offset = xm_encryptor.exports.c(len(track_id))
    assert isinstance(track_id_offset, int)
    memory_i = xm_encryptor.exports.i
    memview_unit8: Uint8Array = memory_i.uint8_view(offset=de_data_offset)
    for i, b in enumerate(de_data):
        memview_unit8[i] = b
    memview_unit8: Uint8Array = memory_i.uint8_view(offset=track_id_offset)
    for i, b in enumerate(track_id):
        memview_unit8[i] = b
        
    xm_encryptor.exports.g(stack_pointer, de_data_offset, len(de_data), track_id_offset, len(track_id))
    memview_int32: Int32Array = memory_i.int32_view(offset=stack_pointer // 4)
    result_pointer = memview_int32[0]
    result_length = memview_int32[1]
    
    result_data = bytearray(memory_i.buffer)[result_pointer:result_pointer + result_length].decode()
    
    # Stage 3 combine
    decrypted_data = base64.b64decode(xm_info.encoding_technology + result_data)
    final_data = decrypted_data + raw_data[xm_info.header_size + xm_info.size::]
    return xm_info, final_data


def find_ext(data):
    exts = ["m4a", "mp3", "flac", "wav"]
    value = magic.from_buffer(data).lower()
    for ext in exts:
        if ext in value:
            return ext
    raise Exception(f"unexpected format {value}")


def replace_invalid_chars(name):
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in name:
            name = name.replace(char, " ")
    return name


def decrypt_xm_file(from_file, output_path, do_rename=False):
    data = read_file(from_file)
    info, audio_data = xm_decrypt(data)
    
    album_name = replace_invalid_chars(info.album)
    title_name = replace_invalid_chars(info.title)
    ext = find_ext(audio_data[:0xff])
    
    album_path = os.path.join(output_path, album_name)
    if not os.path.exists(album_path):
        os.makedirs(album_path)
        
    # 【原生级集数重命名】
    if do_rename and info.tracknumber > 0:
        formatted_name = f"{info.tracknumber:04d} - {title_name}.{ext}"
        output_file = os.path.join(album_path, formatted_name)
    else:
        output_file = os.path.join(album_path, f"{title_name}.{ext}")
    
    buffer = io.BytesIO(audio_data)
    
    # 【内存级音频双重完整性校验】
    try:
        tags = mutagen.File(buffer, easy=True)
        if tags is None:
            raise ValueError("无法识别音频格式，文件可能已严重损坏")
            
        duration = getattr(tags.info, 'length', 0)
        bitrate = getattr(tags.info, 'bitrate', 0)
        
        if duration > 0 and bitrate > 0:
            expected_size = (duration * bitrate) / 8
            actual_size = len(audio_data)
            completion_rate = actual_size / expected_size
            
            if completion_rate < 0.85:
                raise ValueError(f"下载断层 (完整度仅 {completion_rate*100:.1f}%)")
                
    except mutagen.MutagenError:
        raise ValueError("音频流格式破坏，源文件下载不完整")
        
    tags["title"] = info.title
    tags["album"] = info.album
    tags["artist"] = info.artist
    tags.save(buffer)
    
    with open(output_file, "wb") as f:
        buffer.seek(0)
        f.write(buffer.read())


def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.destroy()
    return file_path


def select_directory():
    root = tk.Tk()
    root.withdraw()
    directory_path = filedialog.askdirectory()
    root.destroy()
    return directory_path


def main_loop():
    while True:
        print("\n" + "="*50)
        print(" 欢迎使用喜马拉雅音频解密工具 (大一统旗舰版 v1.0.4) ")
        print(" 核心算法: @sld272 | 维护加强: @a176073240-cmd ")
        print("="*50)
        print("1. 解密单个文件")
        print("2. 批量解密文件")
        print("3. 退出")
        choice = input("请输入选项: ")
        
        if choice == "1" or choice == "2":
            if choice == "1":
                files_to_decrypt = [select_file()]
                if files_to_decrypt == [""]:
                    print("检测到文件选择窗口被关闭")
                    continue
            elif choice == "2":
                dir_to_decrypt = select_directory()
                if dir_to_decrypt == "":
                    print("检测到目录选择窗口被关闭")
                    continue
                files_to_decrypt = glob.glob(os.path.join(dir_to_decrypt, "*.xm"))
                
            total_files = len(files_to_decrypt)
            if total_files == 0:
                print("未找到待处理的 .xm 文件！")
                continue
                
            print("\n请选择是否需要在文件名前面加上序号（按顺序重命名）：")
            print("1. 不进行按顺序重命名 (输出例如：马拉车.m4a)")
            print("2. 进行按顺序重命名   (输出例如：0204 - 马拉车.m4a)")
            rename_choice = input("请输入 (1/2): ")
            do_rename = (rename_choice == "2")

            print("\n请选择是否需要设置输出路径：（不设置默认为本程序目录下的output文件夹）")
            print("1. 设置输出路径")
            print("2. 不设置输出路径")
            out_choice = input("请输入 (1/2): ")
            
            if out_choice == "1":
                output_path = select_directory()
                if output_path == "":
                    print("检测到目录选择窗口被关闭")
                    continue
            else:
                output_path = os.path.join(os.getcwd(), "output")
                
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            success_count = 0
            failed_list = []
            
            print(f"\n🚀 开始火力全开处理，共 {total_files} 个文件...")
            print("（运行期间将隐藏成功提示，保持静默，请耐心等待进度条走完）\n")
            
            for i, file in enumerate(files_to_decrypt, 1):
                file_name = os.path.basename(file)
                
                print(f"\r⏳ 正在解密进度: [ {i} / {total_files} ]", end="", flush=True)
                
                try:
                    if os.path.getsize(file) == 0:
                        raise Exception("文件大小为 0KB (空文件)")
                        
                    decrypt_xm_file(file, output_path, do_rename)
                    success_count += 1
                except Exception as e:
                    failed_list.append((file_name, str(e)))
            
            print("\n\n" + "="*50)
            print(" 📊 解密任务分类报告")
            print("="*50)
            
            print(f"✅ 完美解密文件: {success_count} 个")
            
            if failed_list:
                print(f"\n🚨 智能拦截残次品/失败: {len(failed_list)} 个，清单如下：")
                print("-" * 45)
                for fail_name, reason in failed_list:
                    print(f"❌ {fail_name}")
                    print(f"   -> 状态: {reason}")
                print("-" * 45)
                print("\n💡 提示：请根据以上清单，回客户端重新下载这几个文件即可。")
            else:
                print("\n🎉 恭喜！本次转码零失误，全部完美保存！")
            
            print("="*50)
            
        elif choice == "3":
            sys.exit()
        else:
            print("输入错误，请重新输入！")

if __name__ == "__main__":
    try:
        main_loop()
    except Exception as e:
        print(f"\n\n🚨 哎呀！程序发生了意外的崩溃！")
        print(f"崩溃原因: {e}")
    finally:
        input("\n按回车键退出窗口...")
