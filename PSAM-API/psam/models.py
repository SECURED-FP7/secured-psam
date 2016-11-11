from django.db import models

class PSA (models.Model):

	psa_id = models.CharField(primary_key=True,max_length=100)
	timestamp = models.DateTimeField(auto_now=True)
	hash_manifest = models.CharField(max_length=100)
	hash_plugin = models.CharField(max_length=100)
	hash_mspl = models.CharField(max_length=100)
	hash_image = models.CharField(max_length=100)

