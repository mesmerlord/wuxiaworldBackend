
from rest_framework_extensions.key_constructor.constructors import (
    KeyConstructor 
)
from rest_framework_extensions.key_constructor import bits

class DefaultKeyConstructor(KeyConstructor):
    unique_method_id = bits.UniqueMethodIdKeyBit()
    format = bits.FormatKeyBit()
    language = bits.LanguageKeyBit()
    all_query_params = bits.QueryParamsKeyBit()
    