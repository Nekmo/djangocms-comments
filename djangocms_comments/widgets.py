from django.core.exceptions import SuspiciousOperation
from django.core.signing import Signer, BadSignature
from django.forms import HiddenInput

signer = Signer()


class SignedHiddenInput(HiddenInput):
    def __init__(self, include_field_name=True, attrs=None):
        self.include_field_name = include_field_name
        super(SignedHiddenInput, self).__init__(attrs=attrs)

    def value_from_datadict(self, data, files, name):
        value = super(SignedHiddenInput, self).value_from_datadict(data, files, name)
        try:
            value = signer.unsign(value)
        except BadSignature:
            raise SuspiciousOperation()
        if self.include_field_name:
            name_key = '{0}-'.format(name)
            if not value.startswith(name_key):
                raise SuspiciousOperation()
            value = value.replace(name_key, '', 1)
        return value

    def render(self, name, value, attrs=None):
        value = self.sign_value(name, value)
        return super(SignedHiddenInput, self).render(name, value, attrs=attrs)

    def sign_value(self, name, value):
        if self.include_field_name:
            value = '-'.join(map(str, [name, value]))
        value = signer.sign(value)
        return value

    def value(self):
        pass