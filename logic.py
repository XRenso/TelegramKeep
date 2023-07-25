from cyrtranslit import to_latin

def create_translit(text:str) ->str:
    text = "_".join(text.lower().split())
    return to_latin(text.lower())

