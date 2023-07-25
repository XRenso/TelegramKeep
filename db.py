import pymongo
from dotenv import load_dotenv
import os

import logic


class Mongo:
    def __init__(self):
        self.connection = pymongo.MongoClient(os.getenv('MONGO'))['telegramKeep']
        self.user = self.connection['user']
        self.history = self.connection['history']

    def add_user(self,user_id:int) -> None:
        if not self.returnUser(user_id):
            user={
                'user_id':user_id,
                'saved_history_code':[],
                'adding_to_history_code':None,
                'is_admin':False
            }
            self.user.insert_one(user)


    def returnUser(self,user_id:int) ->dict:
        return self.user.find_one({'user_id':user_id})

    def add_history(self,history_name:str,user_id:int):
        if not self.returnHistory(logic.create_translit(history_name),user_id):
            history ={
                'history_code':logic.create_translit(history_name),
                'history_name':history_name,
                'user_id':user_id,
                'messages':[]
            }
            self.history.insert_one(history)

    def returnHistory(self,history_code:str,user_id:int) -> dict:
        return self.history.find_one({'history_code':history_code,'user_id':user_id})

    def returnUserHistory(self,user_id:int):
        return self.history.find({'user_id':user_id})

    def giveHistoryToUser(self,user_id:int,history_code:str):
        if self.returnUser(user_id):
            self.user.update_one({'user_id':user_id},{'$push':{'saved_history_code':history_code}})

    def add_message_to_history(self,user_id:int,history_code:str,message:dict):
        if self.returnHistory(history_code,user_id):
            self.history.update_one({'history_code':history_code,'user_id':user_id},{'$push':{'messages':message}})

    def addNewMessageToHistory(self,history_code:str,user_id:int,message):
        if self.returnHistory(history_code,user_id):
            self.history.update_one({'user_id':user_id,'history_code':history_code},{'$push':{'messages':message}})

    def deleteMessageFromHistory(self,history_code:str,user_id:int,msg_id:int):
        if self.returnHistory(history_code,user_id):
            self.history.update_one({'user_id':user_id,'history_code':history_code},{'$unset':{f'messages.{msg_id}':1}})
            self.history.update_one({'user_id':user_id,'history_code':history_code},{'$pull':{f'messages':None}})


    def deleteHistory(self,history_code:str,user_id:int):
        if self.returnHistory(history_code,user_id):
            self.user.update_one({'user_id':user_id},{'$pull':{'saved_history_code':history_code}})
            self.history.delete_one({'user_id':user_id,'history_code':history_code})

    def changeUserAddingTo(self,user_id:int, history_code:str):
        if self.returnHistory(history_code,user_id):
            self.user.update_one({'user_id':user_id},{'$set':{'adding_to_history_code':history_code}})