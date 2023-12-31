from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
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

    course_list = ""
    for project in data:
        course_list += ('<li><a href="' + reverse('app-project-detail', kwargs={'project_id': project["id"]}) +
                        f'">{project["id"]}</a> {project["name"]}</li>')

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    total_count_str = f'total projects: {total_count}' if total_count > 0 else ''

    return HttpResponse(
        '<a href="' + reverse('bc-main') + '">back to main</a><br/>'
        f'{total_count_str}'
        f'{course_list}')


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

    tools = ""
    for tool in data["dock"]:
        if tool["enabled"]:
            if tool["name"] in ['todoset']:
                tools += (f'<li><a href="' +
                          reverse('app-todoset-detail',
                                  kwargs={'bucket_id': project_id, 'todoset_id': tool["id"]}) + f'">{tool["id"]}</a> '
                          f'{tool["title"]} ({tool["name"]})</li>')
            elif tool["name"] in ['message_board']:
                tools += (f'<li><a href="' +
                          reverse('app-message-board-detail',
                                  kwargs={'bucket_id': project_id, 'message_board_id': tool["id"]}) +
                          f'">{tool["id"]}</a> '
                          f'{tool["title"]} ({tool["name"]})</li>')
            elif tool["name"] in ['questionnaire']:
                tools += (f'<li><a href="' +
                          reverse('app-questionnaire-detail',
                                  kwargs={'bucket_id': project_id, 'questionnaire_id': tool["id"]}) +
                          f'">{tool["id"]}</a> '
                          f'{tool["title"]} ({tool["name"]})</li>')
            elif tool["name"] in ['schedule']:
                tools += (f'<li><a href="' +
                          reverse('app-schedule-detail',
                                  kwargs={'bucket_id': project_id, 'schedule_id': tool["id"]}) +
                          f'">{tool["id"]}</a> '
                          f'{tool["title"]} ({tool["name"]})</li>')
            elif tool["name"] in ['vault']:
                tools += (f'<li><a href="' +
                          reverse('app-vault-detail',
                                  kwargs={'bucket_id': project_id, 'vault_id': tool["id"]}) +
                          f'">{tool["id"]}</a> '
                          f'{tool["title"]} ({tool["name"]})</li>')
            else:  # other tools
                tools += f'<li>{tool["title"]} ({tool["name"]})</li>'

    recording_type_list = ""
    for recording_type in static_get_recording_types():
        recording_type_list += ('<li><a href="' +
                                reverse('app-project-recording-by-type',
                                        kwargs={'bucket_id': project_id, 'recording_type': recording_type}) +
                                f'">{recording_type}</a></li>')

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

        print(f'project: {project.name} '
              f'dock: {project.dock.count()} '
              f'enabled: {project.dock.filter(enabled=True).count()}')

    return HttpResponse(
        '<a href="' + reverse('app-project-main') + '">back</a><br/>'
        f'project: {data["id"]}<br/>'
        f'name: {data["name"]}<br/>'
        f'purpose: {data["purpose"]}<br/>'
        f'created_at: {data["created_at"]}<br/>'
        f'enabled tools: <br/>{tools}<br/>'
        '<a href="'+reverse('app-message-type', kwargs={'bucket_id': project_id})+'">message types</a><br/>'
        f'recording types: <br/>{recording_type_list}<br/>'
    )
