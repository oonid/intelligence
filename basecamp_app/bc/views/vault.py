from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from bc.utils import (session_get_token_and_identity, bc_api_get, db_get_bucket, db_get_vault_parent,
                      api_vault_get_bucket_vault_uri, api_vault_get_bucket_vault_vaults_uri,
                      api_vault_get_bucket_vault_documents_uri, api_document_get_bucket_document_uri,
                      api_vault_get_bucket_vault_uploads_uri, api_document_get_bucket_upload_uri,
                      static_get_vault_parent_types)
from bc.models import BcPeople, BcVault, BcDocument, BcUpload
from bc.serializers import BcPeopleSerializer


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

    if 'bucket' in vault and vault["bucket"]["type"] == "Project" and 'creator' in vault:

        # process bucket first, because at processing parent still need a valid bucket
        bucket, message = db_get_bucket(bucket_id=vault["bucket"]["id"])
        if not bucket:  # not exists
            return HttpResponseBadRequest(message)

        if 'parent' in vault and vault["parent"]["type"] in static_get_vault_parent_types():
            # process parent with type listed in static_get_vault_parent_types
            parent, message = db_get_vault_parent(parent=vault["parent"], bucket_id=vault["bucket"]["id"])
            if not parent:  # not exists
                return HttpResponseBadRequest(message)

            # remove 'parent' key from vault, will use model instance parent instead
            vault.pop('parent')

        else:  # no parent, as root vault has no parent
            parent = None

        # process creator
        try:
            creator = BcPeople.objects.get(id=vault["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=vault["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'bucket' key from vault. key 'bucket' still used in processing parent
        vault.pop('bucket')

        # remove 'creator' key from vault, will use model instance creator instead
        vault.pop('creator')

        # process vault
        try:
            _vault = BcVault.objects.get(id=vault["id"])
        except BcVault.DoesNotExist:
            _vault = BcVault.objects.create(bucket=bucket, parent=parent, creator=creator, **vault)
            _vault.save()

    else:
        return HttpResponseBadRequest(
            f'vault {vault["title"]} has no creator or bucket type Project')

    _vault_title = _vault.title if _vault else vault["title"]

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_vault_title}<br/>'
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

    # parent of document same with parent of vault: Vault
    if ('parent' in document and document["parent"]["type"] in static_get_vault_parent_types() and
            'bucket' in document and document["bucket"]["type"] == "Project" and 'creator' in document):

        # process bucket first, because at processing parent still need a valid bucket
        bucket, message = db_get_bucket(bucket_id=document["bucket"]["id"])
        if not bucket:  # not exists
            return HttpResponseBadRequest(message)

        # process parent with type listed in static_get_vault_parent_types (same with document parent)
        parent, message = db_get_vault_parent(parent=document["parent"], bucket_id=document["bucket"]["id"])
        if not parent:  # not exists
            return HttpResponseBadRequest(message)

        # process creator
        try:
            creator = BcPeople.objects.get(id=document["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=document["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'bucket' key from document. key 'bucket' still used in processing parent
        document.pop('bucket')

        # remove 'parent' key from document, will use model instance parent instead
        document.pop('parent')

        # remove 'creator' key from document, will use model instance creator instead
        document.pop('creator')

        # process document
        try:
            _document = BcDocument.objects.get(id=document["id"])
        except BcDocument.DoesNotExist:
            _document = BcDocument.objects.create(bucket=bucket, parent=parent, creator=creator, **document)
            _document.save()

    else:
        return HttpResponseBadRequest(
            f'document {document["title"]} has no creator or bucket type Project or parent type in '
            f'{static_get_vault_parent_types()}')

    _document_title = _document.title if _document else document["title"]

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_document_title}<br/>'
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

    # parent of upload same with parent of vault: Vault
    if ('parent' in upload and upload["parent"]["type"] in static_get_vault_parent_types() and
            'bucket' in upload and upload["bucket"]["type"] == "Project" and 'creator' in upload):

        # process bucket first, because at processing parent still need a valid bucket
        bucket, message = db_get_bucket(bucket_id=upload["bucket"]["id"])
        if not bucket:  # not exists
            return HttpResponseBadRequest(message)

        # process parent with type listed in static_get_vault_parent_types (same with upload parent)
        parent, message = db_get_vault_parent(parent=upload["parent"], bucket_id=upload["bucket"]["id"])
        if not parent:  # not exists
            return HttpResponseBadRequest(message)

        # process creator
        try:
            creator = BcPeople.objects.get(id=upload["creator"]["id"])
        except BcPeople.DoesNotExist:
            serializer = BcPeopleSerializer(data=upload["creator"])
            if serializer.is_valid():
                creator = serializer.save()
            else:  # invalid serializer
                return HttpResponseBadRequest(f'creator serializer error: {serializer.errors}')

        # remove 'bucket' key from document. key 'bucket' still used in processing parent
        upload.pop('bucket')

        # remove 'parent' key from document, will use model instance parent instead
        upload.pop('parent')

        # remove 'creator' key from document, will use model instance creator instead
        upload.pop('creator')

        # process document
        try:
            _upload = BcUpload.objects.get(id=upload["id"])
        except BcUpload.DoesNotExist:
            _upload = BcUpload.objects.create(bucket=bucket, parent=parent, creator=creator, **upload)
            _upload.save()

    else:
        return HttpResponseBadRequest(
            f'upload {upload["title"]} has no creator or bucket type Project or parent type in '
            f'{static_get_vault_parent_types()}')

    _upload_title = _upload.title if _upload else upload["title"]

    return HttpResponse(
        '<a href="' + reverse('app-project-detail', kwargs={'project_id': bucket_id}) + '">back</a><br/>'
        f'title: {_upload_title}<br/>'
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
