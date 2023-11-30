from django.urls import reverse


def repr_message_detail(message, bucket_id, message_obj=None, as_list=False):
    _saved_on_db = '(db)' if message_obj else ''
    _repr = (f'<a href="' + reverse('app-message-detail',
                                    kwargs={'bucket_id': bucket_id, 'message_id': message["id"]}) +
             f'">{message["id"]}</a> {message["title"]} {_saved_on_db}')

    return '<li>'+_repr+'</li>' if as_list else _repr


def repr_message_detail_not_found(message, bucket_id):
    return (f'{message["type"]} {message["id"]} not found<br/>'
            f'<a href="' + reverse('app-message-detail',
                                   kwargs={'bucket_id': bucket_id, 'message_id': message["id"]}) +
            f'">try to open {message["type"]}</a> first.')
