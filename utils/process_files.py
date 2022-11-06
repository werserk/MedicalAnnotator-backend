import zipfile

def process_uploaded_zip(zip):
    original_zip = zipfile.ZipFile(zip, 'r')
    new_zip = zipfile.ZipFile(zip.name, 'w')
    for item in original_zip.infolist():
        buffer = original_zip.read(item.filename)
        if not str(item.filename).startswith('__MACOSX/'):
            new_zip.writestr(item, buffer)
    original_zip.close()

    return new_zip, buffer