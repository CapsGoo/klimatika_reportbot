from typing import BinaryIO
from aiogram import types, Bot
from typing import List, Tuple
from dataclasses import dataclass, field
from .cleaningnode import CleaningNode
from .block import Block
from enum import Enum


import os
import tempfile
from typing import Optional
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

from config import SERVICE_ACCOUNT_INFO
import requests

@dataclass
class Room:
    class Type(str, Enum):
        UNKNOWN = "Unknown"
        BEDROOM = "Bedroom"
        LIVING_ROOM = "Living Room"
        MASTER_ROOM = "Master bedroom"
        KIDS_ROOM = "Kids bedroom"
        GUEST_ROOM = "Guest bedroom"
        MAIDS_ROOM = "Maids bedroom"
        CABINET_ROOM = "Cabinet room"
        GYM = "Gym"
        KITCHEN = "Kitchen"

        def __str__(self) -> str:
            return str(self.value)

        def for_button(self, text: str) -> Tuple[str, ...]:
            return (text, self)

    room_type: Type = Type.UNKNOWN
    room_object: str | None = None
    room_comment: str | None = None
    block_type: Type = Type.UNKNOWN
    room_factors: Type = Type.UNKNOWN
    room_video_id: types.Video | None = None
    master: str | None = None

    default_cleaning_nodes: List[Tuple[CleaningNode, bool]] = field(default_factory=list)
    # cleaning_nodes: List[CleaningNode] = field(default_factory=list)
    cleaning_nodes: List[Tuple[CleaningNode, bool]] = field(default_factory=list)
    nodes_queue: List[CleaningNode] = field(default_factory=list)
    _index: int = 0

    def __post_init__(self):
        default_nodes = [CleaningNode("DEFAULT", type=CleaningNode.Type.DEFAULT)]

        # self.default_cleaning_nodes = [(node, False) for node in default_nodes]
        self.default_cleaning_nodes = [(node, False) for node in default_nodes]
        self.cleaning_nodes = []  # Пользовательские узлы


    @property
    def last_cleaning_node(self) -> CleaningNode | None:
        if self.cleaning_nodes_empty():
            return None
        return self.cleaning_nodes[-1]

    def pop_cleaning_node(self) -> None:
        if self.cleaning_nodes_empty():
            return
        self.cleaning_nodes.pop()

    def cleaning_nodes_empty(self) -> bool:
        return len(self.cleaning_nodes) == 0

    # def clear_all_cleaning_nodes(self) -> None:
    #     for default_node in self.default_cleaning_nodes:
    #         default_node[1] = False

    #     self.cleaning_nodes.clear()
    def clear_all_cleaning_nodes(self) -> None:
        # Создаем новые кортежи со статусом False
        self.default_cleaning_nodes = [
            (node, False) for node, status in self.default_cleaning_nodes
        ]
        self.cleaning_nodes.clear()


    def set_default_node(self, node: CleaningNode) -> None:
        """Обновляет или добавляет узел"""
        for i, (existing_node, completed) in enumerate(self.default_cleaning_nodes):
            if existing_node == node:
                self.default_cleaning_nodes[i] = (node, True)
                return
        
        # Если узел не найден - добавляем новый
        self.default_cleaning_nodes.append((node, True))



    def add_node(self, node: CleaningNode) -> None:
        if node.type == CleaningNode.Type.OTHER:
            self.cleaning_nodes.append(node)


    def add_default_node(self, index: int) -> None:
        """Добавляет узел по индексу (устанавливает статус True)"""
        if 0 <= index < len(self.default_cleaning_nodes):
            self.default_cleaning_nodes[index][1] = True
        else:
            raise IndexError(f"Index {index} out of range for default cleaning nodes")


    def delete_node(self, index: int, type: CleaningNode.Type) -> None:
        if type == CleaningNode.Type.DEFAULT:
            self.delete_default_node(index)  # Передаем номер страницы
        elif type == CleaningNode.Type.OTHER:
            self.cleaning_nodes.pop(index)


    def delete_default_node(self, index: int, page: int = 1) -> None:
        # Устанавливаем статус узла в False вместо удаления
        self.default_cleaning_nodes[index][1] = False



    def create_nodes_queue(self):
        self.nodes_queue.clear()
        self._index = 0
        for node, status in filter(lambda x: x[1], self.default_cleaning_nodes):
            self.nodes_queue.append(node)

        for node in self.cleaning_nodes:
            self.nodes_queue.append(node)

    @property
    def current_node(self) -> CleaningNode | None:
        if self.nodes_queue_empty():
            return None
        return self.nodes_queue[self._index]

    def next_cleaning_node(self):
        self._index += 1
        return self.current_node

    def nodes_queue_empty(self):
        return self._index == len(self.nodes_queue)

    def nodes_queue_back(self):
        if self._index == 0:
            raise Exception("_index is zero")
        self._index -= 1

    def clear_room_data(self) -> None:
        """
        Полная очистка данных комнаты: узлов, фото, видео, комментариев
        Сохраняет только базовые настройки (room_type, block_type и т.д.)
        """
        # Сбрасываем статусы дефолтных узлов
        self.default_cleaning_nodes = [
            (CleaningNode(node.name, type=node.type, button_text=node.button_text), False) 
            for node, _ in self.default_cleaning_nodes
        ]
        
        # Очищаем кастомные узлы
        self.cleaning_nodes.clear()
        
        # Очищаем очередь
        self.nodes_queue.clear()
        self._index = 0
        
        # Очищаем комментарии комнаты
        self.room_comment = None
        
        # Очищаем видео комнаты
        self.room_video_id = None
        
        # Очищаем мастера
        self.master = None

        
    def update_node_comment(self, node_index: int, comment: str, node_type: CleaningNode.Type = CleaningNode.Type.DEFAULT) -> None:
        """
        Обновляет комментарий узла по индексу и типу
        Args:
            node_index: Индекс узла в соответствующем списке
            comment: Новый комментарий
            node_type: Тип узла (DEFAULT или OTHER)
        """
        if node_type == CleaningNode.Type.DEFAULT:
            if 0 <= node_index < len(self.default_cleaning_nodes):
                # Создаем новый объект с обновленным комментарием
                old_node, status = self.default_cleaning_nodes[node_index]
                new_node = CleaningNode(
                    name=old_node.name,
                    type=old_node.type,
                    photo_before=old_node.photo_before,
                    photo_after=old_node.photo_after,
                    button_text=old_node.button_text,
                    comment=comment,
                    video_id=old_node.video_id,
                    extra_factors=old_node.extra_factors
                )
                self.default_cleaning_nodes[node_index] = (new_node, status)
            else:
                raise IndexError(f"Default node index {node_index} out of range")
        
        elif node_type == CleaningNode.Type.OTHER:
            if 0 <= node_index < len(self.cleaning_nodes):
                old_node = self.cleaning_nodes[node_index]
                new_node = CleaningNode(
                    name=old_node.name,
                    type=old_node.type,
                    photo_before=old_node.photo_before,
                    photo_after=old_node.photo_after,
                    button_text=old_node.button_text,
                    comment=comment,
                    video_id=old_node.video_id,
                    extra_factors=old_node.extra_factors
                )
                self.cleaning_nodes[node_index] = (new_node)
            else:
                raise IndexError(f"Other node index {node_index} out of range")
            

 
    
    def find_node_index(self, node_name: str, node_type: CleaningNode.Type = None) -> Tuple[int, CleaningNode.Type]:
        """
        Находит индекс узла по имени
        Returns:
            Tuple[index, node_type] или (-1, None) если не найден
        """
        # Ищем в default_cleaning_nodes
        for i, (node, status) in enumerate(self.default_cleaning_nodes):
            if node.name == node_name:
                return i, CleaningNode.Type.DEFAULT
        
        # Ищем в cleaning_nodes
        for i, node in enumerate(self.cleaning_nodes):
            if node.name == node_name:
                return i, CleaningNode.Type.OTHER
        
        return -1, None
    



    def update_node_photo_before(self, node_index: int, photo: types.PhotoSize, node_type: CleaningNode.Type = CleaningNode.Type.DEFAULT) -> None:
        """
        Обновляет фото "до" узла по индексу и типу
        Args:
            node_index: Индекс узла в соответствующем списке
            photo: Фото объекта
            node_type: Тип узла (DEFAULT или OTHER)
        """
        if node_type == CleaningNode.Type.DEFAULT:
            if 0 <= node_index < len(self.default_cleaning_nodes):
                old_node, status = self.default_cleaning_nodes[node_index]
                new_node = CleaningNode(
                    name=old_node.name,
                    type=old_node.type,
                    photo_before=photo,
                    photo_after=old_node.photo_after,
                    button_text=old_node.button_text,
                    comment=old_node.comment,
                    video_id=old_node.video_id,
                    extra_factors=old_node.extra_factors
                )
                self.default_cleaning_nodes[node_index] = (new_node, status)
            else:
                raise IndexError(f"Default node index {node_index} out of range")
        
        elif node_type == CleaningNode.Type.OTHER:
            if 0 <= node_index < len(self.cleaning_nodes):
                old_node = self.cleaning_nodes[node_index]
                new_node = CleaningNode(
                    name=old_node.name,
                    type=old_node.type,
                    photo_before=photo,
                    photo_after=old_node.photo_after,
                    button_text=old_node.button_text,
                    comment=old_node.comment,
                    video_id=old_node.video_id,
                    extra_factors=old_node.extra_factors
                )
                self.cleaning_nodes[node_index] = (new_node)
            else:
                raise IndexError(f"Other node index {node_index} out of range")

    def update_node_photo_after(self, node_index: int, photo: types.PhotoSize, node_type: CleaningNode.Type = CleaningNode.Type.DEFAULT) -> None:
        """
        Обновляет фото "после" узла по индексу и типу
        Args:
            node_index: Индекс узла в соответствующем списке
            photo: Фото объекта
            node_type: Тип узла (DEFAULT или OTHER)
        """
        if node_type == CleaningNode.Type.DEFAULT:
            if 0 <= node_index < len(self.default_cleaning_nodes):
                old_node, status = self.default_cleaning_nodes[node_index]
                new_node = CleaningNode(
                    name=old_node.name,
                    type=old_node.type,
                    photo_before=old_node.photo_before,
                    photo_after=photo,
                    button_text=old_node.button_text,
                    comment=old_node.comment,
                    video_id=old_node.video_id,
                    extra_factors=old_node.extra_factors
                )
                self.default_cleaning_nodes[node_index] = (new_node, status)
            else:
                raise IndexError(f"Default node index {node_index} out of range")
        
        elif node_type == CleaningNode.Type.OTHER:
            if 0 <= node_index < len(self.cleaning_nodes):
                old_node = self.cleaning_nodes[node_index]
                new_node = CleaningNode(
                    name=old_node.name,
                    type=old_node.type,
                    photo_before=old_node.photo_before,
                    photo_after=photo,
                    button_text=old_node.button_text,
                    comment=old_node.comment,
                    video_id=old_node.video_id,
                    extra_factors=old_node.extra_factors
                )
                self.cleaning_nodes[node_index] = (new_node)
            else:
                raise IndexError(f"Other node index {node_index} out of range")
            

    def update_node_video(self, node_index: int, video: types.Video, node_type: CleaningNode.Type = CleaningNode.Type.DEFAULT) -> None:
        """
        Обновляет видео узла по индексу и типу
        Args:
            node_index: Индекс узла в соответствующем списке
            video: Видео объект (сохраняем только file_id)
            node_type: Тип узла (DEFAULT или OTHER)
        """
        if node_type == CleaningNode.Type.DEFAULT:
            if 0 <= node_index < len(self.default_cleaning_nodes):
                old_node, status = self.default_cleaning_nodes[node_index]
                new_node = CleaningNode(
                    name=old_node.name,
                    type=old_node.type,
                    photo_before=old_node.photo_before,
                    photo_after=old_node.photo_after,
                    button_text=old_node.button_text,
                    comment=old_node.comment,
                    video_id=video.file_id if video else None,  # Сохраняем только file_id
                    extra_factors=old_node.extra_factors
                )
                self.default_cleaning_nodes[node_index] = (new_node, status)
            else:
                raise IndexError(f"Default node index {node_index} out of range")
        
        elif node_type == CleaningNode.Type.OTHER:
            if 0 <= node_index < len(self.cleaning_nodes):
                old_node = self.cleaning_nodes[node_index]
                new_node = CleaningNode(
                    name=old_node.name,
                    type=old_node.type,
                    photo_before=old_node.photo_before,
                    photo_after=old_node.photo_after,
                    button_text=old_node.button_text,
                    comment=old_node.comment,
                    video_id=video.file_id if video else None,  # Сохраняем только file_id
                    extra_factors=old_node.extra_factors
                )
                self.cleaning_nodes[node_index] = (new_node)
            else:
                raise IndexError(f"Other node index {node_index} out of range")
            




    def update_node_extra_factors(self, node_index: int, extra_factors: str, node_type: CleaningNode.Type = CleaningNode.Type.DEFAULT) -> None:
        """
        Обновляет дополнительные факторы узла по индексу и типу
        """
        if node_type == CleaningNode.Type.DEFAULT:
            if 0 <= node_index < len(self.default_cleaning_nodes):
                old_node, status = self.default_cleaning_nodes[node_index]
                new_node = CleaningNode(
                    name=old_node.name,
                    type=old_node.type,
                    photo_before=old_node.photo_before,
                    photo_after=old_node.photo_after,
                    button_text=old_node.button_text,
                    comment=old_node.comment,
                    video_id=old_node.video_id,
                    extra_factors=extra_factors
                )
                self.default_cleaning_nodes[node_index] = (new_node, status)
        
        elif node_type == CleaningNode.Type.OTHER:
            if 0 <= node_index < len(self.cleaning_nodes):
                old_node = self.cleaning_nodes[node_index]
                new_node = CleaningNode(
                    name=old_node.name,
                    type=old_node.type,
                    photo_before=old_node.photo_before,
                    photo_after=old_node.photo_after,
                    button_text=old_node.button_text,
                    comment=old_node.comment,
                    video_id=old_node.video_id,
                    extra_factors=extra_factors
                )
                self.cleaning_nodes[node_index] = (new_node)

    def set_node_status(self, node_index: int, status: bool, node_type: CleaningNode.Type = CleaningNode.Type.DEFAULT) -> None:
        """
        Устанавливает статус узла (активен/неактивен) по индексу и типу
        """
        if node_type == CleaningNode.Type.DEFAULT:
            if 0 <= node_index < len(self.default_cleaning_nodes):
                node, old_status = self.default_cleaning_nodes[node_index]
                self.default_cleaning_nodes[node_index] = (node, status)
        
        elif node_type == CleaningNode.Type.OTHER:
            if 0 <= node_index < len(self.cleaning_nodes):
                node = self.cleaning_nodes[node_index]
                self.cleaning_nodes[node_index] = (node)


    async def dict_with_binary(self, bot: Bot, _) -> dict:  # Добавляем параметр _
        nodes = [
            node for node, status in self.default_cleaning_nodes if status
        ] + self.cleaning_nodes

        # Сортируем узлы по приоритету:
        # 1. С двумя фото (before+after)
        # 2. С одним фото
        # 3. С комментариями (но без фото)
        # 4. Без фото и комментариев
        sorted_nodes = sorted(
            nodes,
            key=lambda node: (
                0 if getattr(node, 'photo_before', None) and getattr(node, 'photo_after', None) else
                1 if getattr(node, 'photo_before', None) or getattr(node, 'photo_after', None) else
                2 if getattr(node, 'comment', None) else
                3
            )
        )

        room_video_url = await process_video_to_gdrive(bot, getattr(self, 'room_video_id', None))
        
        dictionary = {
            "room": (str(self.room_type)),  # Переводим тип комнаты
            "object": _(str(self.room_object)),  # Переводим объект комнаты
            "blok_type": (str(self.block_type)),  # Переводим тип блока
            "room_comment": getattr(self, 'room_comment', None) or None,
            "room_master": (str(self.master)),
            "url_room_video": room_video_url,
            "nodes": {
                index: {
                    "name": (_(node.button_text)).lower(),  # Переводим название узла
                    "room_factors": self.room_factors,
                    "check_list_factors": node.extra_factors,
                    "img_before": await safe_download_image(bot, getattr(node, 'photo_before', None)),
                    "img_after": await safe_download_image(bot, getattr(node, 'photo_after', None)),
                    "url_video": await process_video_to_gdrive(bot, getattr(node, 'video_id', None)),
                    "comment": getattr(node, "comment", None),
                }
                for index, node in enumerate(sorted_nodes)
            }
        }
        return dictionary


async def download_image(bot: Bot, photo: types.PhotoSize | None) -> BinaryIO:
    if photo is None:
        return None
    return await bot.download(photo.file_id)

async def safe_download_image(bot: Bot, photo: Optional[types.PhotoSize]) -> Optional[BinaryIO]:
    """Безопасное скачивание изображения с проверкой на None"""
    if photo is None:
        return None
    try:
        return await download_image(bot, photo)
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

async def process_video_to_gdrive(bot: Bot, video_message_id: Optional[str]) -> Optional[str]:
    """Полный цикл обработки видео: скачивание -> Google Drive -> URL"""
    if not video_message_id:
        return None
    
    video_path = None  # Инициализируем переменную
    
    try:
        # 1. Скачиваем видео из Telegram
        video_path = await download_video(bot, video_message_id)
        if not video_path or not os.path.exists(video_path):
            print("Failed to download video or file doesn't exist")
            return None
        
        # 2. Загружаем на Google Drive
        print(f"Uploading {video_path} to Google Drive...")
        video_url = await upload_to_gdrive(video_path)
        
        return video_url
        
    except Exception as e:
        print(f"Error processing video: {e}")
        return None
        
    finally:
        # Удаляем временный файл, если он существует
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)

            except Exception as e:
                print(f"Error deleting temp file: {e}")

async def download_video(bot: Bot, file_id: str) -> Optional[str]:
    """Скачивание видео из Telegram во временный файл"""
    # file_id это id сообщения с файлом видео
    try:
        # Получаем информацию о файле
        file = await bot.get_file(file_id) 
        
        # Создаем временный файл
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"video_{file_id}.mp4")
        
        # Скачиваем файл
        await bot.download(file.file_id, destination=temp_file)
        
        # Проверяем, что файл скачался
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            print(f"Video downloaded to {temp_file} ({os.path.getsize(temp_file)} bytes)")
            return temp_file
        return None
        
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None






from google.auth.transport.requests import Request
import os

from config import FOLDER_ID, SCOPES, SERVICE_ACCOUNT_INFO, OAUTH_TOKEN_INFO

def get_creds():
    creds = None
    # Проверяем, есть ли уже токен
    if os.path.exists(OAUTH_TOKEN_INFO):
        creds = Credentials.from_authorized_user_file(OAUTH_TOKEN_INFO, SCOPES)
    
    # Если токена нет или он просрочен
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Обновляем токен
        else:
            # Запускаем OAuth-поток (откроется браузер)
            flow = InstalledAppFlow.from_client_secrets_file(
                SERVICE_ACCOUNT_INFO, 
                SCOPES
            )
            creds = flow.run_local_server(port=0)  # Авторизация в браузере
        
        # Сохраняем токен для след. запусков
        with open("config/token.json", "w") as token_file:
            token_file.write(creds.to_json())
    
    return creds

async def upload_to_gdrive(file_path: str):
    try:
        creds = get_creds()  # Получаем авторизованные creds
        service = build("drive", "v3", credentials=creds)

        # Загружаем файл с указанием родительской папки
        file_metadata = {
            "name": os.path.basename(file_path),
            "parents": [FOLDER_ID]  # Вот ключевое изменение!
        }
        
        media = MediaFileUpload(file_path, mimetype="video/mp4")
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id,webViewLink",
        ).execute()

        # Делаем файл доступным по ссылке
        service.permissions().create(
            fileId=file["id"],
            body={"type": "anyone", "role": "reader"},
        ).execute()

        return file.get("webViewLink")
    
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        raise