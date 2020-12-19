from django.contrib import admin

from .models import MemoSet, MemoCard

@admin.register(MemoSet)
class MemoSetAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('id', 'parent', 'topic', 'owner', 'is_template',)
    list_display_links = ('topic',)
    list_filter = ('is_template',)
    list_editable = ('is_template',)
    autocomplete_fields = ['owner']
    readonly_fields = ['id', 'created_at', 'updated_at',]


@admin.register(MemoCard)
class MemoCardAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('id', 'memoset', 'topic', 'score', 'memoset__owner',)
    list_display_links = ('topic',)
    readonly_fields = ['id', 'created_at', 'updated_at',]
