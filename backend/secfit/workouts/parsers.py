"""Contains custom parsers for serializers from the workouts Django app
"""
import json
from rest_framework import parsers

# Thanks to https://stackoverflow.com/a/50514630
class MultipartJsonParser(parsers.MultiPartParser):
    """Parser for serializing multipart data containing both files and JSON.

    This is currently unused.
    """

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(
            stream, media_type=media_type, parser_context=parser_context
        )
        data = {}
        new_files = {"files": []}

        # for case1 with nested serializers
        # parse each field with json
        for key, value in result.data.items():
            if not isinstance(value, str):
                data[key] = value
                continue
            if "{" in value or "[" in value:
                try:
                    data[key] = json.loads(value)
                except ValueError:
                    data[key] = value
            else:
                data[key] = value

        files = result.files.getlist("files")
        for file in files:
            new_files["files"].append({"file": file})

        return parsers.DataAndFiles(data, new_files)
