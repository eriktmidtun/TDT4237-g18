"""
Mixins for the workouts application
"""


class CreateListModelMixin(object):
    """Mixin that allows to create multiple objects from lists.
    Taken from https://stackoverflow.com/a/48885641
    """

    def get_serializer(self, *args, **kwargs):
        """If an array is passed, set serializer to many.

        kwargs["many"] will be set to true if an array is passed. This argument
        is passed when retrieving the serializer.

        Args:
            *args: Variable length argument list passed to the serializer.
            **kwargs: Arbitrary keyword arguments passed to the serializer, including "many".

        Returns:
            [type]: [description]
        """
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(CreateListModelMixin, self).get_serializer(*args, **kwargs)
