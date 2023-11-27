from django.conf import settings
from django.urls import (
    include,
    path
)
from django.contrib import admin


from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from django.conf.urls.i18n import i18n_patterns

from search import views as search_views

from setup import views as setup_views


handler404 = 'wagtail_store.views.my_custom_page_not_found_view'

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path('store-app/', include('store.urls')),
    path('setup/', include('setup.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + i18n_patterns(
    path('search/', search_views.search, name='search'),
    path("", include(wagtail_urls)),
)
