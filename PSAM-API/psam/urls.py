from django.conf.urls import include, url
from django.contrib import admin
from psam import views
urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	url(r'^v1/psam/images/$', views.PsamImages.as_view(), name='Psa list'),
	url(r'^v1/psam/images/(?P<psa_id>[^/]+)/$',views.PsamView.as_view(), name= 'PSA view'),
	url(r'^v1/psam/status/$', views.v1Status.as_view(), name='status'),
	url(r'^docs/', include('rest_framework_swagger.urls')),	 	
]
