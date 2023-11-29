from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from bc.models import BcPeople, BcProject


class BcVault(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/vaults.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Vault ID
    status = models.CharField(max_length=30)
    visible_to_clients = models.BooleanField()
    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()
    title = models.CharField(max_length=100)
    inherits_status = models.BooleanField()
    type = models.CharField(max_length=30)
    url = models.URLField()
    app_url = models.URLField()
    bookmark_url = models.URLField()
    position = models.IntegerField(null=True)
    # parent in ["Vault"], not available at the root vault of the project. set null & black at these two.
    parent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    parent_object_id = models.PositiveIntegerField(null=True, blank=True)
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    parent = GenericForeignKey("parent_content_type", "parent_object_id")
    bucket = models.ForeignKey(to=BcProject, on_delete=models.CASCADE)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)
    documents_count = models.IntegerField()
    documents_url = models.URLField()
    uploads_count = models.IntegerField()
    uploads_url = models.URLField()
    vaults_count = models.IntegerField()
    vaults_url = models.URLField()

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'


class BcDocument(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/documents.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Document ID
    status = models.CharField(max_length=30)
    visible_to_clients = models.BooleanField()
    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()
    title = models.CharField(max_length=100)
    inherits_status = models.BooleanField()
    type = models.CharField(max_length=30)
    url = models.URLField()
    app_url = models.URLField()
    bookmark_url = models.URLField()
    subscription_url = models.URLField()
    comments_count = models.IntegerField()
    comments_url = models.URLField()
    position = models.IntegerField(null=True)
    # parent in ["Vault"]
    parent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_object_id = models.PositiveIntegerField()
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    parent = GenericForeignKey("parent_content_type", "parent_object_id")
    bucket = models.ForeignKey(to=BcProject, on_delete=models.CASCADE)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'


class BcUpload(models.Model):
    """
    https://github.com/basecamp/bc3-api/blob/master/sections/uploads.md
    """
    id = models.BigIntegerField(primary_key=True)  # Basecamp Upload ID
    status = models.CharField(max_length=30)
    visible_to_clients = models.BooleanField()
    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()
    title = models.CharField(max_length=100)
    inherits_status = models.BooleanField()
    type = models.CharField(max_length=30)
    url = models.URLField()
    app_url = models.URLField()
    bookmark_url = models.URLField()
    subscription_url = models.URLField()
    comments_count = models.IntegerField()
    comments_url = models.URLField()
    position = models.IntegerField(null=True)
    # parent in ["Vault"]
    parent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_object_id = models.PositiveIntegerField()
    # https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/#generic-relations
    parent = GenericForeignKey("parent_content_type", "parent_object_id")
    bucket = models.ForeignKey(to=BcProject, on_delete=models.CASCADE)
    creator = models.ForeignKey(to=BcPeople, on_delete=models.CASCADE)
    description = models.CharField(max_length=100, null=True, blank=True)
    content_type = models.CharField(max_length=30)
    byte_size = models.BigIntegerField()
    filename = models.CharField(max_length=30)
    download_url = models.URLField()
    app_download_url = models.URLField()
    width = models.IntegerField()
    height = models.IntegerField()

    def __str__(self):
        return f'{self.type} {self.id} {self.title} ({self.status})'
