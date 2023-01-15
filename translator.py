import re

TRANSLATION = {
    'man': 'мужчина',
    'woman': 'женщина',
    'astronaut': 'космонавт',
    'bull': 'бык',
    'usual': 'обычное',
    'chronically': 'хроник',
    'disabled': 'инвалид',
    'depressed': 'депрессия',
    'nervos': 'нервное',
    'normal': 'нормальное',
    'in good form': 'в хорошей форме',
    'happy': 'счастлив',
    'wretched': 'никудышный',
    'squalid': 'нищий',
    'poor': 'бедный',
    'modest': 'скромный',
    'comfortable': 'средний',
    'wealthy': 'богатый',
    'aristocratic': 'аристократичный'
}


def translate(text):
    text = str(text)
    while bool(re.match('[a-zA-Z]', text)):
        for i in TRANSLATION:
            if i in text:
                text = text.replace(i, TRANSLATION[i])
                break
    return text
