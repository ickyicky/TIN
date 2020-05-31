import re

from ..server.handler.HTTPExceptions import HTTPException
from ..server.response import Statuses


class ValidationError(Exception):
    pass


class BaseSerializer:
    validated_type = lambda x: x

    def __init__(self, required=False, unique=False, method=None):
        self.required = required
        self.unique = unique
        self.method = method

    def validate(self, value=None, request=None, model=None, field=None):
        if value is None and self.required:
            raise ValidationError("This field is required")
        elif value is None:
            return value

        try:
            result = self.validated_type(value)

            if self.method:
                result = self.method(result)

            if self.unique:
                assert (
                    request.dbssn.query(model).filter_by(**{field: result}).first()
                    is None
                )

            return result
        except:
            raise ValidationError("Invalid value")

    def parse(self, value=None):
        return value


class ModelSerializer:
    class Meta:
        fields = tuple()
        model = None

    @classmethod
    def additional_modifications(cls, data, request, obj):
        pass

    @classmethod
    def validate(cls, data, request=None):
        result = data

        for field in cls.Meta.fields:
            validator = getattr(cls, field)

            try:
                validated = validator.validate(
                    value=data.get(field),
                    request=request,
                    model=cls.Meta.model,
                    field=field,
                )
            except ValidationError as e:
                raise HTTPException(
                    status=Statuses.BAD_REQUEST,
                    message=f"Validation for field {field} failed: {e.args[0]}",
                )

            result[field] = validated

        return result

    @classmethod
    def parse(cls, obj):
        result = {}

        for field in cls.Meta.fields:
            validator = getattr(cls, field)
            value = getattr(obj, field)
            result[field] = validator.parse(value)

        return result

    @classmethod
    def create(cls, data, request):
        data = cls.validate(data, request)

        obj = cls.Meta.model()
        for k, v in data.items():
            if v is not None:
                setattr(obj, k, v)

        cls.additional_modifications(data, request, obj)

        request.dbssn.add(obj)
        request.dbssn.commit()
        return obj

    @classmethod
    def modify(cls, data, request, pk="id"):
        data = cls.validate(data, request)
        obj = request.dbssn.query(cls.Meta.model).filter_by(**{pk: data[pk]}).first()

        if obj is None:
            raise HTTPException(status=Statuses.NOT_FOUND, message="Not found")

        for k, v in data.items():
            if v is not None:
                setattr(obj, k, v)

        cls.additional_modifications(data, request, obj)

        request.dbssn.commit()
        return obj


class StringSerializer(BaseSerializer):
    validated_type = str

    def __init__(self, min_length=None, max_length=None, regex=None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.regex = regex

    def validate(self, value=None, request=None, model=None, field=None):
        value = super().validate(value, request, model, field)

        if value is None:
            return value

        if self.min_length and len(value) < self.min_length:
            raise ValidationError(f"Value should be at least {self.min_length} long")

        if self.max_length and len(value) > self.max_length:
            raise ValidationError(f"Value should be shorten tan {self.max_length}")

        if self.regex and not re.match(self.regex, value):
            raise ValidationError(f"Value should follow pattern: {self.regex}")

        return value


class IntegerSerializer(BaseSerializer):
    validated_type = int

    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value=None, request=None, model=None, field=None):
        value = super().validate(value, request, model, field)

        if value is None:
            return value

        if self.min_value and value < self.min_value:
            raise ValidationError(f"Value should be greater than {self.min_value}")

        if self.max_value and value > self.max_value:
            raise ValidationError(f"Value should be lesser than {self.max_value}")

        return value
