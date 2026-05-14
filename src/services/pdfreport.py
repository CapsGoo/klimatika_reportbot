from enum import IntEnum, auto
from typing import Any, BinaryIO
from PIL import Image
import tempfile
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from io import BytesIO
import qrcode
from PIL import Image as PilImage

from .translator import translate_if_needed, detect_text_language
QR_SIZE = 150
QR_MARGIN = 20

from .reporttools import (
    FIRST_SLIDE, HEDING_FONT_SIZE, LAST_SLIDE, PDF_WIDTH, PDF_HEIGHT,
    PRE_LAST_SLIDE, REPORTS_PATH, Fonts, Indent, add_image, image_crop, pdf_compression
)

# Константы для единообразия стилей
class StyleConstants:
    # Размеры шрифтов
    ROOM_TITLE = HEDING_FONT_SIZE  # 80
    NODE_TITLE = 60
    SECTION_TITLE = 35
    REGULAR_TEXT = 30
    COMMENT_TEXT = 30
    MASTER_TEXT = 25
    SMALL_TEXT = 23
    
    # Цвета
    PRIMARY_COLOR = "#2082EA"
    SECONDARY_COLOR = "#6F7378"
    TEXT_COLOR = "#525252"
    ERROR_COLOR = "#FF0000"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    LIGHT_GRAY = "#E6E6E6"
    
    # Отступы и spacing
    SECTION_SPACING = 50
    LINE_SPACING = 20
    SMALL_SPACING = 15
    MARGIN = Indent.get_x()
    IMAGE_WIDTH = 720

PREMIUM_DESCRIPTION_POINTS = [
    "Deep cleaning of fan coil unit (VAV, blower fans, air-filter, evaporator coil, drain tray (if accessible))",
    "Check-up and adjustment of valves, fan belts, pulleys, coil, filter, strainer, pipe joints, insulation, bearings, drain trays, drain pipes and manometer tubes. VRV system errors\nand pressure check-up (as applicable to your type of property)",
    "Checking for noise, leaks, smell, vibration and general performance issues (for villas - refrigerant level check-up, board of roof-top AC unit control clean-up and check-up,\ncontrols calibrations checks)",
    "Check-up of thermostat (for villas – starters, relays and timers)",
    "Cleaning of above-ceiling areas (construction work left-overs clean-up, vacuum cleaning with special hose and brush, hand-washing with water)",
    "Disinfection with antibacterial detergent (ShieldMe)",
    "Using anti-dust protection curtains (Zipwall US)",
    "All works performed with german hand tools - DeWalt, Karcher.",
]

class WorkingFactors(IntEnum):
    CUMBERSOME_AND_DIFFICULT_ACCESS = auto()
    PROPERTY_ACCESS_PERMIT_NOT_APPLIED = auto()
    NOT_STANDART_SIZES_OR_DIFFICULTIES = auto()
    INSPECTION_ON_WEEKEND = auto()
    WORK_IN_OTHER_EMIRATE = auto()

WORKING_FACTORS_TEXT: dict[WorkingFactors, str] = {
    WorkingFactors.CUMBERSOME_AND_DIFFICULT_ACCESS: "Cumbersome and otherwise difficult access to units (ceiling access panels located far from AC units, access panels being less than\n60 cm and similar) which affected the overall time of works",
    WorkingFactors.PROPERTY_ACCESS_PERMIT_NOT_APPLIED: "Property access permit not applied for/provided/procured for by the Client in advance",
    WorkingFactors.NOT_STANDART_SIZES_OR_DIFFICULTIES: "Duct grills and/or diffusers are of the length more than 2 meters long and system has not been serviced for a long time",
    WorkingFactors.INSPECTION_ON_WEEKEND: "The inspection performed on a weekend or on a UAE National Holiday",
    WorkingFactors.WORK_IN_OTHER_EMIRATE: "The Client's premises are located outside Dubai, in other emirate",
}

HEREBY_WE = [
    "represent the outline of what we actually did where photos evidence that our services had been performed as shown to the best extent\npossible given the circumstances, access and work conditions;",
    "gaurantee that photos are genuine and had not been used from other clients' premises;",
    "kindly ask you to take into account that mild dust layer in the duct and some dirt in the trays/drain may add up very quickly (in 2-3 days\nafter cleaning) in the GCC region due to cliamte conditions and AC system work, this is normal and does not indicate that our services\nhave been performed loosely or unduly. Please provide evidence if you feel strong that it was our fault, otherwise we won't be able to\nprocess it in a proper way. For frivoulous claims not supported by convicing evidence we reserve the right to dispute such claims based\non this report and solely on the fact that no objections from your side were raised when you received this report and paid for our\nservices.",
    "kindly inform you if you do not raise any objections to what you see in this report or invoice within 24 hours after receiving this\nreport/invoice, we assume that you accept the works as they are depicted in photos in full and have no objections whatsoever.",
]


PDF_TEXTS: dict[str, str] = {
    "comments": "Comments: ",
    "nodes": "Nodes: ", 
    "master": "Master: ",
    "recommendation_immediate": "Recommendation for action immediately",
    "recommendation_normal": "Recommendation for actions in the next service",
}


# Добавьте в начало файла константы для типов узлов
class NodeTypes:
    SERVICE = "service"
    MAINTENANCE = "maintenance" 
    CHECKLIST = "checklist"

# Универсальная структура узла
def create_node_data(name: str, node_type: str, **kwargs) -> dict:
    """Создает унифицированную структуру данных для узла"""
    base_node = {
        "name": name,
        "type": node_type
    }
    base_node.update(kwargs)
    return base_node

class pdfGenerator:
    """Генератор PDF отчетов с унифицированными стилями и логикой"""

    def __init__(self, report_name: str = "report", target_language: str = None):
        self.report_name = report_name
        self.target_language = target_language
        self._cached_language = None
        
        # Инициализация кэша для переводов
        self._translation_cache = {}
        self._processed_nodes = set()  # Для отслеживания уже обработанных узлов
        
        self.canv = canvas.Canvas(
            f"{REPORTS_PATH}/{self.report_name}.pdf", 
            pagesize=(PDF_WIDTH, PDF_HEIGHT)
        )
        self._setup_fonts()


    def _get_cached_translation(self, text: str, target_lang: str) -> str:
        """Получает перевод из кэша или выполняет перевод"""
        cache_key = (text, target_lang)
        
        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]
        
        translated = translate_if_needed(text, target_lang)
        self._translation_cache[cache_key] = translated
        return translated

    def _detect_language_from_gettext(self, gettext_func) -> str:
        """Определяет язык из gettext функции через анализ объекта"""
        try:
            # Если это стандартный gettext объект
            if hasattr(gettext_func, '_lang'):
                return gettext_func._lang
            elif hasattr(gettext_func, 'language'):
                return gettext_func.language
            elif hasattr(gettext_func, '_current_domain'):
                # Для некоторых реализаций gettext
                return 'en'  # fallback
            
            # Анализ через тестовые фразы
            test_translation = gettext_func("Maintenance")
            if test_translation == "Обслуживание":
                return 'ru'
            elif test_translation == "الصيانة":
                return 'ar'
            elif test_translation == "Entretien":
                return 'fr'
            elif test_translation == "Wartung":
                return 'de'
            else:
                return 'en'  # английский по умолчанию
                
        except Exception as e:
            print(f"Language detection failed: {e}")
            return 'en'

    def _get_target_language(self, gettext_func) -> str:
        """Получает целевой язык с кэшированием"""
        if self._cached_language:
            return self._cached_language
            
        # Если язык явно задан, используем его
        if self.target_language:
            self._cached_language = self.target_language
            return self._cached_language
            
        # Определяем язык из gettext_func
        detected_lang = 'en'  # fallback
        if gettext_func and not gettext_func.__name__ == '<lambda>':
            detected_lang = self._detect_language_from_gettext(gettext_func)
        
        self._cached_language = detected_lang
        print(f"DEBUG: Cached language: {self._cached_language}")
        return self._cached_language

    def _translate_text(self, text: str, gettext_func=None) -> str:
        """Вспомогательный метод для перевода текста с учетом gettext_func"""
        if not text:
            return text
            
        target_lang = self._get_target_language(gettext_func)
        return translate_if_needed(text, target_lang)
    

    def _translate_room_name(self, room_name: str, gettext_func=None) -> str:
        """Переводит название комнаты с кэшированием"""
        if not room_name:
            return room_name
        
        target_lang = self._get_target_language(gettext_func)
        
        # Проверяем кэш для названий комнат
        cache_key = f"room_{room_name}_{target_lang}"
        
        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]
        
        # Переводим название комнаты
        translated = self._get_cached_translation(room_name, target_lang)
        self._translation_cache[cache_key] = translated
        
        # Логируем только если перевод изменил текст
        if room_name != translated:
            print(f"DEBUG: Translated room name: '{room_name}' -> '{translated}'")
        
        return translated


    def _process_comments_for_translation(self, room_data: dict, node_data: dict = None, gettext_func=None):
        """Обрабатывает комментарии для перевода с кэшированием"""
        if gettext_func is None:
            gettext_func = lambda x: x
        
        target_lang = self._get_target_language(gettext_func)
        
        # Переводим комментарий комнаты
        if room_data.get("room_comment"):
            original_comment = room_data["room_comment"]
            translated_comment = self._get_cached_translation(original_comment, target_lang)
            room_data["room_comment"] = translated_comment
            
            # Логируем только если перевод действительно произошел
            if original_comment != translated_comment:
                print(f"DEBUG: Translated room comment: '{original_comment[:30]}...' -> '{translated_comment[:30]}...'")
        
        # Переводим комментарии узлов
        if node_data and node_data.get("comment"):
            original_comment = node_data["comment"]
            translated_comment = self._get_cached_translation(original_comment, target_lang)
            node_data["comment"] = translated_comment
            
            if original_comment != translated_comment:
                print(f"DEBUG: Translated node comment: '{original_comment[:30]}...' -> '{translated_comment[:30]}...'")


    def _process_node_name_for_translation(self, node_data: dict, gettext_func=None):
        """Обрабатывает название узла для перевода с кэшированием"""
        if node_data.get("name"):
            target_lang = self._get_target_language(gettext_func)
            original_name = node_data["name"]
            
            # Используем кэшированный перевод
            translated_name = self._get_cached_translation(original_name, target_lang)
            node_data["name"] = translated_name
            
            # Логируем только реальные переводы
            if original_name != translated_name:
                print(f"DEBUG: Translated node name: '{original_name[:30]}...' -> '{translated_name[:30]}...'")

    def _setup_fonts(self):
        """Настройка шрифтов - вынесено в отдельный метод для чистоты"""
        fonts_to_register = [
            (Fonts.regular["name"], Fonts.regular["path"]),
            (Fonts.bold["name"], Fonts.bold["path"]),
            (Fonts.italics["name"], Fonts.italics["path"]),
            (Fonts.medium["name"], Fonts.medium["path"]),
            (Fonts.light["name"], Fonts.light["path"])
        ]
        
        for font_name, font_path in fonts_to_register:
            pdfmetrics.registerFont(TTFont(font_name, font_path))

    def _draw_room_title(self, room_name: str, y_pos: float) -> float:
        """Рисование названия комнаты"""
        return self._draw_centered_text(
            room_name, Fonts.bold["name"], 
            StyleConstants.ROOM_TITLE, y_pos
        )

    def _draw_text_line(self, text: str, font_name: str, size: int, 
                       x: float, y: float, color: str = StyleConstants.PRIMARY_COLOR):
        """Универсальный метод для рисования текста"""
        self.canv.setFont(font_name, size)
        self.canv.setFillColor(color)
        self.canv.drawString(x, y, text)
        return y - size - StyleConstants.LINE_SPACING

    def _draw_centered_text(self, text: str, font_name: str, size: int, 
                           y: float, color: str = StyleConstants.PRIMARY_COLOR):
        """Рисование текста по центру страницы"""
        text_width = self.canv.stringWidth(text, font_name, size)
        x = (PDF_WIDTH - text_width) / 2
        return self._draw_text_line(text, font_name, size, x, y, color)

    def _calculate_text_height(self, text: str, font: str, size: int, max_width: float) -> float:
        """Расчет высоты текста с переносами"""
        lines = self._wrap_text(text, font, size, max_width)
        return len(lines) * (size + StyleConstants.LINE_SPACING // 2)

    def bullet_list(self, textobject: canvas.PDFTextObject, str_list: list[str],
                   bullet_color: str, bullet_font_args: dict[str, Any],
                   text_color: str, text_font_args: dict[str, Any], leading: float):
        """Универсальный метод для списков с буллетами"""
        for line in str_list:
            textobject.setLeading(leading)
            textobject.setFillColor(bullet_color)
            textobject.setFont(**bullet_font_args)
            textobject.textOut("•  ")
            textobject.setFont(**text_font_args)
            textobject.setLeading(leading)
            textobject.setFillColor(text_color)
            
            new_line = line.split("\n")
            for i, part in enumerate(new_line):
                if i > 0:
                    textobject.textOut("    ")
                textobject.textLine(part)

    def _draw_wrapped_text(self, text: str, font: str, size: int, 
                        x: float, y: float, max_width: float, 
                        color: str = None) -> float:
        """Рисование текста с переносами и поддержкой цвета"""
        if color is None:
            color = StyleConstants.PRIMARY_COLOR  # Значение по умолчанию
        
        lines = self._wrap_text(text, font, size, max_width)
        for line in lines:
            self._draw_text_line(line, font, size, x, y, color)
            y -= size + StyleConstants.LINE_SPACING // 2
        return y

    def _wrap_text(self, text: str, font: str, size: int, max_width: float) -> list:
        """Перенос текста на несколько строк"""
        # Добавляем пробелы в местах, где они отсутствуют между словами
        # Исправляем слипшиеся слова
        import re
        # Добавляем пробел между словами, где нет пробела но есть переход с кириллицы/латиницы
        text = re.sub(r'([а-яА-ЯёЁ])([a-zA-Z])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z])([а-яА-ЯёЁ])', r'\1 \2', text)
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.canv.stringWidth(test_line, font, size) <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def _draw_master_info(self, master: str, x: float, gettext_func, y: float = None):
        """Рисование информации о мастере с указанием Y позиции"""
        if y is None:
            # Если Y не указан, используем стандартный отступ
            y = StyleConstants.MARGIN
        
        text = gettext_func("Master: ") + master
        
        return self._draw_text_line(
            text, Fonts.regular["name"], 
            StyleConstants.MASTER_TEXT, x, y, StyleConstants.BLACK
        )
    
    # def _handle_images(self, before: BinaryIO, after: BinaryIO):
    #     """Обработка изображений before/after"""
    #     images = []
    #     if before:
    #         images.append(image_crop(before))
    #     if after:
    #         images.append(image_crop(after))
        
    #     if len(images) == 2:
    #         add_image(self.canv, images[0], StyleConstants.IMAGE_WIDTH, 
    #                 StyleConstants.MARGIN, StyleConstants.MARGIN * 3)
    #         add_image(self.canv, images[1], StyleConstants.IMAGE_WIDTH, 
    #                 PDF_WIDTH - StyleConstants.IMAGE_WIDTH - StyleConstants.MARGIN, 
    #                 StyleConstants.MARGIN * 3)
    #     elif images:
    #         x_pos = (PDF_WIDTH - StyleConstants.IMAGE_WIDTH) / 2
    #         add_image(self.canv, images[0], StyleConstants.IMAGE_WIDTH, 
    #                 x_pos, StyleConstants.MARGIN * 3)
            

    def _handle_images(self, before: BinaryIO, after: BinaryIO, 
                      image_scale: float = 1.2, vertical_offset: float = 4):
        """Обработка изображений before/after с настройками"""
        images = []
        if before:
            images.append(image_crop(before))
        if after:
            images.append(image_crop(after))
        
        # Настраиваемые параметры
        BASE_IMAGE_WIDTH = StyleConstants.IMAGE_WIDTH * image_scale
        BASE_Y_POSITION = StyleConstants.MARGIN * vertical_offset
        SPACING =20  # расстояние между фото
        
        if len(images) == 2:
            # Автоматическое центрирование
            total_needed_width = BASE_IMAGE_WIDTH * 2 + SPACING
            available_width = PDF_WIDTH - (StyleConstants.MARGIN * 2)
            
            # Если фото слишком широкие, уменьшаем их
            if total_needed_width > available_width:
                BASE_IMAGE_WIDTH = (available_width - SPACING) / 2
            
            # Центрируем
            start_x = (PDF_WIDTH - (BASE_IMAGE_WIDTH * 2 + SPACING)) / 2
            
            # Левое фото
            add_image(self.canv, images[0], BASE_IMAGE_WIDTH, 
                    start_x, BASE_Y_POSITION)
            
            # Правое фото
            add_image(self.canv, images[1], BASE_IMAGE_WIDTH, 
                    start_x + BASE_IMAGE_WIDTH + SPACING, 
                    BASE_Y_POSITION)
            
        elif images:
            # Центрируем одно фото
            x_pos = (PDF_WIDTH - BASE_IMAGE_WIDTH) / 2
            add_image(self.canv, images[0], BASE_IMAGE_WIDTH, 
                    x_pos, BASE_Y_POSITION)


    def _draw_images_with_height(self, before: BinaryIO, after: BinaryIO, photo_top_y: float) -> tuple:
        """
        Рисует фотографии и возвращает (нижний_край_фото, высота_фото)
        photo_top_y - Y координата ВЕРХНЕГО края фотографий
        """
        images = []
        if before:
            images.append(image_crop(before))
        if after:
            images.append(image_crop(after))
        
        if not images:
            return (0, 0)  # нет фото
        
        IMAGE_WIDTH = StyleConstants.IMAGE_WIDTH
        SPACING = 40
        
        # Рассчитываем высоту фото
        img = images[0]
        img_w, img_h = img.size
        size_rel = img_h / img_w
        photo_height = int(IMAGE_WIDTH * size_rel)
        
        # Рассчитываем нижний край фото
        photo_bottom_y = photo_top_y - photo_height
        
        if len(images) == 2:
            # Центрируем два фото
            total_width = IMAGE_WIDTH * 2 + SPACING
            start_x = (PDF_WIDTH - total_width) / 2
            
            # Рисуем левое фото (нижний край = photo_bottom_y)
            add_image(self.canv, images[0], IMAGE_WIDTH, 
                    start_x, photo_bottom_y)  # ← НИЖНИЙ край!
            
            # Рисуем правое фото
            add_image(self.canv, images[1], IMAGE_WIDTH, 
                    start_x + IMAGE_WIDTH + SPACING, 
                    photo_bottom_y)  # ← НИЖНИЙ край!
            
        else:
            # Центрируем одно фото
            x_pos = (PDF_WIDTH - IMAGE_WIDTH) / 2
            add_image(self.canv, images[0], IMAGE_WIDTH, 
                    x_pos, photo_bottom_y)  # ← НИЖНИЙ край!
        
        return (photo_bottom_y, photo_height)
    

    def generate_qr_code(self, url: str) -> PilImage.Image:
        """Генерация QR кода"""
        if not url:
            return None
            
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        return qr.make_image(fill_color="black", back_color="white").resize((QR_SIZE, QR_SIZE))

    def add_qr_to_canvas(self, canv, qr_image: PilImage.Image, 
                        y_position: float, x_position: float = None):
        """Добавление QR кода на canvas"""
        if not qr_image:
            return
            
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            qr_image.save(tmp.name)
            canv.drawImage(tmp.name, x_position, y_position,
                          width=QR_SIZE, height=QR_SIZE,
                          mask='auto', preserveAspectRatio=True)
            tmp.close()
            os.unlink(tmp.name)


    def _draw_extra_services(self, textobject: canvas.PDFTextObject, 
                           extra_services: list, y_pos: float, gettext_func=None) -> float:
        """Рисование дополнительных услуг с поддержкой перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        textobject.setTextOrigin(StyleConstants.MARGIN, y_pos)
        textobject.setFillColor(StyleConstants.PRIMARY_COLOR)
        textobject.setFont(Fonts.bold["name"], 28)
        textobject.textLine(gettext_func("What we did extra:"))
        
        textobject.setFont(Fonts.regular["name"], 28)
        textobject.setXPos(28)
        
        self.bullet_list(
            textobject, extra_services,
            StyleConstants.SECONDARY_COLOR,
            {"psfontname": Fonts.bold["name"], "size": 30},
            StyleConstants.SECONDARY_COLOR,
            {"psfontname": Fonts.regular["name"], "size": 30},
            54
        )
        return y_pos - len(extra_services) * 54

    def _draw_working_factors(self, textobject: canvas.PDFTextObject, 
                            working_factors: list[str], gettext_func=None):
        """Рисование рабочих факторов с поддержкой перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        textobject.setFillColor(StyleConstants.PRIMARY_COLOR)
        textobject.setFont(Fonts.bold["name"], 28)
        textobject.textLine(gettext_func("Factors on your premises affecting the inspection time length and final price for our services:"))
        
        textobject.setFont(Fonts.regular["name"], 28)
        textobject.setXPos(28)
        
        self.bullet_list(
            textobject, working_factors,
            StyleConstants.SECONDARY_COLOR,
            {"psfontname": Fonts.bold["name"], "size": 30},
            StyleConstants.SECONDARY_COLOR,
            {"psfontname": Fonts.regular["name"], "size": 30},
            54
        )


    def first_slide(self, gettext_func=None):
        """Первая страница отчета с поддержкой перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        canv = self.canv
        img = Image.open(FIRST_SLIDE)
        add_image(canv, img, PDF_WIDTH, 0, 0)

        textobject = canv.beginText()
        textobject.setTextOrigin(StyleConstants.MARGIN, 791)
        textobject.setFillColor(StyleConstants.WHITE)
        textobject.setFont(Fonts.bold["name"], 88)

        textobject.textLine(text=gettext_func("Maintenance"))
        textobject.textLine(text=gettext_func("Service Completion"))
        textobject.textLine(text=gettext_func("Report"))

        # Информация о компании
        textobject.setFont(Fonts.regular["name"], 30)
        textobject.setTextOrigin(StyleConstants.MARGIN, 467)
        textobject.textOut(gettext_func("Presented by "))
        textobject.setFont(Fonts.bold["name"], 30)
        textobject.textOut("Andrei Nosikov ")
        textobject.setFont(Fonts.regular["name"], 30)
        textobject.textOut(gettext_func("of "))
        textobject.setFont(Fonts.bold["name"], 30)
        textobject.textLine(text="Klimatika AC and Refrigerator ")
        textobject.textOut(text="Maintenance LLC ")
        textobject.setFont(Fonts.regular["name"], 30)
        textobject.textLine(text=gettext_func(" (License# 1113949)"))

        # Слоган
        textobject.setFont(Fonts.regular["name"], 36)
        textobject.setTextOrigin(StyleConstants.MARGIN, 64)
        textobject.textOut(text=gettext_func("Learn how we help "))
        textobject.setFont(Fonts.bold["name"], 36)
        textobject.textOut(text=gettext_func("you breathe."))

        canv.drawText(textobject)
        canv.showPage()

    def summary_first(self, date: str, name: str, phone_number: str, address: str,
                     performed_service: str, summary_num: int, gettext_func=None):
        """Первая страница summary с поддержкой перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        canv = self.canv
        textobject = canv.beginText()

        # Заголовок с переводом
        summary_text = gettext_func("Summary ({} of {})").format(summary_num, 3 if summary_num == 1 else 2)
        textobject.setTextOrigin(StyleConstants.MARGIN, 959)
        textobject.setFont(Fonts.bold["name"], HEDING_FONT_SIZE)
        textobject.setFillColor(StyleConstants.PRIMARY_COLOR)
        textobject.textLine(summary_text)

        # Основная информация с переведенными labels
        info_data = [
            (gettext_func("Date:  "), date),
            (gettext_func("Name:  "), name),
            (gettext_func("Phone number:  "), phone_number),
            (gettext_func("Address:  "), address),
            (gettext_func("Performed services:  "), performed_service)
        ]

        y_position = 880
        for label, value in info_data:
            textobject.setTextOrigin(StyleConstants.MARGIN, y_position)
            textobject.setFillColor(StyleConstants.PRIMARY_COLOR)
            textobject.setFont(Fonts.bold["name"], 29)
            textobject.textOut(label)
            textobject.setFont(Fonts.regular["name"], 29)
            textobject.setFillColor(StyleConstants.SECONDARY_COLOR)
            textobject.textLine(value)
            y_position -= 55

        # Описание услуги с переводом
        textobject.setTextOrigin(StyleConstants.MARGIN, 588)
        textobject.setFillColor(StyleConstants.PRIMARY_COLOR)
        textobject.setFont(Fonts.bold["name"], 23)
        textobject.textOut(gettext_func("Description:"))
        
        textobject.setTextOrigin(StyleConstants.MARGIN, 533)
        textobject.setFont(Fonts.regular["name"], 23)
        textobject.setFillColor(StyleConstants.TEXT_COLOR)

        if "Premium" in performed_service:
            textobject.textLine(gettext_func("Premium cleaning service included:"))
            textobject.setTextOrigin(StyleConstants.MARGIN + 15, 489)
            
            # Переводим каждый пункт PREMIUM_DESCRIPTION_POINTS
            translated_points = [gettext_func(point) for point in PREMIUM_DESCRIPTION_POINTS]
            self.bullet_list(
                textobject, translated_points,
                StyleConstants.PRIMARY_COLOR,
                {"psfontname": Fonts.bold["name"], "size": 23},
                StyleConstants.TEXT_COLOR,
                {"psfontname": Fonts.regular["name"], "size": 23}, 43
            )
        else:
            textobject.textLine(gettext_func("Minor repairs around the house, not related to the repair of air conditioners and ventilation"))

        canv.drawText(textobject)
        canv.showPage()

    

    def summary_second(self, extra_services: list, working_factors: list[WorkingFactors], gettext_func=None):
        """Вторая страница summary с поддержкой перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        canv = self.canv
        textobject = canv.beginText()
        
        textobject.setTextOrigin(StyleConstants.MARGIN, 959)
        textobject.setFont(Fonts.bold["name"], HEDING_FONT_SIZE)
        textobject.setFillColor(StyleConstants.PRIMARY_COLOR)
        textobject.textLine(gettext_func("Summary (2 of 3)"))

        y_pos = 844
        if extra_services:
            y_pos = self._draw_extra_services(textobject, extra_services, y_pos, gettext_func)
            textobject.setTextOrigin(StyleConstants.MARGIN, 492)

        if working_factors:
            self._draw_working_factors(textobject, working_factors, gettext_func)

        canv.drawText(textobject)
        canv.showPage()


    def summary_third(self, summary_num: int, gettext_func=None):
        """Третья страница summary с поддержкой перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        canv = self.canv
        textobject = canv.beginText()

        summary_text = gettext_func("Summary ({} of {})").format(summary_num, 3 if summary_num == 3 else 2)
        textobject.setTextOrigin(StyleConstants.MARGIN, 959)
        textobject.setFont(Fonts.bold["name"], HEDING_FONT_SIZE)
        textobject.setFillColor(StyleConstants.PRIMARY_COLOR)
        textobject.textLine(summary_text)

        # Уменьшаем отступ между Summary и Hereby we: в 2 раза
        # Было: 959 - 833 = 126, теперь сделаем ~60
        textobject.setTextOrigin(StyleConstants.MARGIN, 899)  # Было 833
        textobject.setFont(Fonts.bold["name"], 50)
        textobject.textLine(gettext_func("Hereby we:"))

        # Уменьшаем отступ между Hereby we: и первым пунктом в 2 раза
        # Было: 833 - 755 = 78, теперь сделаем ~40
        textobject.setTextOrigin(75, 859)  # Было 755
        textobject.setFont(Fonts.regular["name"], 29)

        # Переводим каждый пункт HEREBY_WE
        translated_hereby_we = [gettext_func(point) for point in HEREBY_WE]
        self.bullet_list(
            textobject, translated_hereby_we,
            StyleConstants.PRIMARY_COLOR,
            {"psfontname": Fonts.bold["name"], "size": 29},
            StyleConstants.TEXT_COLOR,
            {"psfontname": Fonts.regular["name"], "size": 29},
            55
        )

        # Также уменьшаем отступ для последнего пункта
        textobject.setFont(Fonts.bold["name"], 29)
        textobject.setFillColor(StyleConstants.PRIMARY_COLOR)
        textobject.textOut("• ")
        textobject.textLine(gettext_func("highly recommend that you have your AC units and Duct system serviced at least 3-4 times a year, so that you enjoy fresh air,"))
        textobject.textLine(gettext_func("system work properly and you pay less for electricity bills or AC repair."))

        canv.drawText(textobject)
        canv.showPage()

    def summary_slides(self, date: str, name: str, phone_number: str, address: str,
                      performed_service: str, extra_services: list, working_factors: list, gettext_func=None):
        """Генерация всех summary страниц с поддержкой перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        has_extra_content = bool(extra_services or working_factors)
        
        self.summary_first(date, name, phone_number, address, performed_service, 
                         1 if has_extra_content else 2, gettext_func)
        
        if has_extra_content:
            self.summary_second(extra_services, working_factors, gettext_func)
            self.summary_third(3, gettext_func)
        else:
            self.summary_third(2, gettext_func)


    def room_service_slide(self, node_name: str, before: BinaryIO, after: BinaryIO,
                        room_name: str, comment: str = None, video_url: str = None,
                        room_master: str = None, gettext_func=None):
        """Слайд сервисного отчета - комментарий и мастер под фотографиями"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        # 1. Сначала рисуем заголовки вверху
        y_pos = PDF_HEIGHT - StyleConstants.MARGIN * 2
        
        # Заголовок комнаты
        y_pos = self._draw_room_title(room_name, y_pos)
        y_pos += 30
        
        # Название узла с переводом
        before_after_text = gettext_func("BEFORE and AFTER {}").format(node_name)
        y_pos = self._draw_centered_text(
            before_after_text, Fonts.bold["name"],
            StyleConstants.NODE_TITLE, y_pos
        )
        
        # 2. Определяем где будет ВЕРХ фотографий
        # Оставляем отступ от заголовка узла до верха фото
        photo_top_y = y_pos - StyleConstants.NODE_TITLE + 80 
        
        # Рисуем фото и получаем их нижний край и высоту
        photo_bottom_y, photo_height = self._draw_images_with_height(before, after, photo_top_y)
        
        # 3. "RECOMMENDATIONS AND COMMENTS" - ПОД фотографиями
        # Отступаем от нижнего края фото
        text_start_y = photo_bottom_y - 60  # 80px отступ от нижнего края фото
        
        # "RECOMMENDATIONS AND COMMENTS" (синий, по центру)
        recommendations_text = gettext_func("Recommendations and comments")
        
        # Сохраняем позицию для QR кода
        recommendations_y = text_start_y
        
        text_start_y = self._draw_centered_text(
            recommendations_text,
            Fonts.bold["name"],
            StyleConstants.SECTION_TITLE,
            text_start_y,
            StyleConstants.PRIMARY_COLOR
        )
        text_start_y -= StyleConstants.SECTION_SPACING

        # 4. КОММЕНТАРИЙ (синий) - слева с увеличенным отступом
        if comment:
            # Максимальная ширина для текста (с учетом QR кода справа)
            MAX_TEXT_WIDTH = PDF_WIDTH - StyleConstants.SMALL_SPACING * 2 - QR_SIZE
            
            comment_lines = self._wrap_text(
                comment,
                Fonts.regular["name"],
                StyleConstants.COMMENT_TEXT,
                MAX_TEXT_WIDTH
            )
            
            # Рисуем каждую строку комментария
            for line in comment_lines:
                self._draw_text_line(
                    line,
                    Fonts.regular["name"],
                    StyleConstants.COMMENT_TEXT,
                    StyleConstants.MARGIN * 2,  # Увеличенный отступ слева
                    text_start_y +40 ,
                    StyleConstants.PRIMARY_COLOR
                )
                text_start_y -= StyleConstants.COMMENT_TEXT + StyleConstants.LINE_SPACING // 2
        
        # 5. QR код - справа на уровне "RECOMMENDATIONS AND COMMENTS"
        if video_url:
            qr_image = self.generate_qr_code(video_url)
            if qr_image:
                # QR код на уровне заголовка "RECOMMENDATIONS AND COMMENTS"
                qr_y = recommendations_y - QR_SIZE // 2
                self.add_qr_to_canvas(self.canv, qr_image, qr_y,
                                    PDF_WIDTH - QR_SIZE - StyleConstants.MARGIN * 2)
        
        # 6. Мастер - В САМОМ НИЗУ страницы
        if room_master:
            # Располагаем мастера в самом низу, над нижним отступом
            master_y = StyleConstants.MARGIN * 2
            self._draw_master_info(room_master, StyleConstants.MARGIN, gettext_func, master_y)

        self.canv.showPage()


    def room_maintenance_slide(self, node_name: str, before: BinaryIO, after: BinaryIO,
                             room_name: str, master: str, room_comment: str = None,
                             room_video_url: str = None, gettext_func=None):
        """Слайд отчета по техническому обслуживанию с автоматическим переводом комментариев"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        self._handle_images(before, after)
        
        # Заголовок комнаты
        y_pos = self._draw_room_title(room_name, PDF_HEIGHT - StyleConstants.MARGIN * 2)
        
        before_after_text = gettext_func("BEFORE and AFTER {}").format(node_name)
        y_pos = self._draw_centered_text(
            before_after_text, Fonts.bold["name"],
            StyleConstants.NODE_TITLE, y_pos
        )
        # # Комментарий к комнате с автоматическим переводом если нужно
        # if room_comment:
        #     # room_comment уже переведен в _process_maintenance_nodes
        #     comment_text = gettext_func("Room Comments: {}").format(room_comment)
        #     y_pos = self._draw_text_line(
        #         comment_text, Fonts.regular["name"],
        #         StyleConstants.COMMENT_TEXT, StyleConstants.MARGIN, y_pos
        #     )

        # # QR код для видео комнаты
        # if room_video_url:
        #     qr_image = self.generate_qr_code(room_video_url)
        #     if qr_image:
        #         self.add_qr_to_canvas(self.canv, qr_image, StyleConstants.MARGIN * 2,
        #                              PDF_WIDTH - QR_SIZE - QR_MARGIN)

        # # Мастер
        # self._draw_master_info(master, StyleConstants.MARGIN, gettext_func)

        self.canv.showPage()

    def room_check_list_slide(self, node_name: str, before: BinaryIO,
                            room_name: str, master: str, check_list_factors: str,
                            gettext_func=None):
        """Слайд контрольного списка с поддержкой перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        canv = self.canv
        
        # ============= НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ =============
        # Размеры шрифтов
        ROOM_TITLE_SIZE = StyleConstants.ROOM_TITLE  # 80
        SECTION_TITLE_SIZE = 45                      # "Recommendation for action immediately"
        NODE_TEXT_SIZE = 35                          # Название узла с точкой
        MASTER_TEXT_SIZE = 30                        # Мастер
        
        # Цвета
        ROOM_TITLE_COLOR = StyleConstants.PRIMARY_COLOR    # Синий
        IMMEDIATE_TITLE_COLOR = StyleConstants.ERROR_COLOR # Красный
        NORMAL_TITLE_COLOR = StyleConstants.PRIMARY_COLOR  # Синий
        NODE_TEXT_COLOR = StyleConstants.TEXT_COLOR        # Темно-серый
        MASTER_TEXT_COLOR = StyleConstants.PRIMARY_COLOR   # Синий
        
        # Отступы (оптимизированы для идеального расположения)
        TITLE_MARGIN_TOP = StyleConstants.MARGIN * 2       # Отступ сверху
        ROOM_TITLE_SPACING = 8                            # Отступ после названия комнаты
        RECOMMENDATION_Y_POSITION = 250                   # Идеальная позиция Y для рекомендации (найдена экспериментально)
        SECTION_SPACING = 4                               # Отступ между секциями
        ITEM_SPACING = 3                                  # Отступ между элементами
        NODE_INDENT = StyleConstants.MARGIN * 1.5         # Отступ для узла с точкой
        MASTER_LEFT_MARGIN = StyleConstants.MARGIN        # Отступ слева для мастера
        MASTER_BOTTOM_MARGIN = StyleConstants.MARGIN      # Отступ снизу для мастера
        
        # Настройки изображений
        IMAGE_SCALE = 1.2                                 # Масштаб изображений
        VERTICAL_OFFSET = 6                               # Вертикальный отступ для фото
        # =================================================
        
        # 1. НАЗВАНИЕ КОМНАТЫ (по центру)
        room_name_width = canv.stringWidth(room_name, Fonts.bold["name"], ROOM_TITLE_SIZE)
        room_x = (PDF_WIDTH - room_name_width) / 2
        y_pos = PDF_HEIGHT - TITLE_MARGIN_TOP
        
        y_pos = self._draw_text_line(room_name, Fonts.bold["name"],
                                ROOM_TITLE_SIZE, room_x, y_pos,
                                ROOM_TITLE_COLOR)
        y_pos -= ROOM_TITLE_SPACING
        
        # 2. ОБРАБОТКА ИЗОБРАЖЕНИЙ С ПОМОЩЬЮ _handle_images
        if before:
            # Рисуем фото с помощью _handle_images
            self._handle_images(before, None, IMAGE_SCALE, VERTICAL_OFFSET)
            
            # Идеальная позиция для текста рекомендации
            y_pos = RECOMMENDATION_Y_POSITION
        
        # 3. РЕКОМЕНДАЦИЯ (слева) - с цветом в зависимости от типа
        if check_list_factors == 'immediate':
            recommendation_text = gettext_func(PDF_TEXTS["recommendation_immediate"])
            recommendation_color = IMMEDIATE_TITLE_COLOR
        else:
            recommendation_text = gettext_func(PDF_TEXTS["recommendation_normal"])
            recommendation_color = NORMAL_TITLE_COLOR
        
        y_pos = self._draw_text_line(recommendation_text, Fonts.bold["name"],
                                SECTION_TITLE_SIZE, StyleConstants.MARGIN, y_pos,
                                recommendation_color)
        y_pos -= ITEM_SPACING
        
        # 4. НАЗВАНИЕ УЗЛА С ТОЧКОЙ (с отступом)
        node_text = "• " + node_name
        y_pos = self._draw_text_line(node_text, Fonts.regular["name"],
                                NODE_TEXT_SIZE, NODE_INDENT, y_pos,
                                NODE_TEXT_COLOR)
        y_pos -= SECTION_SPACING * 2
        
        # 5. МАСТЕР (слева) - всегда помещается благодаря маленькому размеру
        master_text = gettext_func("Master: ") + master
        
        # Проверяем, достаточно ли места для мастера
        min_y_position = MASTER_BOTTOM_MARGIN + MASTER_TEXT_SIZE
        if y_pos < min_y_position:
            y_pos = min_y_position
        
        # Мастер на текущей странице
        y_pos = self._draw_text_line(master_text, Fonts.bold["name"],
                                MASTER_TEXT_SIZE, MASTER_LEFT_MARGIN, y_pos,
                                MASTER_TEXT_COLOR)

        canv.showPage()

        
    def _draw_centered_text_line(self, text: str, font: str, size: int, y: float, color: str):
        """Рисует текст по центру страницы"""
        text_width = self.canv.stringWidth(text, font, size)
        x = (PDF_WIDTH - text_width) / 2
        return self._draw_text_line(text, font, size, x, y, color)


    def create_grouped_slides(self, grouped_nodes: list, gettext_func=None):
        """Группированные слайды для узлов без фото в новом формате"""
        if gettext_func is None:
            gettext_func = lambda x: x
                
        canv = self.canv

        # ============= НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ =============
        # Размеры шрифтов
        ROOM_TITLE_SIZE = StyleConstants.ROOM_TITLE  # 80
        NODE_TITLE_SIZE = StyleConstants.NODE_TITLE  # 60
        SECTION_TITLE_SIZE = 45 # 45
        COMMENT_SIZE = 35 # 25
        MASTER_SIZE = StyleConstants.REGULAR_TEXT  # 23
        
        # Цвета
        ROOM_TITLE_COLOR = StyleConstants.PRIMARY_COLOR    # Синий
        NODE_TITLE_COLOR = StyleConstants.PRIMARY_COLOR    # Синий
        SECTION_TITLE_COLOR = StyleConstants.PRIMARY_COLOR # Синий
        COMMENT_TEXT_COLOR = StyleConstants.TEXT_COLOR     # Темно-серый
        MASTER_TEXT_COLOR = StyleConstants.PRIMARY_COLOR   # Синий
        
        # Отступы (настраиваемые между разными типами текста)
        TITLE_MARGIN_TOP = StyleConstants.MARGIN * 2       # Отступ сверху для названия комнаты
        ROOM_TITLE_SPACING = 80                           # Отступ после названия комнаты
        NODE_TITLE_SPACING = 0                          # Уменьшено: отступ после названия узла (было 20)
        SECTION_TITLE_SPACING = 0                     # Уменьшено: отступ после заголовка рекомендаций (было 20)
        COMMENT_LINE_SPACING = 15                       # Отступ между строками комментария
        BETWEEN_NODES_SPACING = 60                     # Уменьшено: отступ между разными узлами (было 20)
        MASTER_TOP_SPACING = 20                           # Отступ перед мастером
        MASTER_BOTTOM_MARGIN = StyleConstants.MARGIN * 2  # Отступ снизу для мастера
        
        # QR код
        QR_SIZE = 100
        QR_SPACING = 15
        QR_RIGHT_MARGIN = StyleConstants.MARGIN * 3       # Отступ справа для QR
        
        # Максимальные значения
        MAX_TEXT_WIDTH = PDF_WIDTH - QR_SIZE - QR_RIGHT_MARGIN - StyleConstants.MARGIN * 2
        MAX_NODES_PER_PAGE = 3
        # =================================================
        
        for room_data in grouped_nodes:
            room_name = room_data["room_name"]
            room_nodes = room_data["nodes"]
            master = room_data["room_master"]
            
            # Перевод комментариев
            translated_nodes = []
            for node in room_nodes:
                node_copy = node.copy()
                if node_copy.get("comment"):
                    original_comment = node_copy["comment"]
                    node_copy["comment"] = self._translate_text(original_comment, gettext_func)
                translated_nodes.append(node_copy)
            
            # Начинаем новую страницу для комнаты
            canv.setFillColorRGB(1, 1, 1)
            canv.rect(0, 0, PDF_WIDTH, PDF_HEIGHT, stroke=0, fill=1)
            y_pos = PDF_HEIGHT - TITLE_MARGIN_TOP
            
            nodes_on_current_page = 0
            
            # 1. НАЗВАНИЕ КОМНАТЫ (по центру) - Size: ROOM_TITLE_SIZE, Color: ROOM_TITLE_COLOR
            room_name_width = canv.stringWidth(room_name, Fonts.bold["name"], ROOM_TITLE_SIZE)
            room_x = (PDF_WIDTH - room_name_width) / 2
            self._draw_text_line(room_name, Fonts.bold["name"], ROOM_TITLE_SIZE, 
                            room_x, y_pos, ROOM_TITLE_COLOR)
            y_pos -= ROOM_TITLE_SPACING
            
            # ОБРАБОТКА КАЖДОГО УЗЛА
            for node_idx, node in enumerate(translated_nodes):
                # Проверяем, не превышен ли лимит узлов на странице
                if nodes_on_current_page >= MAX_NODES_PER_PAGE:
                    # 6. МАСТЕР (по центру) - Size: MASTER_SIZE, Color: MASTER_TEXT_COLOR
                    master_text = gettext_func(PDF_TEXTS["master"]) + master
                    master_width = canv.stringWidth(master_text, Fonts.regular["name"], MASTER_SIZE)
                    x_center = (PDF_WIDTH - master_width) / 2
                    
                    if y_pos - MASTER_SIZE - MASTER_BOTTOM_MARGIN >= StyleConstants.MARGIN:
                        y_pos = self._draw_text_line(master_text, Fonts.regular["name"], 
                                                MASTER_SIZE, x_center, y_pos, MASTER_TEXT_COLOR)
                    
                    # Новая страница
                    canv.showPage()
                    canv.setFillColorRGB(1, 1, 1)
                    canv.rect(0, 0, PDF_WIDTH, PDF_HEIGHT, stroke=0, fill=1)
                    y_pos = PDF_HEIGHT - TITLE_MARGIN_TOP
                    nodes_on_current_page = 0
                    
                    # Повторяем название комнаты на новой странице
                    room_name_width = canv.stringWidth(room_name, Fonts.bold["name"], ROOM_TITLE_SIZE)
                    room_x = (PDF_WIDTH - room_name_width) / 2
                    self._draw_text_line(room_name, Fonts.bold["name"], ROOM_TITLE_SIZE, 
                                    room_x, y_pos, ROOM_TITLE_COLOR)
                    y_pos -= ROOM_TITLE_SPACING
                
                # 2. НАЗВАНИЕ УЗЛА (по центру) - Size: NODE_TITLE_SIZE, Color: NODE_TITLE_COLOR
                node_title = node["name"]
                node_title_width = canv.stringWidth(node_title, Fonts.bold["name"], NODE_TITLE_SIZE)
                x_center = (PDF_WIDTH - node_title_width) / 2
                
                # Сохраняем Y позицию названия узла для расчета позиции QR
                node_title_y = y_pos
                
                y_pos = self._draw_text_line(node_title, Fonts.bold["name"], NODE_TITLE_SIZE, 
                                        x_center, y_pos, NODE_TITLE_COLOR)
                y_pos -= NODE_TITLE_SPACING  # Уменьшено расстояние
                
                # 3. "RECOMMENDATIONS AND COMMENTS" (по центру) - Size: SECTION_TITLE_SIZE, Color: SECTION_TITLE_COLOR
                recommendations_text = gettext_func("Recommendations and comments")
                rec_width = canv.stringWidth(recommendations_text, Fonts.bold["name"], SECTION_TITLE_SIZE)
                x_center = (PDF_WIDTH - rec_width) / 2
                
                # Сохраняем Y позицию для заголовка
                recommendations_y = y_pos
                
                y_pos = self._draw_text_line(recommendations_text, Fonts.bold["name"], SECTION_TITLE_SIZE, 
                                        x_center, y_pos, SECTION_TITLE_COLOR)
                y_pos -= SECTION_TITLE_SPACING  # Уменьшено расстояние
                
                # 4. QR КОД (справа) - если есть видео URL
                video_url = node.get("video_url") or node.get("url_video")
                if video_url:
                    qr_image = self.generate_qr_code(video_url)
                    if qr_image:
                        # Вычисляем середину между названием узла и заголовком
                        middle_y = node_title_y - NODE_TITLE_SIZE / 2  # Центр названия узла
                        qr_y = middle_y - QR_SIZE / 2  # Центрируем QR
                        
                        # Позиция справа с отступом
                        qr_x = PDF_WIDTH - QR_SIZE - QR_RIGHT_MARGIN
                        
                        # Добавляем QR код на canvas
                        self.add_qr_to_canvas(canv, qr_image, qr_y, qr_x)
                
                # 5. КОММЕНТАРИЙ (слева с отступом) - Size: COMMENT_SIZE, Color: COMMENT_TEXT_COLOR
                if node.get("comment"):
                    comment_y = y_pos
                    comment_lines = self._wrap_text(node["comment"], Fonts.regular["name"], 
                                                COMMENT_SIZE, MAX_TEXT_WIDTH)
                    
                    for line in comment_lines:
                        self._draw_text_line(line, Fonts.regular["name"], COMMENT_SIZE, 
                                        StyleConstants.MARGIN * 2, comment_y, COMMENT_TEXT_COLOR)
                        comment_y -= COMMENT_SIZE + COMMENT_LINE_SPACING // 2
                    
                    y_pos = comment_y
                
                nodes_on_current_page += 1
                
                # Отступ между узлами, если это не последний узел
                if node_idx < len(translated_nodes) - 1:
                    y_pos -= BETWEEN_NODES_SPACING  # Уменьшено расстояние
            
            # 6. МАСТЕР (по центру) - Size: MASTER_SIZE, Color: MASTER_TEXT_COLOR
            master_text = gettext_func(PDF_TEXTS["master"]) + master
            master_width = canv.stringWidth(master_text, Fonts.regular["name"], MASTER_SIZE)
            x_center = (PDF_WIDTH - master_width) / 2
            
            # Проверяем, достаточно ли места для мастера
            if y_pos - MASTER_SIZE - MASTER_BOTTOM_MARGIN >= StyleConstants.MARGIN:
                y_pos = self._draw_text_line(master_text, Fonts.regular["name"], 
                                        MASTER_SIZE, x_center, y_pos, MASTER_TEXT_COLOR)
            else:
                # Если не хватает места, создаем новую страницу для мастера
                canv.showPage()
                canv.setFillColorRGB(1, 1, 1)
                canv.rect(0, 0, PDF_WIDTH, PDF_HEIGHT, stroke=0, fill=1)
                y_pos = PDF_HEIGHT - TITLE_MARGIN_TOP
                y_pos = self._draw_text_line(master_text, Fonts.regular["name"], 
                                        MASTER_SIZE, x_center, y_pos, MASTER_TEXT_COLOR)
            
            # Новая страница для следующей комнаты, если это не последняя комната
            if room_data != grouped_nodes[-1]:
                canv.showPage()
        
        canv.showPage()


    def create_maintenance_summary_slides(self, maintenance_nodes: list, gettext_func=None):
        """Summary страницы для технического обслуживания - показывает все комнаты"""
        if gettext_func is None:
            gettext_func = lambda x: x
                        
        canv = self.canv
        
        # ============= НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ =============
        # Размеры шрифтов
        ROOM_TITLE_SIZE = StyleConstants.ROOM_TITLE  # 80
        SECTION_TITLE_SIZE = 55  # "Other service without photo:", "Recommendations and comments"
        NODE_TEXT_SIZE = 45      # Названия узлов (diffuser, condenser и т.д.)
        COMMENT_TEXT_SIZE = 45   # Текст рекомендаций
        MASTER_TEXT_SIZE = 55    # Мастер
        
        # Цвета
        ROOM_TITLE_COLOR = StyleConstants.PRIMARY_COLOR    # Синий
        SECTION_TITLE_COLOR = StyleConstants.PRIMARY_COLOR  # Синий 
        NODE_TEXT_COLOR = StyleConstants.TEXT_COLOR        # Темно-серый
        COMMENT_TEXT_COLOR = StyleConstants.TEXT_COLOR     # Темно-серый
        MASTER_TEXT_COLOR = StyleConstants.PRIMARY_COLOR   # Синий
        
        # Отступы
        TITLE_MARGIN_TOP = StyleConstants.MARGIN * 2       # Отступ сверху
        ROOM_TITLE_SPACING = 80                           # Отступ после названия комнаты
        BETWEEN_SECTIONS_SPACING = 6                       # Отступ между секциями
        BETWEEN_ITEMS_SPACING = 6                          # Отступ между элементами
        BETWEEN_LINES_SPACING = 4                          # Отступ между строками
        ITEM_INDENT = StyleConstants.MARGIN * 1.5          # Отступ для элементов списка
        MASTER_LEFT_MARGIN = StyleConstants.MARGIN         # Отступ слева для мастера
        
        # QR код
        QR_SIZE = 100  # Размер QR кода
        QR_BOTTOM_MARGIN = StyleConstants.MARGIN * 2  # Отступ снизу для QR
        QR_RIGHT_MARGIN = StyleConstants.MARGIN * 2   # Отступ справа для QR
        
        # ПАГИНАЦИЯ
        MAX_NODES_PER_PAGE = 5  # Максимальное количество узлов на странице
        # =================================================
        
        # Флаг для отслеживания первой страницы отчета
        is_first_page_of_section = True

        for room_idx, room_data in enumerate(maintenance_nodes):
            # Извлекаем данные комнаты
            room_name = room_data["room_name"]
            room_master = room_data["room_master"]
            room_comment = room_data.get("room_comment")
            room_video_url = room_data.get("room_video_url")
            nodes = room_data["nodes"]
            
            # Вычисляем количество страниц для этой комнаты
            if len(nodes) > 0:
                # Есть узлы - обычная пагинация
                num_pages = (len(nodes) + MAX_NODES_PER_PAGE - 1) // MAX_NODES_PER_PAGE
            else:
                # Нет узлов - создаем одну пустую страницу
                num_pages = 1
            
            for page_num in range(num_pages):
                # Определяем узлы для текущей страницы
                if len(nodes) > 0:
                    start_idx = page_num * MAX_NODES_PER_PAGE
                    page_nodes = nodes[start_idx:start_idx + MAX_NODES_PER_PAGE]
                else:
                    # Пустой список узлов
                    page_nodes = []
                
                is_first_page = (page_num == 0)  # ← Это ПЕРВАЯ СТРАНИЦА ГРУППЫ УЗЛОВ!
                            
                # Новая страница ТОЛЬКО если это не первая страница раздела
                if not is_first_page_of_section:
                    canv.showPage()
                
                is_first_page_of_section = False
                
                # Очищаем страницу (как в create_grouped_slides)
                canv.setFillColorRGB(1, 1, 1)
                canv.rect(0, 0, PDF_WIDTH, PDF_HEIGHT, stroke=0, fill=1)
                
                y_pos = PDF_HEIGHT - TITLE_MARGIN_TOP
                
                # 1. НАЗВАНИЕ КОМНАТЫ (по центру)
                room_name_width = canv.stringWidth(room_name, Fonts.bold["name"], ROOM_TITLE_SIZE)
                room_x = (PDF_WIDTH - room_name_width) / 2
                self._draw_text_line(room_name, Fonts.bold["name"], ROOM_TITLE_SIZE, 
                                room_x, y_pos, ROOM_TITLE_COLOR)
                y_pos -= ROOM_TITLE_SPACING
                
                # 2. "Other service without photo:" (слева, на каждой странице)
                other_service_text = gettext_func("Other service without photo:")
                y_pos = self._draw_text_line(other_service_text, Fonts.bold["name"],
                                        SECTION_TITLE_SIZE, StyleConstants.MARGIN, y_pos,
                                        SECTION_TITLE_COLOR)
                y_pos -= BETWEEN_ITEMS_SPACING
                
                # 3. СПИСОК УЗЛОВ ТЕКУЩЕЙ СТРАНИЦЫ (может быть пустым)
                if page_nodes:
                    for node in page_nodes:
                        node_name = node["name"]
                        y_pos = self._draw_text_line("• " + node_name, Fonts.regular["name"],
                                                NODE_TEXT_SIZE, 
                                                ITEM_INDENT, y_pos,
                                                NODE_TEXT_COLOR)
                        y_pos -= BETWEEN_LINES_SPACING
                    
                    y_pos -= BETWEEN_SECTIONS_SPACING
                else:
                    no_nodes_text = gettext_func("No nodes")
                    y_pos = self._draw_text_line("•" + no_nodes_text, Fonts.regular["name"],
                                            NODE_TEXT_SIZE, 
                                            ITEM_INDENT, y_pos,
                                            NODE_TEXT_COLOR)
                    y_pos -= BETWEEN_SECTIONS_SPACING
                
                # 4. "Recommendations and comments" и КОММЕНТАРИЙ (ТОЛЬКО на первой странице)
                if is_first_page and room_comment:
                    recommendations_text = gettext_func("Recommendations and comments")
                    y_pos = self._draw_text_line(recommendations_text, Fonts.bold["name"],
                                            SECTION_TITLE_SIZE, StyleConstants.MARGIN, y_pos,
                                            ROOM_TITLE_COLOR)
                    y_pos -= BETWEEN_ITEMS_SPACING
                    
                    # Разбиваем комментарий на строки
                    comment_lines = self._wrap_text(room_comment, Fonts.regular["name"],
                                                COMMENT_TEXT_SIZE,
                                                PDF_WIDTH - ITEM_INDENT * 2)
                    
                    for line in comment_lines:
                        y_pos = self._draw_text_line(line, Fonts.regular["name"],
                                                COMMENT_TEXT_SIZE, 
                                                ITEM_INDENT, y_pos,
                                                COMMENT_TEXT_COLOR)
                        y_pos -= BETWEEN_LINES_SPACING
                    
                    y_pos -= BETWEEN_SECTIONS_SPACING
                
                # 5. МАСТЕР (слева, на каждой странице)
                master_text = gettext_func("Master: ") + room_master
                y_pos = self._draw_text_line(master_text, Fonts.bold["name"],
                                        MASTER_TEXT_SIZE, MASTER_LEFT_MARGIN, y_pos,
                                        MASTER_TEXT_COLOR)
                
                # 6. QR КОД ДЛЯ ВИДЕО КОМНАТЫ (ТОЛЬКО на первой странице и если есть видео)
                if is_first_page and room_video_url:
                    qr_image = self.generate_qr_code(room_video_url)
                    if qr_image:
                        # Позиция в правом нижнем углу слайда
                        qr_x = PDF_WIDTH - QR_SIZE - QR_RIGHT_MARGIN
                        qr_y = QR_BOTTOM_MARGIN
                        
                        # Добавляем QR код на canvas
                        self.add_qr_to_canvas(canv, qr_image, qr_y, qr_x)

        # Последний showPage() после всех комнат
        canv.showPage()

    def check_list_grouped_slides(self, grouped_nodes: list, gettext_func=None):
        """Группированные слайды контрольного списка с поддержкой перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
        
        canv = self.canv
        
        # ============= НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ =============
        # Размеры шрифтов
        ROOM_TITLE_SIZE = StyleConstants.ROOM_TITLE  # 80
        SECTION_TITLE_SIZE = 45   # 45
        NODE_TEXT_SIZE = 45                           # Размер для названий узлов с точками
        MASTER_TEXT_SIZE = StyleConstants.MASTER_TEXT  # 25
        
        # Цвета
        ROOM_TITLE_COLOR = StyleConstants.PRIMARY_COLOR    # Синий
        IMMEDIATE_TITLE_COLOR = StyleConstants.ERROR_COLOR # Красный
        NORMAL_TITLE_COLOR = StyleConstants.PRIMARY_COLOR  # Синий
        NODE_TEXT_COLOR = StyleConstants.TEXT_COLOR        # Темно-серый
        MASTER_TEXT_COLOR = StyleConstants.PRIMARY_COLOR   # Синий
        
        # Отступы
        TITLE_MARGIN_TOP = StyleConstants.MARGIN * 2       # Отступ сверху
        BETWEEN_SECTIONS_SPACING = 15                      # Отступ между секциями
        BETWEEN_ITEMS_SPACING = 6                          # Отступ между элементами
        BETWEEN_LINES_SPACING = 4                          # Отступ между строками
        NODE_INDENT = StyleConstants.MARGIN * 1.5          # Отступ для узлов с точками
        BULLET_SPACING = 8                                 # Отступ после точки
        MASTER_BOTTOM_MARGIN = StyleConstants.MARGIN * 2   # Отступ снизу для мастера
        # =================================================
        
        y_pos = PDF_HEIGHT - TITLE_MARGIN_TOP

        for room_data in grouped_nodes:
            room_name = room_data["room_name"]
            room_nodes = room_data["nodes"]
            master = room_data["room_master"]
            
            
            # Группировка узлов
            immediate_nodes = [n for n in room_nodes if n.get("check_list_factors") == "immediate"]
            normal_nodes = [n for n in room_nodes if n.get("check_list_factors") != "immediate"]
            
            
            # Расчет места (учитываем точки и отступы)
            required_space = ROOM_TITLE_SIZE + MASTER_TEXT_SIZE + MASTER_BOTTOM_MARGIN
            
            # Immediate узлы
            if immediate_nodes:
                required_space += (SECTION_TITLE_SIZE + BETWEEN_ITEMS_SPACING +
                                (len(immediate_nodes) * NODE_TEXT_SIZE) +
                                (len(immediate_nodes) * BETWEEN_LINES_SPACING) +
                                BETWEEN_SECTIONS_SPACING)
            
            # Normal узлы
            if normal_nodes:
                required_space += (SECTION_TITLE_SIZE + BETWEEN_ITEMS_SPACING +
                                (len(normal_nodes) * NODE_TEXT_SIZE) +
                                (len(normal_nodes) * BETWEEN_LINES_SPACING) +
                                BETWEEN_SECTIONS_SPACING)

            # Проверка места на странице
            if y_pos - required_space < StyleConstants.MARGIN * 2:
                canv.showPage()
                y_pos = PDF_HEIGHT - TITLE_MARGIN_TOP
            
            # 1. НАЗВАНИЕ КОМНАТЫ (по центру) - Size: ROOM_TITLE_SIZE, Color: ROOM_TITLE_COLOR
            room_name_width = canv.stringWidth(room_name, Fonts.bold["name"], ROOM_TITLE_SIZE)
            room_x = (PDF_WIDTH - room_name_width) / 2
            y_pos = self._draw_text_line(room_name, Fonts.bold["name"],
                                    ROOM_TITLE_SIZE, room_x, y_pos,
                                    ROOM_TITLE_COLOR)
            y_pos -= BETWEEN_SECTIONS_SPACING
            
            # 2. IMMEDIATE УЗЛЫ - "Recommendation for action immediately" - Size: SECTION_TITLE_SIZE, Color: IMMEDIATE_TITLE_COLOR
            if immediate_nodes:
                immediate_title = gettext_func(PDF_TEXTS["recommendation_immediate"])
                y_pos = self._draw_text_line(immediate_title, Fonts.bold["name"],
                                        SECTION_TITLE_SIZE, StyleConstants.MARGIN, y_pos,
                                        IMMEDIATE_TITLE_COLOR)
                y_pos -= BETWEEN_ITEMS_SPACING
                
                # Список immediate узлов с точками
                for node in immediate_nodes:
                    node_text = "• " + node["name"]
                    y_pos = self._draw_text_line(node_text, Fonts.regular["name"],
                                            NODE_TEXT_SIZE, NODE_INDENT, y_pos,
                                            NODE_TEXT_COLOR)
                    y_pos -= BETWEEN_LINES_SPACING
                
                y_pos -= BETWEEN_SECTIONS_SPACING
            
            # 3. NORMAL УЗЛЫ - "Recommendation for actions in the next service" - Size: SECTION_TITLE_SIZE, Color: NORMAL_TITLE_COLOR
            if normal_nodes:
                normal_title = gettext_func(PDF_TEXTS["recommendation_normal"])
                y_pos = self._draw_text_line(normal_title, Fonts.bold["name"],
                                        SECTION_TITLE_SIZE, StyleConstants.MARGIN, y_pos,
                                        NORMAL_TITLE_COLOR)
                y_pos -= BETWEEN_ITEMS_SPACING
                
                # Список normal узлов с точками
                for node in normal_nodes:
                    node_text = "• " + node["name"]
                    y_pos = self._draw_text_line(node_text, Fonts.regular["name"],
                                            NODE_TEXT_SIZE, NODE_INDENT, y_pos,
                                            NODE_TEXT_COLOR)
                    y_pos -= BETWEEN_LINES_SPACING
                
                y_pos -= BETWEEN_SECTIONS_SPACING
            
            # 4. МАСТЕР (слева) - Size: MASTER_TEXT_SIZE, Color: MASTER_TEXT_COLOR
            master_text = gettext_func("Master: ") + master
            
            # Проверяем, достаточно ли места для мастера
            if y_pos - MASTER_TEXT_SIZE < MASTER_BOTTOM_MARGIN:
                canv.showPage()
                y_pos = PDF_HEIGHT - TITLE_MARGIN_TOP
                
                # На новой странице снова выводим название комнаты
                room_name_width = canv.stringWidth(room_name, Fonts.bold["name"], ROOM_TITLE_SIZE)
                room_x = (PDF_WIDTH - room_name_width) / 2
                y_pos = self._draw_text_line(room_name, Fonts.bold["name"],
                                        ROOM_TITLE_SIZE, room_x, y_pos,
                                        ROOM_TITLE_COLOR)
                y_pos -= BETWEEN_SECTIONS_SPACING
            
            # Выводим мастера
            y_pos = self._draw_text_line(master_text, Fonts.bold["name"],
                                    MASTER_TEXT_SIZE, StyleConstants.MARGIN, y_pos,
                                    MASTER_TEXT_COLOR)
            
            y_pos -= MASTER_BOTTOM_MARGIN
            
        canv.showPage()

    def last_slides(self, gettext_func=None):
        """Финальные страницы отчета с поддержкой перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
            
        canv = self.canv

        # Предпоследняя страница
        canv.setFillColor(StyleConstants.PRIMARY_COLOR)
        canv.rect(0, 0, PDF_WIDTH, PDF_HEIGHT, stroke=0, fill=1)
        
        img = Image.open(PRE_LAST_SLIDE)
        add_image(canv, img, PDF_WIDTH, 0, 0)

        textobject = canv.beginText()
        textobject.setTextOrigin(StyleConstants.MARGIN, 879)
        textobject.setFont(Fonts.bold["name"], HEDING_FONT_SIZE)
        textobject.setFillColor(StyleConstants.WHITE)
        textobject.textLine(gettext_func("Make   Sure   to    get   Your    VAC"))
        textobject.textLine(gettext_func("system  inspected  and  serviced"))
        textobject.textLine(gettext_func("on a regular basis!"))

        textobject.setFillColor(StyleConstants.LIGHT_GRAY)
        textobject.setTextOrigin(StyleConstants.MARGIN, 587)
        textobject.setFont(Fonts.regular["name"], 48)
        textobject.textLine(gettext_func("Clean air system can help you save between 5{percent} and").format(percent="%"))
        textobject.textLine(gettext_func("15{percent} from your electricity bill!").format(percent="%"))

        textobject.setTextOrigin(StyleConstants.MARGIN, 372)
        textobject.textLine(gettext_func("HAVE  your  AC  and  Duct  system  SERVICED  every  3-4"))
        textobject.textLine(gettext_func("months  to  prevent  the  system  from  faailing  when  you"))
        textobject.textLine(gettext_func("need it most."))

        canv.drawText(textobject)
        canv.showPage()

        # Последняя страница
        img = Image.open(LAST_SLIDE)
        add_image(canv, img, PDF_WIDTH, StyleConstants.MARGIN, StyleConstants.MARGIN)

        contact_info = [
            (gettext_func("Phone"), "+971 58 819 7173"),
            (gettext_func("Email"), "info@klimatika.ae"),
            (gettext_func("Website"), "www.klimatika.ae")
        ]

        textobject = canv.beginText()
        textobject.setTextOrigin(108, 817)
        textobject.setFont(Fonts.bold["name"], HEDING_FONT_SIZE)
        textobject.setFillColor(StyleConstants.PRIMARY_COLOR)
        textobject.textLine(gettext_func("Let's talk!"))

        textobject.setTextOrigin(108, 737)
        textobject.setFont(Fonts.regular["name"], 30)
        textobject.textLine(gettext_func("Call or email us any time for any inquiries"))
        textobject.textLine(gettext_func("regarding our services"))

        y_pos = 591
        for label, value in contact_info:
            textobject.setTextOrigin(108, y_pos)
            textobject.setFont(Fonts.bold["name"], 40)
            textobject.textLine(label)
            textobject.setTextOrigin(108, y_pos - 44)
            textobject.setFont(Fonts.regular["name"], 40)
            textobject.textLine(value)
            y_pos -= 86

        canv.drawText(textobject)
        canv.showPage()


    def _process_service_nodes(self, room, room_data, gettext_func=None):
        """Обработка сервисных узлов с кэшированием переводов"""
        if gettext_func is None:
            gettext_func = lambda x: x
        
        target_lang = self._get_target_language(gettext_func)
        
        for node_id, node in room["nodes"].items():
            # Создаем уникальный ключ для отслеживания обработки узла
            node_key = f"{room_data['room_name']}_{node_id}"
            
            # Пропускаем уже обработанные узлы
            if node_key in self._processed_nodes:
                print(f"DEBUG: Skipping already processed node: {node_key}")
                continue
                
            self._processed_nodes.add(node_key)
            
            # Создаем копию данных узла
            node_copy = node.copy()
            
            # Переводим название узла с кэшированием
            if node_copy.get("name"):
                original_name = node_copy["name"]
                node_copy["name"] = self._get_cached_translation(original_name, target_lang)
            
            # Переводим комментарии если нужно (используется в _process_comments_for_translation)
            self._process_comments_for_translation(room_data, node_copy, gettext_func)
            
            # Проверяем наличие фото
            has_photos = bool(node.get("img_before") or node.get("img_after"))
            
            if has_photos:
                room_data["nodes_with_photos"].append(
                    create_node_data(node_copy["name"], NodeTypes.SERVICE)
                )
                # Используем ПЕРЕВЕДЕННОЕ название комнаты
                self.room_service_slide(
                    node_copy["name"], node["img_before"], node["img_after"],
                    room_data["room_name"],  # Используем переведенное название комнаты
                    node_copy.get("comment"), node.get("url_video"),
                    room_data["master"], gettext_func
                )
            else:
                # Сохраняем переведенное имя в узле
                room_data["nodes_without_photos"].append(
                    create_node_data(
                        node_copy["name"], NodeTypes.SERVICE,
                        comment=node_copy.get("comment"),
                        video_url=node.get("url_video"),
                        original_name=node.get("name"),  # Сохраняем оригинальное имя
                        translated_name=node_copy["name"]  # И переведенное
                    )
                )


    def _process_maintenance_nodes(self, room, room_data, gettext_func=None):
        """Обработка узлов техобслуживания с кэшированием переводов"""
        if gettext_func is None:
            gettext_func = lambda x: x
        
        target_lang = self._get_target_language(gettext_func)
        
        # Переводим комментарий комнаты
        if room_data.get("room_comment"):
            original_comment = room_data["room_comment"]
            translated_comment = self._get_cached_translation(original_comment, target_lang)
            room_data["room_comment"] = translated_comment
            
            if original_comment != translated_comment:
                print(f"DEBUG: Translated room comment: '{original_comment[:30]}...' -> '{translated_comment[:30]}...'")
        
        # ОЧИЩАЕМ списки узлов для этой комнаты
        room_data["nodes_with_photos"] = []
        room_data["nodes_without_photos"] = []
        
        for node_id, node in room["nodes"].items():
            # Создаем уникальный ключ
            node_key = f"{room_data['room_name']}_maintenance_{node_id}"
            
            # Пропускаем уже обработанные узлы
            if node_key in self._processed_nodes:
                continue
                
            self._processed_nodes.add(node_key)
            
            # Создаем копию данных узла
            node_copy = node.copy()
            
            # Переводим название узла
            if node_copy.get("name"):
                original_name = node_copy["name"]
                node_copy["name"] = self._get_cached_translation(original_name, target_lang)
            
            # Проверяем наличие фото
            has_photos = bool(node.get("img_before") or node.get("img_after"))
            
            if has_photos:
                # Узлы с фото - создаем отдельные слайды
                room_data["nodes_with_photos"].append(
                    create_node_data(node_copy["name"], NodeTypes.MAINTENANCE)
                )
                # Используем ПЕРЕВЕДЕННОЕ название комнаты
                self.room_maintenance_slide(
                    node_copy["name"], node["img_before"], node["img_after"],
                    room_data["room_name"],  # Используем переведенное название комнаты
                    room_data["master"],
                    room_data.get("room_comment"),
                    room.get("url_room_video"), gettext_func
                )
            else:
                # Узлы без фото - сохраняем для группированных слайдов
                room_data["nodes_without_photos"].append(
                    create_node_data(
                        node_copy["name"], NodeTypes.MAINTENANCE,
                        original_name=node.get("name"),
                        translated_name=node_copy["name"]  # Сохраняем переведенное имя
                    )
                )


    def _process_checklist_nodes(self, room, room_data, gettext_func=None):
        """Обработка узлов контрольного списка с кэшированием переводов"""
        if gettext_func is None:
            gettext_func = lambda x: x
        
        target_lang = self._get_target_language(gettext_func)
        
        for node_id, node in room["nodes"].items():
            # Создаем уникальный ключ
            node_key = f"{room_data['room_name']}_checklist_{node_id}"
            
            # Пропускаем уже обработанные узлы
            if node_key in self._processed_nodes:
                continue
                
            self._processed_nodes.add(node_key)
            
            # Создаем копию данных узла
            node_copy = node.copy()
            
            # Переводим название узла
            if node_copy.get("name"):
                original_name = node_copy["name"]
                node_copy["name"] = self._get_cached_translation(original_name, target_lang)
            
            # Проверяем наличие фото
            if node.get("img_before"):
                room_data["nodes_with_photos"].append(
                    create_node_data(node_copy["name"], NodeTypes.CHECKLIST)
                )
                self.room_check_list_slide(
                    node_copy["name"], node["img_before"],
                    room["object"], room_data["master"],
                    node["check_list_factors"], gettext_func
                )
            else:
                room_data["nodes_without_photos"].append(
                    create_node_data(
                        node_copy["name"], NodeTypes.CHECKLIST,
                        check_list_factors=node["check_list_factors"],
                        original_name=node.get("name"),
                        translated_name=node_copy["name"]  # Сохраняем переведенное имя
                    )
                )

    def _prepare_service_nodes(self, all_rooms_data, gettext_func=None):
        """Подготовка сервисных узлов для группировки без повторного перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
        
        service_nodes = []
        for room_data in all_rooms_data:
            # Фильтруем только сервисные узлы
            service_nodes_without_photos = [
                node for node in room_data["nodes_without_photos"] 
                if node.get("type") == NodeTypes.SERVICE
            ]
            
            if service_nodes_without_photos:
                # Используем уже переведенные имена из узлов
                prepared_nodes = []
                for node in service_nodes_without_photos:
                    # Используем переведенное имя если оно есть, иначе оригинальное
                    node_name = node.get("translated_name") or node["name"]
                    prepared_nodes.append({
                        "name": node_name,
                        "comment": node.get("comment"),
                        "video_url": node.get("video_url")
                    })
                
                service_nodes.append({
                    "room_name": room_data["room_name"],  # Уже переведенное название
                    "original_room_name": room_data.get("original_room_name", room_data["room_name"]),
                    "nodes": prepared_nodes,  # Уже переведенные узлы
                    "room_master": room_data["master"]
                })
        return service_nodes

    def _prepare_maintenance_nodes(self, all_rooms_data, gettext_func=None):
        """Подготовка maintenance узлов для группировки без повторного перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
        
        maintenance_nodes = []
        for room_data in all_rooms_data:
            # Фильтруем только maintenance узлы БЕЗ фото
            maintenance_nodes_without_photos = [
                node for node in (room_data["nodes_without_photos"])
                if node.get("type") == NodeTypes.MAINTENANCE
            ]
            
            # Используем уже переведенные имена
            prepared_nodes = []
            for node in maintenance_nodes_without_photos:
                # Используем переведенное имя если оно есть
                node_name = node.get("translated_name") or node["name"]
                prepared_nodes.append({"name": node_name})
            
            maintenance_nodes.append({
                "room_name": room_data["room_name"],  # Уже переведенное название
                "original_room_name": room_data.get("original_room_name", room_data["room_name"]),
                "nodes": prepared_nodes,  # Уже переведенные узлы
                "room_master": room_data["master"],
                "room_comment": room_data.get("room_comment"),
                "room_video_url": room_data.get("room_video_url")
            })
            if not prepared_nodes:
                print(f"DEBUG: Room '{room_data['room_name']}' has NO maintenance nodes without photos")

        return maintenance_nodes

    def _prepare_checklist_nodes(self, all_rooms_data, gettext_func=None):
        """Подготовка узлов контрольного списка для группировки без повторного перевода"""
        if gettext_func is None:
            gettext_func = lambda x: x
        
        checklist_nodes = []
        for room_data in all_rooms_data:
            # Фильтруем узлы контрольного списка
            checklist_nodes_list = [
                node for node in room_data["nodes_without_photos"] 
                if node.get("type") == NodeTypes.CHECKLIST
            ]
            
            if checklist_nodes_list:
                # Используем уже переведенные имена
                prepared_nodes = []
                for node in checklist_nodes_list:
                    node_name = node.get("translated_name") or node["name"]
                    prepared_nodes.append({
                        "name": node_name,
                        "check_list_factors": node.get("check_list_factors")
                    })
                
                checklist_nodes.append({
                    "room_name": room_data["room_name"],  # Уже переведенное название
                    "original_room_name": room_data.get("original_room_name", room_data["room_name"]),
                    "nodes": prepared_nodes,  # Уже переведенные узлы
                    "room_master": room_data["master"]
                })
        return checklist_nodes


    def _validate_room_data(self, all_rooms_data: list):
        """Валидация формата данных комнат"""
        for i, room_data in enumerate(all_rooms_data):
            # Проверяем nodes_with_photos
            for j, node in enumerate(room_data["nodes_with_photos"]):
                if not isinstance(node, dict) or "name" not in node:
                    print(f"ERROR: Invalid node format in nodes_with_photos[{i}][{j}]: {node}")
                    # Автоматически исправляем если возможно
                    if isinstance(node, str):
                        room_data["nodes_with_photos"][j] = {"name": node, "type": "unknown"}
                    else:
                        room_data["nodes_with_photos"][j] = {"name": "Invalid Node", "type": "error"}
            
            # Проверяем nodes_without_photos
            for j, node in enumerate(room_data["nodes_without_photos"]):
                if not isinstance(node, dict) or "name" not in node:
                    print(f"ERROR: Invalid node format in nodes_without_photos[{i}][{j}]: {node}")
                    # Автоматически исправляем если возможно
                    if isinstance(node, str):
                        room_data["nodes_without_photos"][j] = {"name": node, "type": "unknown"}
                    else:
                        room_data["nodes_without_photos"][j] = {"name": "Invalid Node", "type": "error"}       



    def generate(self, report: dict, gettext_func=None) -> str:
        """Основной метод генерации отчета с оптимизированным переводом"""
        if gettext_func is None:
            gettext_func = lambda x: x
        
        try:
            # Очищаем кэши перед началом новой генерации
            self._translation_cache.clear()
            self._processed_nodes.clear()
            
            # Определяем и логируем язык
            detected_language = self._get_target_language(gettext_func)
            print(f"DEBUG: Detected language: {detected_language}")
            
            self.first_slide(gettext_func)
            
            outline = report["Outline"]
            self.summary_slides(
                outline["date"].strftime("%m/%d/%Y"),
                outline["name"],
                outline["phone_number"],
                outline["address"],
                outline["performed_service"],
                outline["extra_services"],
                outline["work_factors"],
                gettext_func
            )

            rooms = report["Rooms"]
            all_rooms_data = []
            report_type = outline["report_service"]
            
            # Обработка всех комнат с оптимизированным переводом
            for room in rooms["rooms_list"]:
                # Переводим название комнаты
                original_room_name = room["object"]
                translated_room_name = self._translate_room_name(original_room_name, gettext_func)
                
                # Инициализация комнаты с переведенным названием
                room_data = {
                    "room_name": translated_room_name,  # Используем переведенное название
                    "original_room_name": original_room_name,  # Сохраняем оригинальное название
                    "room_comment": room.get("room_comment"),
                    "room_video_url": room.get("url_room_video"),
                    "master": room.get("room_master"),
                    "nodes_with_photos": [],
                    "nodes_without_photos": []
                }
                
                print(f"DEBUG: Original room name: '{original_room_name}' -> Translated: '{translated_room_name}'")
                print(f"DEBUG: Original room comment: '{room_data['room_comment']}'")
                
                all_rooms_data.append(room_data)

                # Обработка узлов в зависимости от типа отчета
                if report_type == "Service":
                    self._process_service_nodes(room, room_data, gettext_func)
                elif report_type == "Maintenance":
                    self._process_maintenance_nodes(room, room_data, gettext_func)
                elif report_type == "Check list":
                    self._process_checklist_nodes(room, room_data, gettext_func)
                else:
                    print(f"WARNING: Unknown report type: {report_type}")
                    self._process_service_nodes(room, room_data, gettext_func)
                
                print(f"DEBUG: After processing room comment: '{room_data['room_comment']}'")

            # Валидация данных
            self._validate_room_data(all_rooms_data)

            # Генерация summary страниц
            if report_type == "Maintenance":
                maintenance_nodes = self._prepare_maintenance_nodes(all_rooms_data, gettext_func)
                self.create_maintenance_summary_slides(maintenance_nodes, gettext_func)

            elif report_type == "Service":
                service_nodes = self._prepare_service_nodes(all_rooms_data, gettext_func)
                if service_nodes:
                    self.create_grouped_slides(service_nodes, gettext_func)
            elif report_type == "Check list":
                checklist_nodes = self._prepare_checklist_nodes(all_rooms_data, gettext_func)
                if checklist_nodes:
                    self.check_list_grouped_slides(checklist_nodes, gettext_func)

            self.last_slides(gettext_func)
            self.canv.save()
            
            return pdf_compression(f"{REPORTS_PATH / self.report_name}.pdf")
        
        finally:
            # Выводим статистику по кэшу
            print(f"DEBUG: Translation cache size: {len(self._translation_cache)} entries")
            print(f"DEBUG: Processed nodes: {len(self._processed_nodes)}")