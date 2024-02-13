from django.urls import reverse
from django.template import Template, Context


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


def repr_http_response_template_string(template_str, context_dict=None):
    # sanitize to avoid xss
    t = Template(template_str)
    c = Context({} if context_dict is None else context_dict)
    return t.render(context=c)


def repr_template_response_entity_not_found(parent_id, parent_type, href):
    template_str = ('{{ parent_type }} {{ parent_id }} not found<br/>'
                    '<a href="{{ href }}">try to open {{ parent_type }}</a> first.')
    context_dict = {'parent_id': parent_id, 'parent_type': parent_type, 'href': href}
    return repr_http_response_template_string(template_str=template_str, context_dict=context_dict)


def repr_template_response_parent_not_in_list(parent_id, parent_type, list_parent_types):
    template_str = 'parent {{ parent_id }} type {{ parent_type }} not in {{ list_parent_types }}.'
    context_dict = {'parent_id': parent_id, 'parent_type': parent_type, 'list_parent_types': list_parent_types}
    return repr_http_response_template_string(template_str=template_str, context_dict=context_dict)


def repr_template_response_entity_creator_bucket_parent(entity_type, entity_title, list_parent_types):
    template_str = ('{{ entity_type }} {{ entity_title }} has no creator or bucket type Project or parent type in '
                    '{{ list_parent_types }}')
    context_dict = {'entity_type': entity_type, 'entity_title': entity_title, 'list_parent_types': list_parent_types}
    return repr_http_response_template_string(template_str=template_str, context_dict=context_dict)
