print('https://repl.it/@Levashov/messenger')

# name = 'Jack'
# name = name + 'Black'
# print(name)


# a = [1, 2, 3, 4, 5, 6]
# a.append(7)
# print(a)
# print(a[-1])

# message1 = [
#     'Jack',
#     'Привет всем, я Jack',
#     '4 mar 2021'
# ]
# print(message1[3])

# message2 = {
#     'name': 'Jack',
#     'text': 'Привет всем, я Jack',
#     'time': '4 mar 2021',
# }
# print(message2['name'])

# def my_func(arg1, arg2):
#     print(arg1, arg2)
#     # return arg1 + arg2

# result = my_func(1, 3)
# print(result)

# result = my_func('Jack', 'Black')
# print(result)

from pprint import pprint
from datetime import datetime
import time

print(time.time())

messages = [
    {
        'name': 'Jack',
        'text': 'Привет всем, я Jack',
        'time': 1614887855.3456457,
    },
    {
        'name': 'Mary',
        'text': 'Привет Jack, я - Mary',
        'time': 1614887857.3456457,
    }
]
pprint(messages)
print()
# print(messages[0]['text'], messages[0]['name'], sep='|')

def send_message(name, text):
    message = {
        'name': name,
        'text': text,
        'time': time.time()
    }
    messages.append(message)

def get_messages(after):
    response = []
    for message in messages:
        if message['time'] > after:
            response.append(message)
    return response[:50]

# pprint(get_messages(0))


send_message('Jack', 'Привет, Mary')

response = get_messages(0)
pprint(response)
print()

after = response[-1]['time']

response = get_messages(after)
pprint(response)
print()

response = get_messages(after)
pprint(response)
print()

send_message('Jack', '1')
send_message('Jack', '2')

response = get_messages(after)
pprint(response)
print()

after = response[-1]['time']
