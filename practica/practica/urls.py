from django.conf.urls import include, url
from django.contrib import admin
import settings

urlpatterns = [
    # Examples:
    # url(r'^$', 'practica.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^archivos/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_URL}),
    url(r'^logout/(.+)$', "app.views.logout_view"),
    url(r'^add/(.+)$', "app.views.add"),
    url(r'^eliminar/(.+)/(.+)$', "app.views.eliminar"),
    url(r'^(.+)$', "app.views.usuario"),
    url(r'^$', "app.views.general"),
]
