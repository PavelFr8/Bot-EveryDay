from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def make_row_keyboard(items: list[str]) -> InlineKeyboardButton:
    """
    Создаёт инлайн-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [InlineKeyboardButton(text=item) for item in items]
    return InlineKeyboardMarkup(keyboard=[row], resize_keyboard=True)