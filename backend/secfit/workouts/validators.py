import os
import magic
from django.core.exceptions import ValidationError

def ImageValidator(file):
    valid_mime_types = ['image/jpeg','image/png', 'image/bmp', 'image/x-ms-bmp']
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    if file_mime_type not in valid_mime_types:
        raise ValidationError('Unsupported file type: ' + file_mime_type)
    valid_file_extensions = ['.jpg','.jpeg','.png','.bmp']
    ext = os.path.splitext(file.name)[1]
    if ext.lower() not in valid_file_extensions:
        raise ValidationError('Unacceptable file extension:' + ext)