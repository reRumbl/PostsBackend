from uuid import uuid4


def generate_object_name(file_path: str) -> str:
    extension = file_path.split('/')[-1].split('.')[-1]
    object_name = f'{uuid4().hex}.{extension}'
    return object_name
