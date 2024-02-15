from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse

from bc.models import BcVault, BcDocument, BcUpload
from bc.utils import (session_get_token_and_identity, bc_api_get,
                      db_get_bucket, db_get_vault_parent, db_get_or_create_person,
                      api_vault_get_bucket_vault_uri, api_vault_get_bucket_vault_vaults_uri,
                      api_vault_get_bucket_vault_documents_uri, api_document_get_bucket_document_uri,
                      api_vault_get_bucket_vault_uploads_uri, api_document_get_bucket_upload_uri,
                      static_get_vault_parent_types,
                      repr_http_response_template_string, repr_template_response_entity_creator_bucket_parent,
                      repr_template_response_entity_creator_bucket, repr_template_response_simple_with_back)


def app_vault_detail(request, bucket_id, vault_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get vault API
    api_vault_get_bucket_vault = api_vault_get_bucket_vault_uri(bucket_id=bucket_id, vault_id=vault_id)
    response = bc_api_get(uri=api_vault_get_bucket_vault, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    vault = response.json()

    if 'bucket' in vault and vault["bucket"]["type"] == "Project" and 'creator' in vault:

        # process bucket first, because at processing parent still need a valid bucket
        _bucket, _exception = db_get_bucket(bucket_id=vault["bucket"]["id"])
        if not _bucket:  # not exists
            return HttpResponseBadRequest(_exception)  # db_get_bucket implemented XSS protection

        if 'parent' in vault and vault["parent"]["type"] in static_get_vault_parent_types():
            # process parent with type listed in static_get_vault_parent_types
            _parent, _exception = db_get_vault_parent(parent=vault["parent"], bucket_id=vault["bucket"]["id"])
            if not _parent:  # not exists
                return HttpResponseBadRequest(_exception)

            # remove 'parent' key from vault, will use model instance parent instead
            vault.pop('parent')

        else:  # no parent, as root vault has no parent
            _parent = None

        # process creator
        _creator, _exception = db_get_or_create_person(person=vault["creator"])
        if not _creator:  # create person error
            return HttpResponseBadRequest(_exception)

        # remove 'bucket' key from vault. key 'bucket' still used in processing parent
        vault.pop('bucket')

        # remove 'creator' key from vault, will use model instance creator instead
        vault.pop('creator')

        # process vault
        try:
            _vault = BcVault.objects.get(id=vault["id"])
        except BcVault.DoesNotExist:
            _vault = BcVault.objects.create(bucket=_bucket, parent=_parent, creator=_creator, **vault)
            _vault.save()

    else:
        _exception = repr_template_response_entity_creator_bucket(entity_type=vault["type"],
                                                                  entity_title=vault["title"])
        return HttpResponseBadRequest(_exception)

    _vault_title = _vault.title if _vault else vault["title"]

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-project-detail', kwargs={'project_id': bucket_id}),
        body=f'title: {_vault_title}<br/>'
             f'<a href="' + reverse('app-vault-documents',
                                    kwargs={'bucket_id': bucket_id, 'vault_id': vault_id}) +
             f'">{vault["documents_count"]} documents</a><br/>'
             f'<a href="' + reverse('app-vault-uploads', kwargs={'bucket_id': bucket_id, 'vault_id': vault_id}) +
             f'">{vault["uploads_count"]} uploads</a><br/>'
             f'<a href="' + reverse('app-vault-vaults',
                                    kwargs={'bucket_id': bucket_id, 'vault_id': vault["id"]}) +
             f'">{vault["vaults_count"]} vaults</a>'
    )
    return HttpResponse(_response)


def app_vault_vaults(request, bucket_id, vault_id):
    token, identity = session_get_token_and_identity(request)
    if not (token and identity):  # no token or identity, redirect to auth
        return HttpResponseRedirect(reverse('bc-auth'))

    # request to get vault vaults API
    api_vault_get_bucket_vault_vaults = api_vault_get_bucket_vault_vaults_uri(bucket_id=bucket_id, vault_id=vault_id)
    response = bc_api_get(uri=api_vault_get_bucket_vault_vaults, access_token=token["access_token"])

    if response.status_code != 200:  # not OK
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    data = response.json()

    count = 0
    vault_list = ""
    for vault in data:

        vault_list += (f'<li><a href="' + reverse('app-vault-detail',
                                                  kwargs={'bucket_id': bucket_id, 'vault_id': vault["id"]}) +
                       f'">{vault["id"]}</a> {vault["title"]} '
                       f'{vault["documents_count"]} documents '
                       f'{vault["uploads_count"]} uploads '
                       f'{vault["vaults_count"]} vaults'
                       '</li>')

        count += 1

    # if 'next' in response.links and 'url' in response.links["next"]:
    #     print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} vaults'

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-vault-detail', kwargs={'bucket_id': bucket_id, 'vault_id': vault_id}),
        body=f'{total_count_str}<br/>{vault_list}')
    return HttpResponse(_response)


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
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    document = response.json()

    # parent of document same with parent of vault: Vault
    if ('parent' in document and document["parent"]["type"] in static_get_vault_parent_types() and
            'bucket' in document and document["bucket"]["type"] == "Project" and 'creator' in document):

        # process bucket first, because at processing parent still need a valid bucket
        _bucket, _exception = db_get_bucket(bucket_id=document["bucket"]["id"])
        if not _bucket:  # not exists
            return HttpResponseBadRequest(_exception)  # db_get_bucket implemented XSS protection

        # process parent with type listed in static_get_vault_parent_types (same with document parent)
        _parent, _exception = db_get_vault_parent(parent=document["parent"], bucket_id=document["bucket"]["id"])
        if not _parent:  # not exists
            return HttpResponseBadRequest(_exception)

        # process creator
        _creator, _exception = db_get_or_create_person(person=document["creator"])
        if not _creator:  # create person error
            return HttpResponseBadRequest(_exception)

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
            _document = BcDocument.objects.create(bucket=_bucket, parent=_parent, creator=_creator, **document)
            _document.save()

    else:
        _exception = repr_template_response_entity_creator_bucket_parent(
            entity_type=document["type"], entity_title=document["title"],
            list_parent_types=static_get_vault_parent_types())
        return HttpResponseBadRequest(_exception)

    _document_title = _document.title if _document else document["title"]

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-project-detail', kwargs={'project_id': bucket_id}),
        body=f'title: {_document_title}')
    return HttpResponse(_response)


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
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    data = response.json()

    count = 0
    document_list = ""
    for document in data:

        document_list += (f'<li><a href="' + reverse('app-document-detail',
                                                     kwargs={'bucket_id': bucket_id, 'document_id': document["id"]}) +
                          f'">{document["id"]}</a> {document["title"]} '
                          '</li>')

        count += 1

    # if 'next' in response.links and 'url' in response.links["next"]:
    #     print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} documents'

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-vault-detail', kwargs={'bucket_id': bucket_id, 'vault_id': vault_id}),
        body=f'{total_count_str}<br/>{document_list}')
    return HttpResponse(_response)


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
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    upload = response.json()

    # parent of upload same with parent of vault: Vault
    if ('parent' in upload and upload["parent"]["type"] in static_get_vault_parent_types() and
            'bucket' in upload and upload["bucket"]["type"] == "Project" and 'creator' in upload):

        # process bucket first, because at processing parent still need a valid bucket
        _bucket, _exception = db_get_bucket(bucket_id=upload["bucket"]["id"])
        if not _bucket:  # not exists
            return HttpResponseBadRequest(_exception)  # db_get_bucket implemented XSS protection

        # process parent with type listed in static_get_vault_parent_types (same with upload parent)
        _parent, _exception = db_get_vault_parent(parent=upload["parent"], bucket_id=upload["bucket"]["id"])
        if not _parent:  # not exists
            return HttpResponseBadRequest(_exception)

        # process creator
        _creator, _exception = db_get_or_create_person(person=upload["creator"])
        if not _creator:  # create person error
            return HttpResponseBadRequest(_exception)

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
            _upload = BcUpload.objects.create(bucket=_bucket, parent=_parent, creator=_creator, **upload)
            _upload.save()

    else:
        _exception = repr_template_response_entity_creator_bucket_parent(
            entity_type=upload["type"], entity_title=upload["title"],
            list_parent_types=static_get_vault_parent_types())
        return HttpResponseBadRequest(_exception)

    _upload_title = _upload.title if _upload else upload["title"]

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-project-detail', kwargs={'project_id': bucket_id}),
        body=f'title: {_upload_title}')
    return HttpResponse(_response)


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
        return HttpResponse(repr_http_response_template_string(''), status=response.status_code)

    # if OK
    data = response.json()

    count = 0
    upload_list = ""
    for upload in data:

        upload_list += (f'<li><a href="' + reverse('app-upload-detail',
                                                   kwargs={'bucket_id': bucket_id, 'upload_id': upload["id"]}) +
                        f'">{upload["id"]}</a> {upload["title"]} '
                        '</li>')

        count += 1

    # if 'next' in response.links and 'url' in response.links["next"]:
    #     print(response.links["next"]["url"])

    total_count_str = ''
    if "X-Total-Count" in response.headers:
        total_count = int(response.headers["X-Total-Count"])
        total_count_str = f'shows {count}/{total_count} uploads'

    _response = repr_template_response_simple_with_back(
        back_href=reverse('app-vault-detail', kwargs={'bucket_id': bucket_id, 'vault_id': vault_id}),
        body=f'{total_count_str}<br/>{upload_list}')
    return HttpResponse(_response)
