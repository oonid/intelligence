from django.urls import reverse
from bc.utils import static_get_recording_parent_types


def static_get_recording_parent_uri(parent, bucket):
    if ('type' in parent and parent["type"] in static_get_recording_parent_types() and
            'type' in bucket and bucket["type"] == "Project"):
        if parent["type"] == 'Todo':
            return reverse('app-todo-detail', kwargs={'bucket_id': bucket["id"], 'todo_id': parent["id"]})
        elif parent["type"] == 'Todolist':
            return reverse('app-todolist-detail',
                           kwargs={'bucket_id': bucket["id"], 'todolist_id': parent["id"]})
        else:
            return '#'  # uri is None
    else:
        return '#'  # uri is None
