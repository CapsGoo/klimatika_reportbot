# translator.py
import logging
import langdetect
from typing import Optional, Dict, Tuple
from deep_translator import GoogleTranslator
from functools import lru_cache

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Для консистентности определения языка
from langdetect import DetectorFactory, detect
DetectorFactory.seed = 0

# Конфигурация переводчика
class TranslationConfig:
    """Конфигурация для переводчика"""
    FORCE_TRANSLATE = False  # Принудительно переводить все тексты
    USE_CACHE = True         # Использовать кэширование
    CACHE_SIZE = 1000        # Размер кэша переводов
    MAX_TEXT_LENGTH = 4000   # Максимальная длина текста для перевода
    DEFAULT_SOURCE_LANG = 'auto'  # Автоматическое определение языка источника

def detect_language(text: str) -> str:
    """
    Определяет язык текста.
    Возвращает код языка (en, ru, ar и т.д.) или 'unknown' если не удалось определить
    """
    if not text or len(text.strip()) < 2:
        return 'unknown'
    
    # Простая проверка для английского текста (только ASCII символы)
    try:
        # Если текст состоит в основном из ASCII символов, скорее всего это английский
        ascii_count = sum(1 for c in text if ord(c) < 128)
        if ascii_count / len(text) > 0.9:  # 90% символов ASCII
            return 'en'
        
        # Используем langdetect для определения языка
        detected = detect(text)
        
        # Маппинг кодов языков
        lang_mapping = {
            'en': 'en',  # Английский
            'ru': 'ru',  # Русский
            # 'ar': 'ar',  # Арабский
            # 'fr': 'fr',  # Французский
            # 'de': 'de',  # Немецкий
            # 'es': 'es',  # Испанский
            # 'zh-cn': 'zh',  # Китайский упрощенный
            # 'zh-tw': 'zh',  # Китайский традиционный
        }
        
        return lang_mapping.get(detected, detected)
        
    except Exception as e:
        logger.debug(f"Language detection failed for text '{text[:50]}...': {e}")
        return 'unknown'

class TextTranslator:
    """Класс для перевода текста с кэшированием и оптимизациями"""
    
    def __init__(self, target_lang: str = 'en'):
        self.target_lang = target_lang
        self.translator = GoogleTranslator(
            source=TranslationConfig.DEFAULT_SOURCE_LANG, 
            target=target_lang
        )
        
        # Кэш для переводов
        self._translation_cache: Dict[Tuple[str, str], str] = {}
        
        # Кэш для определений языка
        self._language_cache: Dict[str, str] = {}
        
        logger.info(f"Initialized translator for target language: {target_lang}")
    
    def should_translate(self, text: str) -> Tuple[bool, str]:
        """
        Определяет, нужно ли переводить текст.
        Возвращает (нужно_ли_переводить, определенный_язык)
        """
        if not text or len(text.strip()) < 2:
            return False, 'unknown'
        
        # Определяем язык текста с кэшированием
        if text in self._language_cache:
            source_lang = self._language_cache[text]
        else:
            source_lang = detect_language(text)
            self._language_cache[text] = source_lang
        
        # Если язык не определен, переводим
        if source_lang == 'unknown':
            return True, source_lang
        
        # Если исходный язык совпадает с целевым, не переводим
        if source_lang == self.target_lang:
            return False, source_lang
        
        # Принудительный перевод если включен в конфиге
        if TranslationConfig.FORCE_TRANSLATE:
            return True, source_lang
        
        return True, source_lang
    
    def translate_text(self, text: str) -> str:
        """
        Переводит текст на целевой язык с оптимизациями:
        - Определяет язык исходного текста
        - Пропускает перевод если язык совпадает
        - Использует кэширование
        """
        # Проверяем, нужно ли переводить
        should_translate, source_lang = self.should_translate(text)
        
        if not should_translate:
            logger.debug(f"Skipping translation (source={source_lang}, target={self.target_lang}): '{text[:50]}...'")
            return text
        
        # Проверяем кэш
        cache_key = (text, self.target_lang)
        if TranslationConfig.USE_CACHE and cache_key in self._translation_cache:
            cached_result = self._translation_cache[cache_key]
            logger.debug(f"Using cached translation: '{text[:50]}...' -> '{cached_result[:50]}...'")
            return cached_result
        
        try:
            # Ограничиваем длину текста
            text_to_translate = text[:TranslationConfig.MAX_TEXT_LENGTH]
            
            # Выполняем перевод
            translated = self.translator.translate(text_to_translate)
            
            # Сохраняем в кэш
            if TranslationConfig.USE_CACHE:
                self._translation_cache[cache_key] = translated
                
                # Ограничиваем размер кэша
                if len(self._translation_cache) > TranslationConfig.CACHE_SIZE:
                    # Удаляем самые старые записи
                    keys_to_remove = list(self._translation_cache.keys())[:TranslationConfig.CACHE_SIZE // 10]
                    for key in keys_to_remove:
                        del self._translation_cache[key]
            
            logger.info(f"Translated from {source_lang} to {self.target_lang}: '{text[:30]}...' -> '{translated[:30]}...'")
            return translated
            
        except Exception as e:
            logger.error(f"Translation failed for text '{text[:50]}...': {e}")
            return text
    
    def clear_cache(self):
        """Очищает кэш переводов"""
        self._translation_cache.clear()
        self._language_cache.clear()
        logger.info("Translation cache cleared")

# Глобальные экземпляры переводчика
_translator_instances: Dict[str, TextTranslator] = {}

def get_translator(target_lang: str = 'en') -> TextTranslator:
    """
    Получает или создает экземпляр переводчика для указанного языка
    """
    global _translator_instances
    
    # Нормализуем код языка
    normalized_lang = target_lang.lower().strip()
    
    if normalized_lang not in _translator_instances:
        _translator_instances[normalized_lang] = TextTranslator(normalized_lang)
    
    return _translator_instances[normalized_lang]

def translate_if_needed(text: str, target_lang: str = 'en') -> str:
    """
    Основная функция для перевода текста на целевой язык.
    Оптимизирована для избежания ненужных переводов.
    """
    if not text:
        return text
    
    # Нормализуем язык
    normalized_lang = target_lang.lower().strip() if target_lang else 'en'
    
    # Получаем переводчик для целевого языка
    translator = get_translator(normalized_lang)
    
    # Выполняем перевод с оптимизациями
    return translator.translate_text(text)

def detect_text_language(text: str) -> str:
    """
    Публичная функция для определения языка текста
    """
    return detect_language(text)

def clear_all_caches():
    """
    Очищает все кэши переводчиков
    """
    global _translator_instances
    
    for translator in _translator_instances.values():
        translator.clear_cache()
    
    logger.info("All translation caches cleared")

# Функции для статистики
def get_translation_stats() -> Dict:
    """
    Возвращает статистику по переводам
    """
    global _translator_instances
    
    stats = {
        'total_translators': len(_translator_instances),
        'translators': {}
    }
    
    for lang, translator in _translator_instances.items():
        stats['translators'][lang] = {
            'cache_size': len(translator._translation_cache),
            'language_cache_size': len(translator._language_cache)
        }
    
    return stats

def print_translation_stats():
    """
    Выводит статистику по переводам в лог
    """
    stats = get_translation_stats()
    
    logger.info("=== Translation Statistics ===")
    logger.info(f"Total translators: {stats['total_translators']}")
    
    for lang, lang_stats in stats['translators'].items():
        logger.info(f"  Language '{lang}':")
        logger.info(f"    Translation cache: {lang_stats['cache_size']} entries")
        logger.info(f"    Language cache: {lang_stats['language_cache_size']} entries")
    
    logger.info("==============================")

# Пример использования конфигурации
if __name__ == "__main__":
    # Пример настройки конфигурации
    TranslationConfig.FORCE_TRANSLATE = False
    TranslationConfig.USE_CACHE = True
    
    # Тестовые примеры
    test_texts = [
        "Hello, world!",  # Английский - не должен переводиться
        "Привет, мир!",   # Русский - должен переводиться на английский
        "مرحبا بالعالم",  # Арабский - должен переводиться
    ]
    
    print("Testing translator...")
    for text in test_texts:
        translated = translate_if_needed(text, 'en')
        detected = detect_text_language(text)
        print(f"Original: '{text}'")
        print(f"Detected language: {detected}")
        print(f"Translated: '{translated}'")
        print("-" * 40)
    
    # Показать статистику
    print_translation_stats()