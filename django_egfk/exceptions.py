class EnhancedGenericForeignKeyException(Exception):
    pass


class GenericForeignKeyDetected(AttributeError, EnhancedGenericForeignKeyException):
    pass


class PropertyIsImutable(AttributeError):
    def __init__(self):
        super(PropertyIsImutable, self).__init__(
            "content_type you provided does not match the content_type property")
