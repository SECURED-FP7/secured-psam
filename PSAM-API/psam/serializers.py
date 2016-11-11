from django.forms import widgets
from rest_framework import serializers
from models import PSA


class PSASerializer (serializers.ModelSerializer):
	class Meta:
		model=PSA
		fields = ('psa_id','timestamp','hash_manifest','hash_plugin','hash_mspl','hash_image')


