from typing import Any
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator 


class ProductParamDuplicateValidator(BaseValidator):

    message = "Product param with this key already exists."
    code = "duplicate"

    def __init__(self, *args, **kwargs):
        super().__init__(limit_value=1, *args, **kwargs)

    def compare(self, param: Any, limit: Any) -> bool:
        raise ValidationError("Not implemented")
        print(param, limit)
        count = param.product.params.filter(
            param__param_value__param__key=param.param_value.param.key
        ).count()
        return count >= limit
