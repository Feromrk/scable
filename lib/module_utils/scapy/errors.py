'''Raised when a serialization operation fails.'''
class SerializationError(RuntimeError):
    pass

'''Raised when a deserialization operation fails.'''
class DeserializationError(RuntimeError):
    pass