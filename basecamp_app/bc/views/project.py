from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from ..utils import session_get_token_and_identity, bc_api_get, api_project_get_all_projects_uri


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
        course_list += ('<li><a href="'+project["app_url"] +
                        f'" target="_blank">{project["id"]}</a> {project["name"]}</li>')
        print(project)

    if "Link" in response.headers:
        print(response.headers["Link"])

    total_count = 0
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])

    total_count_str = f'total projects: {total_count}' if total_count > 0 else ''

    return HttpResponse(
        '<a href="' + reverse('bc-main') + '">back to main</a><br/>'
        f'{total_count_str}'
        f'{course_list}')
