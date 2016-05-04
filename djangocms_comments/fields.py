import django
from django import forms
from django.forms.fields import ChoiceField
from django.forms.utils import flatatt
from django.forms.widgets import CheckboxChoiceInput, ChoiceFieldRenderer, RadioChoiceInput, SubWidget, RendererMixin, \
    Select, CheckboxInput
from django.utils import html


from django.utils.encoding import python_2_unicode_compatible, force_text
if django.VERSION < (1, 7):
    from django.utils.html import html_safe
else:
    def html_safe(klass):
        return klass
from django.utils.html import format_html


class SubmitButtonWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return '<input type="submit" name="%s" value="%s">' % (html.escape(name), html.escape(value))


class SubmitButtonField(forms.Field):
    def __init__(self, *args, **kwargs):
        if not kwargs:
            kwargs = {}
        kwargs["widget"] = SubmitButtonWidget

        super(SubmitButtonField, self).__init__(*args, **kwargs)

    def clean(self, value):
        return value


class ButtonGroupRenderer(ChoiceFieldRenderer):
    outer_html = '<div class="btn-group" role="group">{content}</div>'
    inner_html = '{choice_value}{sub_widgets}'


@html_safe
@python_2_unicode_compatible
class ChoiceButton(SubWidget):
    input_type = None  # Subclasses must define this

    def __init__(self, name, value, attrs, choice, index):
        self.choice_value = force_text(choice[0])
        self.choice_label = force_text(choice[1])
        attrs = dict(attrs)
        enabled_class = attrs.pop('enabled_classes', {}).get(self.choice_value, 'btn-primary')
        disabled_class = attrs.pop('dissabled_classes', {}).get(self.choice_value, '')
        self.name = name
        self.value = value
        self.attrs = attrs
        self.index = index
        if 'id' in self.attrs:
            self.attrs['id'] += "_%d" % self.index
        self.attrs['type'] = self.attrs.get('type', 'submit')
        self.attrs['class'] = ' '.join(filter(lambda x: x, [self.attrs.get('class', 'btn'),
                                                            enabled_class if self.value == self.choice_value
                                                            else disabled_class]))

    def __str__(self):
        return self.render()

    def render(self, name=None, value=None, attrs=None, choices=()):
        if self.id_for_label:
            label_for = format_html(' for="{}"', self.id_for_label)
        else:
            label_for = ''
        return format_html(self.tag(attrs))

    def is_checked(self):
        return True

    def tag(self, attrs=None):
        attrs = attrs or self.attrs
        final_attrs = dict(attrs, name=self.name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return format_html('<button{}>{}</button>', flatatt(final_attrs), self.choice_label)

    @property
    def id_for_label(self):
        return self.attrs.get('id', '')


class MultipleSubmitButtonRendered(ButtonGroupRenderer):
    choice_input_class = ChoiceButton


class MultipleSubmitButton(RendererMixin, Select):
    renderer = MultipleSubmitButtonRendered
    _empty_value = ''


class Button(CheckboxInput):
    def __init__(self, attrs=None, check_test=None, values=None):
        self.values = values or ['True', 'False']
        super(Button, self).__init__(attrs, check_test)

    def render(self, name, value, attrs=None):
        attrs = dict(attrs or {})
        attrs.update(self.attrs)
        enabled_class = attrs.pop('enabled_class', 'btn-primary')
        disabled_class = attrs.pop('dissabled_class', '')
        attrs['class'] = ' '.join(filter(lambda x: x, [attrs.get('class', 'btn'),
                                                       enabled_class if value else disabled_class]))
        attrs['type'] = attrs.get('type', 'submit')
        final_attrs = self.build_attrs(attrs, name=name)
        return format_html('<button{}>{}</button>', flatatt(final_attrs), self.values[0 if not value else 1])
