from django.db import models
import uuid


class Audit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    action = models.CharField(max_length=225)
    resource_type = models.CharField(max_length=225)
    resource_id = models.UUIDField()
    ip_address = models.GenericIPAddressField(null=True)
    meta_data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def delete(self, *args, **kwargs):
        raise PermissionError("Audit logs cannot be deleted")
    
    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError("Audit logs are immutable")
        super().save(*args, **kwargs)
