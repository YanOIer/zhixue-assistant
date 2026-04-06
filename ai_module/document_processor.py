"""
文档处理模块
支持PDF、图片、文本文件的文本提取
"""

import os
import re

def extract_text_from_txt(file_path):
    """
    从文本文件提取内容
    
    参数：
        file_path: 文件路径
    
    返回：
        文本内容
    """
    try:
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # 如果都失败，使用latin-1（不会报错但可能有乱码）
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()
            
    except Exception as e:
        print(f"读取文本文件失败: {e}")
        return ""

def extract_text_from_pdf(file_path):
    """
    从PDF文件提取文本
    
    参数：
        file_path: PDF文件路径
    
    返回：
        提取的文本内容
    
    说明：
        需要安装PyPDF2: pip install PyPDF2
    """
    try:
        import PyPDF2
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"PDF共 {len(pdf_reader.pages)} 页")
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- 第{page_num + 1}页 ---\n"
                    text += page_text
                    
        return text
        
    except ImportError:
        print("错误: 未安装PyPDF2，请运行: pip install PyPDF2")
        return ""
    except Exception as e:
        print(f"读取PDF失败: {e}")
        return ""

def extract_text_from_image(image_path):
    """
    从图片提取文本（OCR）
    
    参数：
        image_path: 图片文件路径
    
    返回：
        识别的文本内容
    
    说明：
        需要安装:
        1. pytesseract: pip install pytesseract
        2. Tesseract-OCR引擎（系统级安装）
           Windows: 下载安装包 https://github.com/UB-Mannheim/tesseract/wiki
           Mac: brew install tesseract
           Linux: sudo apt-get install tesseract-ocr
    """
    try:
        from PIL import Image
        import pytesseract
        
        # 设置Tesseract路径（Windows需要）
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        image = Image.open(image_path)
        
        # 使用中文+英文识别
        text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        
        return text
        
    except ImportError:
        print("错误: 未安装pytesseract，请运行: pip install pytesseract Pillow")
        return ""
    except Exception as e:
        print(f"OCR识别失败: {e}")
        return ""

def process_document(file_path):
    """
    自动识别文件类型并提取文本
    
    参数：
        file_path: 文件路径
    
    返回：
        提取的文本内容
    """
    # 获取文件扩展名
    ext = os.path.splitext(file_path)[1].lower()
    
    print(f"处理文件: {file_path}")
    print(f"文件类型: {ext}")
    
    if ext == '.txt':
        return extract_text_from_txt(file_path)
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
        return extract_text_from_image(file_path)
    else:
        print(f"不支持的文件类型: {ext}")
        return ""

def clean_text(text):
    """
    清理文本内容
    
    参数：
        text: 原始文本
    
    返回：
        清理后的文本
    """
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    
    # 移除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,;:!?()-]', '', text)
    
    # 移除空行
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    return '\n'.join(lines)


# 测试代码
if __name__ == "__main__":
    # 测试文本提取
    test_file = "test.txt"
    
    if os.path.exists(test_file):
        text = process_document(test_file)
        print(f"\n提取的文本内容（前500字符）:\n{text[:500]}")
    else:
        print(f"测试文件不存在: {test_file}")
        print("请创建一个测试文件或修改测试代码中的文件路径")
