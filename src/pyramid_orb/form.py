import logging

from webhelpers.html import tags
from webhelpers.html.builder import HTML
from pyramid.renderers import render

log = logging.getLogger(__name__)


class OrbForm(object):
    def __init__(self, request, record, **kwds):
        self._record = record
        self._errors = kwds.get('errors', {})
        self._prefix = kwds.get('prefix', '')
        self._method = kwds.get('method', 'POST')
        self._multipart = kwds.get('multipart', False)
        self._request = request
        self._validated = False

    def _id(self, id, name):
        if id is not None:
            return id
        elif self._prefix:
            return self._prefix + name
        else:
            return name

    def begin(self, url=None, **attrs):
        attrs.setdefault('multipart', self.multipart())
        attrs.setdefault('method', self.method())
        return tags.form(url, **attrs)

    def commit(self, params=None):
        if not params:
            params = self.submittedValues()

        self.record().setRecordValues(**params)
        return self.record().commit()

    def checkbox(self, name, value="1", checked=False, label=None, id=None, **attrs):
        return tags.checkbox(name,
                             value,
                             self.value(name),
                             label,
                             self._id(id, name),
                             **attrs)

    def error(self, key=''):
        return self._errors.get(key)

    def errors(self):
        return self._errors

    def isErrored(self, name=None):
        if name is None:
            return bool(self._errors)
        return name in self._errors

    def end(self):
        return tags.end_form()

    def file(self, name, value=None, id=None, **attrs):
        return tags.file(name,
                         self.value(name, value),
                         self._id(id, name),
                         **attrs)

    def hidden(self, name, value=None, id=None, **attrs):
        if value is None:
            value = self.value(name)

        return tags.hidden(name,
                           value,
                           self._id(id, name),
                           **attrs)

    def label(self, name, label=None, **attrs):
        if 'for_' not in attrs:
            attrs['for_'] = self._id(None, name.lower())

        column = self.record().schema().column(name)
        label = label or column.displayName()
        return HTML.tag('label', label, **attrs)

    def method(self):
        return self._method

    def multipart(self):
        return self._multipart

    def password(self, name, value=None, id=None, **attrs):
        return tags.password(name,
                             self.value(name, value),
                             self._id(id, name),
                             **attrs)

    def radio(self, name, value=None, checked=False, id=None, **attrs):
        checked = self.value(name) == value or checked
        return tags.radio(name, value, checked, label, **attrs)

    def record(self):
        return self._record

    def render(self, template, **kwds):
        kwds.setdefault('form', self)
        return render(template, kwds, self._request)

    def submittedValues(self):
        if hasattr(self._request, 'json_body') and self._request.json_body:
            params = self._request.json_body
        elif self.method() == 'POST':
            params = self._request.POST
        else:
            params = self._request.params

        return params

    def select(self, name, options, selected=None, id=None, **attrs):
        return tags.select(name,
                           self.value(name, selected),
                           options,
                           self._id(id, name),
                           **attrs)

    def setError(self, error, key=''):
        self._errors[key] = error

    def submit(self, name='submit', value=None, id=None, **attrs):
        return tags.submit(name,
                           value,
                           self._id(id, name),
                           **attrs)

    def text(self, name, value=None, id=None, **attrs):
        return tags.text(name,
                         self.value(name, value),
                         self._id(id, name),
                         **attrs)

    def textarea(self, name, content='', id=None, **attrs):
        return tags.textarea(name,
                             self.value(name, content),
                             self._id(id, name),
                             **attrs)

    def value(self, name, default=None):
        return self._record.recordValue(name, default=default)

    def validate(self, force=False, params=None):
        if self._validated:
            return not self.errors()

        if not force:
            if self.method() and self.method() != self._request.method:
                log.error('Invalid form submission, mismatched methods.')
                return False

        if params is None:
            params = self.submittedValues()

        _, errors = self.record().validateValues(params, validateColumns=False, returnErrors=True)
        self._errors.update(errors)
        self._validated = True
        return not self._errors

