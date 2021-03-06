"""
This module defines a converter that uses :py:mod:`marshmallow` schemas
to deserialize and serialize values.
"""

# Standard library imports
import inspect

# Local imports
from uplink.converters import interfaces


class MarshmallowConverter(interfaces.ConverterFactory):
    """
    A converter that serializes and deserializes values using
    :py:mod:`marshmallow` schemas.

    To deserialize JSON responses into Python objects with this
    converter, define a :py:class:`marshmallow.Schema` subclass and set
    it as the return annotation of a consumer method:

    .. code-block:: python

        @get("/users")
        def get_users(self, username) -> UserSchema():
            '''Fetch a single user'''

    Also, when instantiating a consumer, be sure to set this class as
    a converter for the instance:

    .. code-block:: python

        github = GitHub(BASE_URL, converter=MarshmallowConverter())

    Note:

        This converter is an optional feature and requires the :py:mod:`marshmallow`
        package. For example, here's how to install this feature using pip::

            $ pip install uplink[marshmallow]
    """
    try:
        import marshmallow
    except ImportError:  # pragma: no cover
        marshmallow = None

    def __init__(self):
        if self.marshmallow is None:
            raise ImportError("No module named 'marshmallow'")

    class ResponseBodyConverter(interfaces.Converter):

        def __init__(self, schema):
            self._schema = schema

        def convert(self, response):
            return self._schema.load(response.json()).data

    class RequestBodyConverter(interfaces.Converter):
        def __init__(self, schema):
            self._schema = schema

        def convert(self, value):
            return self._schema.dump(value).data

    @classmethod
    def _get_schema(cls, type_):
        if inspect.isclass(type_) and issubclass(type_, cls.marshmallow.Schema):
            return type_()
        elif isinstance(type_, cls.marshmallow.Schema):
            return type_
        raise ValueError("Expected marshmallow.Scheme subclass or instance.")

    def _make_converter(self, converter_cls, type_):
        try:
            # Try to generate schema instance from the given type.
            schema = self._get_schema(type_)
        except ValueError:
            # Failure: the given type is not a `marshmallow.Schema`.
            return None
        else:
            return converter_cls(schema)

    def make_request_body_converter(self, type_, *args, **kwargs):
        """
        Constructs a :py:class:`uplink.converters.interfaces.Converter`
        subclass that serializes values using a
        :py:class:`marshmallow.Schema`.
        """
        return self._make_converter(self.RequestBodyConverter, type_)

    def make_response_body_converter(self, type_, *args, **kwargs):
        """
        Constructs a :py:class:`uplink.converters.interfaces.Converter`
        subclass that deserializes values using a
        :py:class:`marshmallow.Schema`.
        """
        return self._make_converter(self.ResponseBodyConverter, type_)

    def make_string_converter(self, type_, *args, **kwargs):
        return None
