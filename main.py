import aiogram.utils.exceptions
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, \
    LabeledPrice, PreCheckoutQuery, InlineQuery, InlineQueryResultArticle, InlineQueryResultCachedPhoto
from aiogram import Bot, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaAnimation
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import logic
import phrases as phr
import keyboards as kb
from db import Mongo as mg
import logging
from dotenv import load_dotenv
import os
storage=MemoryStorage()
load_dotenv()
bot = Bot(token = os.getenv('TOKEN'))
logging.basicConfig(level=logging.INFO)
dp = Dispatcher(bot=bot,storage=storage)

db = mg()
db.__init__()

class Main(StatesGroup):
    create_history = State()
    add_mess = State()
    send_last = State()
    send_spec = State()
@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    await message.answer('Добро пожаловать в заметки прямо в телеграм', reply_markup=kb.main_kb)
    db.add_user(message.from_user.id)

@dp.message_handler(content_types=[types.ContentType.TEXT])
async def get_text(message: types.Message):
    match message.text:
        case phr.create_new_history:
            markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/stop'))
            await message.answer(f"Отправьте название папки для сообщений",reply_markup=markup)
            await Main.create_history.set()
        case phr.all_history:
            markup = kb.all_history(db.returnUserHistory(message.from_user.id))
            if not len(markup['inline_keyboard']):
                await message.answer(f'У вас ещё нет папок')
            else:
                await message.answer(f'Ваши папки',reply_markup=markup)

        case phr.profile:
            user = db.returnUser(message.from_user.id)
            text = f'Ваш id - {message.from_user.id}\n' \
                   f'Количество папок - {len(user["saved_history_code"])}'
            await message.answer(text)

@dp.callback_query_handler(kb.send_history_info.filter())
async def get_history_info(call:types.CallbackQuery, callback_data:dict):
    history = db.returnHistory(callback_data['history_code'],call.message.chat.id)
    if history:
        text = f'Название папки - {history["history_name"]}\n' \
               f'Количество заметок  - {len(history["messages"])}'
        markup = kb.get_history_kb(history['history_code'])
        await call.message.edit_text(text,reply_markup=markup)
    else:
        await call.message.edit_text('Папки не существует')



@dp.callback_query_handler(kb.add_messages_to_history.filter())
async def add_messages_to_history(call:types.CallbackQuery, callback_data:dict):
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/stop'))
    await call.message.edit_text('Отправьте сообщение, которое нужно добавить')
    await call.message.answer('Клавиатура временно недоступна',reply_markup=markup)
    db.changeUserAddingTo(call.message.chat.id, callback_data['history_code'])
    await Main.add_mess.set()

@dp.callback_query_handler(kb.send_history_messages.filter())
async def send_history_messages_handler(call:types.CallbackQuery, callback_data:dict):
    history = db.returnHistory(callback_data['history_code'],call.message.chat.id)
    if len(history['messages']):
        await call.message.edit_text(call.message.text,reply_markup=kb.send_mess_history_kb(history['history_code']))
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(phr.back, callback_data=kb.send_history_info.new(history['history_code'])))
        await call.message.edit_text('У вас ещё нет заметок',
                                     reply_markup=markup)

@dp.callback_query_handler(kb.delete_history.filter())
async def delete_history(call:types.CallbackQuery, callback_data:dict):
    db.deleteHistory(callback_data['history_code'],call.message.chat.id)
    await call.message.edit_text('Успешно удалена папка')

@dp.callback_query_handler(kb.delete_msg.filter())
async def delete_history(call:types.CallbackQuery, callback_data:dict):
    info = callback_data['info'].split('@')
    history_code = info[0]
    idx = info[1]
    db.deleteMessageFromHistory(history_code,call.message.chat.id,idx)
    await call.message.delete()
    await call.message.answer('Успешно удалено')

async def send_mess_call(call, messages, history):
    for idx, v in enumerate(messages):
        match v['type']:
            case 'text':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                await call.message.answer(f"{v['caption']}\n\nНомер заметки - {idx + 1}", reply_markup=markup)

            case 'sticker':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                sticker = await call.message.answer_sticker(v['file_id'])
                await call.message.answer(f'Номер заметки - {idx + 1}', reply=sticker.message_id,reply_markup=markup)

            case 'video':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                if v['caption']:
                    text = f"{v['caption']}\n\nНомер заметки - {idx + 1}"
                else:
                    text = f'Номер заметки - {idx + 1}'
                await call.message.answer_video(video=v['file_id'], caption=text,reply_markup=markup)

            case 'photo':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                if v['caption']:
                    text = f"{v['caption']}\n\nНомер заметки - {idx + 1}"
                else:
                    text = f'Номер заметки - {idx + 1}'
                await call.message.answer_photo(photo=v['file_id'], caption=text,reply_markup=markup)

            case 'audio':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                if v['caption']:
                    text = f"{v['caption']}\n\nНомер заметки - {idx + 1}"
                else:
                    text = f'Номер заметки - {idx + 1}'
                await call.message.answer_audio(audio=v['file_id'], caption=text,reply_markup=markup)
            case 'animation':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                if v['caption']:
                    text = f"{v['caption']}\n\nНомер заметки - {idx + 1}"
                else:
                    text = f'Номер заметки - {idx + 1}'
                await call.message.answer_animation(animation=v['file_id'], caption=text,reply_markup=markup)
            case 'document':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                if v['caption']:
                    text = f"{v['caption']}\n\nНомер заметки - {idx + 1}"
                else:
                    text = f'Номер заметки - {idx + 1}'
                await call.message.answer_document(document=v['file_id'], caption=text,reply_markup=markup)
            case 'voice':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                await call.message.answer_voice(voice=v['file_id'], caption=f'Номер заметки - {idx + 1}',reply_markup=markup)
            case _:
                print(f'Forgotten type => {v["type"]}')


async def send_mess(message, messages, history):
    for idx, v in enumerate(messages):
        match v['type']:
            case 'text':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить',callback_data=kb.delete_msg.new(f'{history["history_code"]}@{history["messages"].index(v)}')))
                await message.answer(f"{v['caption']}\n\nНомер заметки - {history['messages'].index(v) + 1}", reply_markup=markup)

            case 'sticker':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                sticker = await message.answer_sticker(v['file_id'])
                await message.answer(f'Номер заметки - {history["messages"].index(v) + 1}', reply=sticker.message_id, reply_markup=markup)

            case 'video':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                if v['caption']:
                    text = f"{v['caption']}\n\nНомер заметки - {history['messages'].index(v) + 1}"
                else:
                    text = f'Номер заметки - {history["messages"].index(v) + 1}'
                await message.answer_video(video=v['file_id'], caption=text, reply_markup=markup)

            case 'photo':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                if v['caption']:
                    text = f"{v['caption']}\n\nНомер заметки - {history['messages'].index(v) + 1}"
                else:
                    text = f'Номер заметки - {history["messages"].index(v) + 1}'
                await message.answer_photo(photo=v['file_id'], caption=text, reply_markup=markup)

            case 'audio':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                if v['caption']:
                    text = f"{v['caption']}\n\nНомер заметки - {history['messages'].index(v) + 1}"
                else:
                    text = f'Номер заметки - {history["messages"].index(v) + 1}'
                await message.answer_audio(audio=v['file_id'], caption=text, reply_markup=markup)
            case 'animation':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                if v['caption']:
                    text = f"{v['caption']}\n\nНомер заметки - {history['messages'].index(v) + 1}"
                else:
                    text = f'Номер заметки - {history["messages"].index(v) + 1}'
                await message.answer_animation(animation=v['file_id'], caption=text,reply_markup=markup)

            case 'document':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                if v['caption']:
                    text = f"{v['caption']}\n\nНомер заметки - {history['messages'].index(v) + 1}"
                else:
                    text = f'Номер заметки - {history["messages"].index(v) + 1}'
                await message.answer_document(document=v['file_id'], caption=text,reply_markup=markup)
            case 'voice':
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Удалить', callback_data=kb.delete_msg.new(
                    f'{history["history_code"]}@{history["messages"].index(v)}')))
                await message.answer_voice(voice=v['file_id'], caption=f'Номер заметки - {history["messages"].index(v) + 1}',reply_markup=markup)
            case _:
                print(f'Forgotten type => {v["type"]}')

@dp.callback_query_handler(kb.all_mess_send_history.filter())
async def send_all_mess_history(call:types.CallbackQuery, callback_data:dict):
    history = db.returnHistory(callback_data['history_code'], call.message.chat.id)
    await send_mess_call(call,history["messages"],history)
    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(kb.send_only_last_mess_history.filter())
async def send_last_mess_history(call:types.CallbackQuery, callback_data:dict):
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/stop'))
    history = db.returnHistory(callback_data['history_code'], call.message.chat.id)
    db.changeUserAddingTo(call.message.chat.id, history["history_code"])
    await call.message.edit_text(f'Сколько заметок вам нужно отправить? От 1 до {len(history["messages"])}',reply_markup=markup)
    await Main.send_last.set()

@dp.callback_query_handler(kb.send_specific_mess_history.filter())
async def send_specific_mess_history(call:types.CallbackQuery, callback_data:dict):
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/stop'))
    history = db.returnHistory(callback_data['history_code'], call.message.chat.id)
    db.changeUserAddingTo(call.message.chat.id, history["history_code"])
    await call.message.edit_text(f'Какую заметку вам нужно отправить? От 1 до {len(history["messages"])}',reply_markup=markup)
    await Main.send_spec.set()

@dp.message_handler(state=Main.add_mess,content_types=[
            types.ContentType.PHOTO,
            types.ContentType.DOCUMENT,
            types.ContentType.TEXT,
            types.ContentType.AUDIO,
            types.ContentType.VOICE,
            types.ContentType.VIDEO
        ])
async def adding_messages_to_his(message: types.Message, state: FSMContext):
    user = db.returnUser(message.from_user.id)
    msg = {}
    match message.content_type:
        case 'photo':
            msg = {
                'type':'photo',
                'file_id':message.photo[-1].file_id,
                'caption':message.caption
            }
        case 'text':
            if message.text == '/stop':
                await message.answer('Успешно завершено добавление сообщений',reply_markup=kb.main_kb)
                await state.finish()
                return
            msg = {
                'type':'text',
                'file_id':None,
                'caption':message.text
            }
        case 'video':
            msg = {
                'type':'video',
                'file_id':message.video.file_id,
                'caption':message.caption
            }
        case 'sticker':
            msg = {
                'type':'sticker',
                'file_id':message.sticker.file_id,
                'caption':None
            }
        case 'audio':
            msg ={
                'type':'audio',
                'file_id':message.audio.file_id,
                'caption':message.caption
            }
        case 'animation':
            msg = {
                'type':'animation',
                'file_id':message.animation.file_id,
                'caption':message.caption
            }
        case 'document':
            msg = {
                'type':'document',
                'file_id':message.document.file_id,
                'caption':message.caption
            }
        case 'voice':
            msg = {
                'type':'voice',
                'file_id':message.voice.file_id,
                'caption':None
            }

    if msg:
        db.addNewMessageToHistory(user['adding_to_history_code'],user['user_id'],msg)
        await message.answer('Успешно добавлено',reply=message.message_id)


@dp.message_handler(state=Main.send_last)
async def sendLastHistoryMessage(message: types.Message, state: FSMContext):
    if message.text != '/stop':
        try:
            number = int(message.text)
            user = db.returnUser(message.from_user.id)
            history = db.returnHistory(user['adding_to_history_code'], user['user_id'])
            if number in range(len(history['messages']) + 1):
                await send_mess(message, history["messages"][-number:],history)
                await message.answer('Клавиатура доступна',reply_markup=kb.main_kb)
                await state.finish()
            else:
                await message.answer('Вы отправили число в неправильном диапазоне')
        except:
            await message.answer('Отправьте только число')
    else:
        await message.answer('Успешно завершено',reply_markup=kb.main_kb)
        await state.finish()

@dp.message_handler(state=Main.send_spec)
async def sendSpecificHistory(message: types.Message, state: FSMContext):
    if message.text != '/stop':

        try:
            number = int(message.text)
            user = db.returnUser(message.from_user.id)
            history = db.returnHistory(user['adding_to_history_code'], user['user_id'])
            if number in range(len(history['messages']) + 1):

                msg = []
                msg.append(history["messages"][number-1])
                await send_mess(message, msg,history)
                await message.answer('Клавиатура доступна',reply_markup=kb.main_kb)

                await state.finish()
            else:
                await message.answer('Вы отправили число в неправильном диапазоне')
        except ValueError:
            await message.answer('Отправьте только число')
    else:
        await message.answer('Успешно завершено',reply_markup=kb.main_kb)
        await state.finish()


@dp.message_handler(state=Main.create_history)
async def creatingHistory(message: types.Message, state: FSMContext):
    if message.text != '/stop':
        history_name = message.text
        history_code = logic.create_translit(history_name)
        db.add_history(history_name, message.from_user.id)
        db.giveHistoryToUser(message.from_user.id,history_code)
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton(phr.back, callback_data=kb.send_history_info.new(history_code)))
        await message.answer(f'Папка под названием {history_name} была создана', reply_markup=markup)
        await message.answer(f'Клавиатура доступна',reply_markup=kb.main_kb)
        await state.finish()
    else:
        await message.answer('Успешно отменено',reply_markup=kb.main_kb)
        await state.finish()

async def on_startup(_):
    print('Бот вышел в онлайн')
if __name__== '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

