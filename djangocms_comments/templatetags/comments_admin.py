from django.template.loader_tags import register


@register.inclusion_tag('djangocms_comments/admin_submit_line.html', takes_context=True)
def submit_row(context):
    """
    Displays the row of buttons for delete and save.
    """
    from django.contrib.admin.templatetags.admin_modify import submit_row
    row = submit_row(context)
    row['is_soft_deleted'] = context['original'].moderated == 'deleted'
    return row

