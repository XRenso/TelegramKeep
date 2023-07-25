from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import phrases as phr

send_history_info = CallbackData('history_info','history_code')
send_history_messages = CallbackData('send_his_mess','history_code')

delete_history = CallbackData('delete_history','history_code')
add_messages_to_history = CallbackData('add_messages_to_his', 'history_code')

delete_msg = CallbackData('delete_msg_from_his','info')

profile = KeyboardButton(phr.profile)
create_history = KeyboardButton(phr.create_new_history)
all_history = KeyboardButton(phr.all_history)

main_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(create_history).row(all_history,profile)


all_mess_send_history = CallbackData('send_all_history_messages','history_code')
send_only_last_mess_history = CallbackData('send_only_last_mess_his','history_code')
send_specific_mess_history = CallbackData('send_spec_mess_his','history_code')


def send_mess_history_kb(history_code):
    markup = InlineKeyboardMarkup()
    send_all_messages = InlineKeyboardButton(phr.send_all, callback_data=all_mess_send_history.new(history_code))
    send_last_messages = InlineKeyboardButton(phr.send_last, callback_data=send_only_last_mess_history.new(history_code))
    send_specif_messages = InlineKeyboardButton(phr.send_specif, callback_data=send_specific_mess_history.new(history_code))
    markup.add(send_all_messages).row(send_last_messages,send_specif_messages).add(InlineKeyboardButton(phr.back,callback_data=send_history_info.new(history_code)))
    return markup


def get_history_kb(history_code:str):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Отправить заметки', callback_data=send_history_messages.new(history_code)))
    markup.row(InlineKeyboardButton('Удалить', callback_data=delete_history.new(history_code)), InlineKeyboardButton('Добавить заметки',callback_data=add_messages_to_history.new(history_code)))
    return markup


def all_history(histories):
    markup = InlineKeyboardMarkup()
    if histories != 0:
        for i in histories:
            markup.add(InlineKeyboardButton(i['history_name'],callback_data=send_history_info.new(i['history_code'])))
    return markup