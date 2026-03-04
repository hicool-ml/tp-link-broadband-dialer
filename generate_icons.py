from PIL import Image, ImageDraw, ImageFont
import os

# 定义图标尺寸（多尺寸ICO必须包含这些）
ICO_SIZES = [(16, 16), (32, 32), (48, 48), (256, 256)]

def create_icon(size, color, text, bg_transparent=True):
    """生成单个尺寸的图标（Win10风格网络图标）"""
    # 创建透明背景画布
    img = Image.new("RGBA", size, (0, 0, 0, 0) if bg_transparent else (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 绘制Win10风格网络图标主体（简化版，清晰易识别）
    center_x, center_y = size[0]//2, size[1]//2
    radius = min(size)//4
    
    # 网络图标基础形状（电脑+网线）
    # 主体矩形（电脑）
    rect_x1 = center_x - radius*1.5
    rect_y1 = center_y - radius
    rect_x2 = center_x + radius*1.5
    rect_y2 = center_y + radius
    draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], fill=color, outline=(0,0,0,100), width=1)
    
    # 网线（3条横线）
    for i in range(3):
        line_y = rect_y2 + (i+1)*2
        draw.line([rect_x1, line_y, rect_x2, line_y], fill=color, width=1)
    
    # 状态文字（小尺寸不显示，大尺寸显示）
    if size[0] >= 32:
        try:
            # 尝试加载系统字体，没有则用默认
            font = ImageFont.truetype("arial.ttf", size[0]//6)
        except:
            font = ImageFont.load_default()
        draw.text((center_x, rect_y2 + 8), text, fill=color, font=font, anchor="mt")
    
    return img

def generate_ico(icon_name, color, text):
    """生成多尺寸ICO文件"""
    # 生成所有尺寸的图标
    icons = [create_icon(size, color, text) for size in ICO_SIZES]
    # 保存为ICO
    icons[0].save(
        f"{icon_name}.ico",
        format="ICO",
        sizes=ICO_SIZES,
        append_images=icons[1:]
    )
    print(f"[OK] Generated: {icon_name}.ico")

# 批量生成4个状态图标
if __name__ == "__main__":
    # 主图标（蓝色）
    generate_ico("app", (0, 120, 215, 255), "拨号")
    # 在线（绿色）
    generate_ico("online", (0, 180, 0, 255), "Online")
    # 断开（灰色）
    generate_ico("offline", (128, 128, 128, 255), "Offline")
    # 连接中（蓝色）
    generate_ico("connecting", (0, 100, 200, 255), "Connecting")
    # 错误（红色）
    generate_ico("error", (200, 0, 0, 255), "Error")
    
    input("All icons generated! Press Enter to exit...")
