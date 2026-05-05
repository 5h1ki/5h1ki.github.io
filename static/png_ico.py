from PIL import Image

# 1. 设置输入和输出文件名
# 请确保 input_filename 与您保存的无背景 PNG 图像的文件名一致
input_filename = "input.png" 
output_filename = "output.ico"

try:
    # 2. 打开生成的透明 PNG 图像并确保为 RGBA 模式
    img = Image.open(input_filename).convert("RGBA")

    # 3. 创建一个符合大多数要求的 ICO 文件。
    # 为了将文件大小保持在 10KB 以下，我们将 ICO 限制为
    # 两个最常用的尺寸：16x16 和 32x32 像素。
    # 一个包含这两个尺寸的 standard ICO 文件（使用基于调色板的 BMP 编码）
    # 通常只有 2-3 KB。

    # 我们首先将图像调整为一个合理的中间尺寸（例如 128x128）
    # 以确保 Pillow 不会尝试保存全分辨率版本，这会增加文件头元数据的大小。
    base_image = img.resize((128, 128), Image.LANCZOS)
    
    # 4. 保存为包含 16x16 和 32x32 像素的单个 ICO 文件。
    # Pillow 的 sizes 参数可以处理多帧 ICO，并会自动管理内部编码。
    # 这个组合几乎可以肯定会产生小于 10KB 的文件。
    base_image.save(output_filename, format='ICO', sizes=[(16, 16), (32, 32)])

    print(f"--------------------------------------------------")
    print(f"成功创建 ICO 文件: '{output_filename}'。")
    print(f"请检查该文件的大小，它应该远小于 10KB。")
    print(f"--------------------------------------------------")

except FileNotFoundError:
    print(f"--------------------------------------------------")
    print(f"错误：请确保文件夹中存在无背景 PNG 文件 '{input_filename}'。")
    print(f"--------------------------------------------------")
except Exception as e:
    print(f"--------------------------------------------------")
    print(f"发生错误: {e}")
    print(f"--------------------------------------------------")