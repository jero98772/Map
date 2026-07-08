from core.tools.tools import read_folders, read_json_files

PROGRAMING_LANGUAGES_FOLDER = "core/codesnippets/"
LANGUAGES_FOLDER = "core/content/"
SUPPORTED_PROGRAMING_LANGUAGES = read_folders(PROGRAMING_LANGUAGES_FOLDER)
SUPPORTED_LANGUAGES = read_json_files(LANGUAGES_FOLDER)
DEFAULT_PROGRAMING_LANGUAGE = "python"
DEFAULT_LANGUAGE = "en"
