from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import Template, Context

from bc.utils import (session_get_token_and_identity, bc_api_get, api_project_get_all_projects_uri,
                      api_project_get_project_uri, static_get_recording_types)
from bc.models import BcProject, BcProjectTool


def app_project_main(request):

    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get all projects API
    response = bc_api_get(uri=api_project_get_all_projects_uri(), access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    project_list = []
    for project in data:
        project_list.append({
            'id': project["id"],
            'name': project["name"],
            'url': reverse('app-project-detail', kwargs={'project_id': project["id"]})})

    # if 'next' in response.links and 'url' in response.links["next"]:
    #     print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    total_count_str = f'total projects: {total_count}' if total_count > 0 else ''

    # sanitize to avoid xss
    t = Template('<a href="' + reverse('bc-main') + '">back to main</a><br/>{{total_count_str}}'
                 '{% for project in project_list %}'
                 '<li><a href="{{ project.url }}">{{ project.id }}</a> {{ project.name }}</li>'
                 '{% endfor %}')
    c = Context({'total_count_str': total_count_str, 'project_list': project_list})
    return HttpResponse(t.render(context=c))


def app_project_detail(request, project_id, update_db=False):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get project API
    api_project_get_project = api_project_get_project_uri(project_id=project_id)
    response = bc_api_get(uri=api_project_get_project, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    tool_list = []
    for tool in data["dock"]:
        if tool["enabled"]:
            if tool["name"] in ['todoset']:
                tool_list.append({
                    'id': tool["id"],
                    'title': tool["title"],
                    'name': tool["name"],
                    'url': reverse('app-todoset-detail',
                                   kwargs={'bucket_id': project_id, 'todoset_id': tool["id"]})
                })
            elif tool["name"] in ['message_board']:
                tool_list.append({
                    'id': tool["id"],
                    'title': tool["title"],
                    'name': tool["name"],
                    'url': reverse('app-message-board-detail',
                                   kwargs={'bucket_id': project_id, 'message_board_id': tool["id"]})
                })
            elif tool["name"] in ['questionnaire']:
                tool_list.append({
                    'id': tool["id"],
                    'title': tool["title"],
                    'name': tool["name"],
                    'url': reverse('app-questionnaire-detail',
                                   kwargs={'bucket_id': project_id, 'questionnaire_id': tool["id"]})
                })
            elif tool["name"] in ['schedule']:
                tool_list.append({
                    'id': tool["id"],
                    'title': tool["title"],
                    'name': tool["name"],
                    'url': reverse('app-schedule-detail',
                                   kwargs={'bucket_id': project_id, 'schedule_id': tool["id"]})
                })
            elif tool["name"] in ['vault']:
                tool_list.append({
                    'id': tool["id"],
                    'title': tool["title"],
                    'name': tool["name"],
                    'url': reverse('app-vault-detail',
                                   kwargs={'bucket_id': project_id, 'vault_id': tool["id"]})
                })
            else:  # other tools
                tool_list.append({
                    'id': tool["id"],
                    'title': tool["title"],
                    'name': tool["name"],
                    'url': '#'
                })

    recording_type_list = []
    for recording_type in static_get_recording_types():
        recording_type_list.append({
            'type': recording_type,
            'url': reverse('app-project-recording-by-type',
                           kwargs={'bucket_id': project_id, 'recording_type': recording_type})
        })

    if update_db:
        # let's try to remove the m2m dock first
        project_dock = data.pop('dock')

        # load project or create new project from data
        try:
            project = BcProject.objects.get(id=project_id)
        except BcProject.DoesNotExist:
            project = BcProject.objects.create(**data)

        # process tools in the dock, make sure all tools exist
        for tool in project_dock:

            try:
                _tool = BcProjectTool.objects.get(id=tool["id"])
            except BcProjectTool.DoesNotExist:
                _tool = BcProjectTool.objects.create(**tool)

            # make sure tool in the project exist
            if not project.dock.filter(id=_tool.id).exists():
                project.dock.add(_tool)

    # sanitize to avoid xss
    t = Template('<a href="' + reverse('app-project-main') + '">back</a><br/>'
                 'project: {{ project.id }}<br/>'
                 'name: {{ project.name }}<br/>'
                 'purpose: {{ project.purpose }}<br/>'
                 'created_at: {{ project.created_at }}<br/>'
                 'enabled tools: <br/>'
                 '{% for tool in tool_list %}'
                 '{% if tool.url == "#" %}'
                 '<li>{{ tool.id }} {{ tool.title }} ({{ tool.name }})</li>'
                 '{% else %}'
                 '<li><a href="{{ tool.url }}">{{ tool.id }}</a> {{ tool.title }} ({{ tool.name }})</li>'
                 '{% endif %}'
                 '{% endfor %}<br/>'
                 '<a href="{{ message_types_url }}">message types</a><br/>'
                 'recording types: <br/>'
                 '{% for recording_type in recording_type_list %}'
                 '<li><a href="{{ recording_type.url }}">{{ recording_type.type }}</a></li>'
                 '{% endfor %}<br/>')
    message_types_url = reverse('app-message-type', kwargs={'bucket_id': project_id})
    c = Context({'project': data,
                 'tool_list': tool_list,
                 'message_types_url': message_types_url,
                 'recording_type_list': recording_type_list})
    return HttpResponse(t.render(context=c))
