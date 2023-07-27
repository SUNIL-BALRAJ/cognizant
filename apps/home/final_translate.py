from .detection import language

def final(input,path):
    print("In translate.py")
    from googletrans import Translator
    lang=language(path)
    k=Translator()
    output=k.translate(input,src='en',dest=lang)
    return output.text