from django.urls import reverse
from bc.models import BcProject


def db_get_bucket(bucket_id):
    try:
        bucket = BcProject.objects.get(id=bucket_id)
        message = None
    except BcProject.DoesNotExist:
        bucket = None
        message = (f'bucket {bucket_id} not found<br/>'
                   f'<a href="' + reverse('app-project-detail-update-db',
                                          kwargs={'project_id': bucket_id}) +
                   '">save project to db</a> first.')

    return bucket, message
