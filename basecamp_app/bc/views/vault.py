from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get,
                      api_vault_get_bucket_vault_uri, api_vault_get_bucket_vault_vaults_uri,
                      api_vault_get_bucket_vault_documents_uri, api_document_get_bucket_document_uri,
                      api_vault_get_bucket_vault_uploads_uri, api_document_get_bucket_upload_uri)


def app_vault_detail(request, bucket_id, vault_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get vault API
    api_vault_get_bucket_vault = api_vault_get_bucket_vault_uri(bucket_id=bucket_id, vault_id=vault_id)
    response = bc_api_get(uri=api_vault_get_bucket_vault, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    vault = response.json()
    print(vault)
    print(vault.keys())

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {vault["title"]}<br/>'
        f'<a href="' + reverse('app-vault-documents',
                               kwargs={'bucket_id': bucket_id, 'vault_id': vault_id}) +
        f'">{vault["documents_count"]} documents</a><br/>'
        f'<a href="' + reverse('app-vault-uploads', kwargs={'bucket_id': bucket_id, 'vault_id': vault_id}) +
        f'">{vault["uploads_count"]} uploads</a><br/>'
        f'<a href="' + reverse('app-vault-vaults',
                               kwargs={'bucket_id': bucket_id, 'vault_id': vault["id"]}) +
        f'">{vault["vaults_count"]} vaults</a><br/>'
    )


def app_vault_vaults(request, bucket_id, vault_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get vault vaults API
    api_vault_get_bucket_vault_vaults = api_vault_get_bucket_vault_vaults_uri(bucket_id=bucket_id, vault_id=vault_id)
    response = bc_api_get(uri=api_vault_get_bucket_vault_vaults, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()

    count = 0
    vault_list = ""
    for vault in data:
        print(vault)

        vault_list += (f'<li><a href="' + reverse('app-vault-detail',
                                                  kwargs={'bucket_id': bucket_id, 'vault_id': vault["id"]}) +
                       f'">{vault["id"]}</a> {vault["title"]} '
                       f'{vault["documents_count"]} documents '
                       f'{vault["uploads_count"]} uploads '
                       f'{vault["vaults_count"]} vaults'
                       '</li>')

        count += 1

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} vaults'

    return HttpResponse(
        '<a href="' + reverse('app-vault-detail',
                              kwargs={'bucket_id': bucket_id, 'vault_id': vault_id}) + '">back</a><br/>'
        f'{total_count_str}<br/>'
        f'{vault_list}<br/>'
    )


def app_document_detail(request, bucket_id, document_id):
    """
        basecamp document is different from CloudFile and GoogleDocument

    :param request:
    :param bucket_id:
    :param document_id:
    :return:
    """
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get vault API
    api_document_get_bucket_document = (
        api_document_get_bucket_document_uri(bucket_id=bucket_id, document_id=document_id))
    response = bc_api_get(uri=api_document_get_bucket_document, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    document = response.json()
    print(document)

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {document["title"]}<br/>'
    )


def app_vault_documents(request, bucket_id, vault_id):
    """
        basecamp document is different from CloudFile and GoogleDocument

    :param request:
    :param bucket_id:
    :param vault_id:
    :return:
    """
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get vault vaults API
    api_vault_get_bucket_vault_documents = (
        api_vault_get_bucket_vault_documents_uri(bucket_id=bucket_id, vault_id=vault_id))
    response = bc_api_get(uri=api_vault_get_bucket_vault_documents, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    print(data)

    count = 0
    document_list = ""
    for document in data:
        print(document)

        document_list += (f'<li><a href="' + reverse('app-document-detail',
                                                     kwargs={'bucket_id': bucket_id, 'document_id': document["id"]}) +
                          f'">{document["id"]}</a> {document["title"]} '
                          '</li>')

        count += 1

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} documents'

    return HttpResponse(
        '<a href="' + reverse('app-vault-detail',
                              kwargs={'bucket_id': bucket_id, 'vault_id': vault_id}) + '">back</a><br/>'
        f'{total_count_str}<br/>'
        f'{document_list}<br/>'
    )


def app_upload_detail(request, bucket_id, upload_id):
    """
        basecamp upload is different from CloudFile and GoogleDocument

    :param request:
    :param bucket_id:
    :param upload_id:
    :return:
    """
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get vault API
    api_document_get_bucket_upload = (
        api_document_get_bucket_upload_uri(bucket_id=bucket_id, upload_id=upload_id))
    response = bc_api_get(uri=api_document_get_bucket_upload, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    upload = response.json()
    print(upload)

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {upload["title"]}<br/>'
    )


def app_vault_uploads(request, bucket_id, vault_id):
    """
        basecamp upload is different from CloudFile and GoogleDocument

    :param request:
    :param bucket_id:
    :param vault_id:
    :return:
    """
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get vault vaults API
    api_vault_get_bucket_vault_uploads = (
        api_vault_get_bucket_vault_uploads_uri(bucket_id=bucket_id, vault_id=vault_id))
    response = bc_api_get(uri=api_vault_get_bucket_vault_uploads, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse('', status=response.status_code)

    # if OK
    data = response.json()
    print(data)

    count = 0
    upload_list = ""
    for upload in data:
        print(upload)

        upload_list += (f'<li><a href="' + reverse('app-upload-detail',
                                                   kwargs={'bucket_id': bucket_id, 'upload_id': upload["id"]}) +
                        f'">{upload["id"]}</a> {upload["title"]} '
                        '</li>')

        count += 1

    if 'next' in response.links and 'url' in response.links["next"]:
        print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} uploads'

    return HttpResponse(
        '<a href="' + reverse('app-vault-detail',
                              kwargs={'bucket_id': bucket_id, 'vault_id': vault_id}) + '">back</a><br/>'
        f'{total_count_str}<br/>'
        f'{upload_list}<br/>'
    )
