# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse

from .models import AldrynCloudUser


class AldrynCloudUserAdmin(admin.ModelAdmin):
    list_display = (
        'cloud_id',
        'linked_user',
    )
    search_fields = (
        'cloud_id',
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
    )
    raw_id_fields = (
        'user',
    )

    def get_queryset(self, request):
        return (
            super(AldrynCloudUserAdmin, self)
            .get_queryset(request)
            .select_related('user')
        )

    def linked_user(self, obj):
        return '<a href="{}">{}</a>'.format(
            reverse('admin:auth_user_change', args=[obj.pk]),
            obj.user,
        )
    linked_user.short_description = 'user'
    linked_user.allow_tags = True
    linked_user.admin_order_field = 'user'

if settings.ALDRYN_SSO_HIDE_USER_MANAGEMENT:
    admin.site.unregister(User)
    admin.site.unregister(Group)
else:
    admin.site.register(AldrynCloudUser, AldrynCloudUserAdmin)


original_admin_login_view = admin.site.login


@login_required
def admin_login_view(request, extra_context=None):
    # The login required decorator takes care of redirect not logged in users
    # to our custom login view.
    # It does not make sense to show the admin login form for users that are
    # logged in, but are not staff users (default behaviour of admin).
    # Instead show an message and explain the situation to the user.
    if not request.user.is_staff:
        context = dict()
        return TemplateResponse(
            request,
            'aldryn_sso/admin_non_staff.html',
            context,
        )
    return original_admin_login_view(request, extra_context=extra_context)


if settings.ALDRYN_SSO_OVERIDE_ADMIN_LOGIN_VIEW:
    # Force the default admin login view to use the default django login view.
    admin.site.login = admin_login_view
