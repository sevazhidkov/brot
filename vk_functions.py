import vk_api
from time import sleep
from config import VK_LOGIN, VK_PASSWORD

vk = vk_api.VkApi(login=VK_LOGIN, password=VK_PASSWORD)  # Authorization in VK


def get_message(last_message_id=0, specify_dialog=False,
                specify_dialog_type=None, id=None):
    """ Получение сообщения из ВКонтакте


    :param last_message_id: id последнего обработанного сообщения
    :param specify_dialog: получать сообщение из конкретного диалога
    :param specify_dialog_type: тип конкретного диалога (chat/user)
    :param id: id конкретного диалога, если параметр type равен True
    :return: словарь с данными о сообщении
    """

    if specify_dialog and specify_dialog_type and id:
        values = {
            'count': 1,
            'start_message_id': last_message_id
        }
        if specify_dialog_type == 'chat':
            values.update({'chat_id': id})
        elif specify_dialog_type == 'user':
            values.update({'user_id': id})
        else:
            print("Передан неправильный specify_dialog_type")
        response = vk_method('messages.getHistory', values)
    else:
        values = {
            'count': 1,
            'last_message_id': last_message_id
        }
        response = vk_method('messages.get', values)

    if response["items"]:
        loaded_message = response["items"][0]
        loaded_attachments = []
        if "attachments" in loaded_message:
            for attachment in loaded_message['attachments']:
                type_of_attachment = attachment['type']
                loaded_attachments.append('{type}{owner}_{id}'.format(
                    type=type_of_attachment,
                    owner=attachment[type_of_attachment]['owner_id'],
                    id=attachment[type_of_attachment]['id']
                ))

        message = {
            'id': loaded_message['id'],
            'sender_id': loaded_message['user_id'],
            'type': 'chat' if 'chat_id' in loaded_message else 'user',
            'chat': loaded_message['chat_id'] if 'chat_id' in loaded_message else None,
            'text': loaded_message['body'],
            'attachments': loaded_attachments
        }
        return message
    else:
        return None



def send_message(message='Произошла ошибка. Код ошибки: 02.2.0',
                 attachments=[], type='user', send_to=91670994):
    """ Отправляет сообщение и вложения к нему


    :rtype : dict
    :param message: текст сообщения
    :param attachments: список вложений
    :param type: тип получателя сообщения (user/chat)
    :param send_to: id получателя сообщения
    :return: результат отправки сообщения
    """
    values = {
        'message': message,
        'attachment': ','.join(attachments)
    }

    error_values = {
        'message': 'Увы, у нас возникли проблемы. Попробуйте другую команду.'
    }

    if type == 'chat':
        values.update({'chat_id': send_to})
        error_values.update({'chat_id': send_to})
    else:
        values.update({'user_id': send_to})
        error_values.update({'user_id': send_to})
    try:
        response = vk_method('messages.send', values)
    except vk_api.ApiError as error:
        response = vk_method('messages.send', error_values)
        return None
    except vk_api.Captcha:
        print("Появилась каптча")
        return None
    return response


def vk_method(method, values):
    """ Использование метода ВКонтакте


    :param method: необходимый метод
    :param values: параметры для метода
    :return: ответ ВКонтакте на запрос
    """
    response = vk.method(method, values)
    return response


def fast_send_message(message, text, attachments = []):
    """ Быстро отправить сообщение в беседу или чат, в зависимости
        от параметра 'message'


    :param message: словарь сообщения, возвращаемый get_message
    :param text: текст для отправки
    :param attachments: вложения для отправки
    :return: результат отправки сообщения
    """
    return send_message(
        message=text,
        attachments=attachments,
        type=message['type'],
        send_to=message['sender_id'] if message['type'] == 'user'
                else message['chat']
    )
