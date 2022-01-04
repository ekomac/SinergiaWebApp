class EmptyPDFError(Exception):
    pass


class InvalidExcelFileError(Exception):
    pass


class InvalidPdfFileError(Exception):
    pass


class CantConvertNothingError(Exception):
    pass


class FileWithNoExtensionError(Exception):
    pass


class InvalidExtensionError(Exception):
    pass


class UnsupportedExtensionError(Exception):
    pass
