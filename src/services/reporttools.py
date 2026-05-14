from pathlib import Path
from typing import BinaryIO
from reportlab.pdfgen import canvas
from PIL import Image
import subprocess
import shutil
import os

px = 0.75
SCALE = 1
SCALED_PX = px * SCALE

PDF_HEIGHT, PDF_WIDTH = 1080, 1920
HEDING_FONT_SIZE = 80
INDENTS = (50, 50)  # indents by x and y
REPORTS_PATH = Path("reports")


IMG_FOLDER = Path(__file__).parent / "imgs"

FIRST_SLIDE = IMG_FOLDER / "first_slide_bg.png"
PRE_LAST_SLIDE = IMG_FOLDER / "pre_last_slide_bg.png"
LAST_SLIDE = IMG_FOLDER / "last_slide_bg.png"


class Indent:
    x = INDENTS[0]
    y = INDENTS[1]

    @staticmethod
    def get_x() -> float:
        return Indent.x

    @staticmethod
    def get_y() -> float:
        return Indent.y


FONTS_PATH = Path(__file__).parent / "fonts"


class Fonts:
    regular = {
        "name": "IBMPlexSansRegular",
        "path": FONTS_PATH / "IBMPlexSans-Regular.ttf",
    }
    bold = {
        "name": "IBMPlexSansBold",
        "path": FONTS_PATH / "IBMPlexSans-Bold.ttf",
    }
    italics = {
        "name": "IBMPlexSansRegular",
        "path": FONTS_PATH / "IBMPlexSans-Regular.ttf",
    }
    medium = {
        "name": "IBMPlexSansRegular",
        "path": FONTS_PATH / "IBMPlexSans-Regular.ttf",
    }
    light = {
        "name": "IBMPlexSansRegular",
        "path": FONTS_PATH / "IBMPlexSans-Regular.ttf",
    }
    
class Formatter:
    IMAGE_WIDTH = 0
    X_POS = 0
    Y_POS = 0

    def __init__(self, img_width, hor_pos, vert_pos):
        self.IMAGE_WIDTH = img_width
        self.X_POS = hor_pos
        self.Y_POS = vert_pos

    def width(self) -> float:
        return self.IMAGE_WIDTH

    def center(self) -> tuple[int, int]:
        return (int((PDF_WIDTH - self.X_POS) / 2), int(self.Y_POS))

    def left(self) -> tuple[int, int]:
        return (0, int(self.Y_POS))

    def right(self) -> tuple[int, int]:
        return (int(PDF_WIDTH - self.X_POS), int(self.Y_POS))


def divide_by_len(text: str, line_len: int) -> list:
    text = text.replace("  ", " ")
    new_text = []
    j = 1
    start = 0
    if line_len >= len(text):
        new_text.append(text)
    else:
        while j <= 4 and start < len(text):
            end_j = j * (line_len + 1)
            if end_j >= len(text):
                end_j = len(text) - 1
            for end in range(end_j, start, -1):
                if end + 1 == len(text) or text[end] == " ":
                    end += 1
                    new_text.append(text[start:end])
                    start = end
                    j += 1
                    break
    return new_text


def image_crop(img_bin: BinaryIO, w_size=4, h_size=3) -> Image.Image:
    img = Image.open(img_bin)
    width, height = img.size

    relation = width / height
    left = 0
    top = 0
    right = width
    bottom = height

    if relation > w_size / h_size:
        to_crop = (width - (height * w_size) / h_size) / 2
        left = to_crop
        right = width - to_crop
        bottom = height
    elif relation < w_size / h_size:
        to_crop = (height - (width * h_size) / w_size) / 2
        top = to_crop
        right = width
        bottom = height - to_crop
    return img.crop((left, top, right, bottom))


def image_formatter(img, exp_width: int) -> canvas.ImageReader:
    img_w, img_h = img.size
    size_rel = img_h / img_w
    exp_height = int(exp_width * size_rel)
    exp_size = tuple([exp_width, exp_height])
    return canvas.ImageReader(img.resize(exp_size))


def add_image(canv, img: Image.Image, img_width: float, x: float, y: float):
    format_const = Formatter(img_width, INDENTS[0], y)
    img_f = image_formatter(img, int(format_const.width()))
    canv.drawImage(img_f, x=x, y=y, mask="auto")


def _get_ghostscript_path():
    # gs_names = ["gswin64c", "gswin32c", "gs"]  # "c" в конце — консольная версия
    gs_names = ["gs", "gswin32", "gswin64"]
    for name in gs_names:
        if shutil.which(name):
            return shutil.which(name)
    raise FileNotFoundError(
        f'No GhostScript executable was found on path ({"/".join(gs_names)})'
    )


def pdf_compression(filepath: str, remove_input_file=True) -> str:
    gs = _get_ghostscript_path()
    input_file_abs_path = filepath
    new_filename = os.path.splitext(filepath)[0]
    output_file_abs_path = os.path.abspath(f"{new_filename}-compressed.pdf")

    with open(f"{output_file_abs_path}", "w") as _:
        pass
    subprocess.call(
        [
            gs,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS={}".format("/default"),
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-sOutputFile={}".format(output_file_abs_path),
            input_file_abs_path,
        ]
    )
    if remove_input_file:
        os.remove(input_file_abs_path)
    return output_file_abs_path

# def _get_ghostscript_path():
#     # 1. Проверяем стандартные имена в PATH
#     gs_names = ["gswin64c", "gswin32c", "gs"]
#     for name in gs_names:
#         path = shutil.which(name)
#         if path:
#             return path
    
#     # 2. Проверяем стандартные пути установки
#     gs_install_paths = [
#         r"C:\Program Files\gs\gs10.05.1\bin\gswin64c.exe",
#         r"C:\Program Files (x86)\gs\gs9.53.3\bin\gswin32c.exe",
#     ]
    
#     for path in gs_install_paths:
#         if os.path.exists(path):
#             return path
    
#     # 3. Если ничего не найдено
#     raise FileNotFoundError(
#         f"GhostScript не найден. Убедитесь, что он установлен в C:\\Program Files\\gs\\gs10.05.1\\bin"
#         f" и добавлен в PATH, или укажите полный путь к gswin64c.exe"
#     )



# def pdf_compression(filepath: str, remove_input_file=True) -> str:
#     try:
#         gs = _get_ghostscript_path()
#         input_file_abs_path = os.path.abspath(filepath)
#         output_file_abs_path = os.path.splitext(input_file_abs_path)[0] + "-compressed.pdf"
        
#         # Проверяем существование входного файла
#         if not os.path.exists(input_file_abs_path):
#             raise FileNotFoundError(f"Input PDF file not found: {input_file_abs_path}")
        
#         # Создаем пустой выходной файл
#         Path(output_file_abs_path).touch()
        
#         # Запускаем Ghostscript
#         subprocess.run(
#             [
#                 gs,
#                 "-sDEVICE=pdfwrite",
#                 "-dCompatibilityLevel=1.4",
#                 "-dPDFSETTINGS=/default",
#                 "-dNOPAUSE",
#                 "-dQUIET",
#                 "-dBATCH",
#                 f"-sOutputFile={output_file_abs_path}",
#                 input_file_abs_path,
#             ],
#             check=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#         )
        
#         if remove_input_file:
#             os.remove(input_file_abs_path)
            
#         return output_file_abs_path
        
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Ghostscript failed with error: {e.stderr.decode()}") from e
#     except Exception as e:
#         raise RuntimeError(f"PDF compression failed: {str(e)}") from e