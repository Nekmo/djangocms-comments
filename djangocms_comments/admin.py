from django.contrib import admin

from .models import CommentsConfig, Comment


class CommentsConfigAdmin(admin.ModelAdmin):
    pass

admin.site.register(CommentsConfig, CommentsConfigAdmin)


class CommentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Comment, CommentAdmin)
