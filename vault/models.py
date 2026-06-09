from django.db import models
import uuid

class Secret(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='secrets')
    name = models.CharField(max_length=225)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('owner', 'name')


class SecretVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vault = models.ForeignKey(Secret, on_delete=models.CASCADE, related_name='versions')

    encrypted_value = models.CharField(max_length=225)
    version_number = models.PositiveBigIntegerField()

    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)


class SecretShare(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    secret = models.ForeignKey(Secret, on_delete=models.CASCADE, related_name='shares')
    shared_with = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='shared_secrets')

    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)
    shared_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  
