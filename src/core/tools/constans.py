CODESNIPPETS_DIR = Path(__file__).parent / "codesnippets"
SUPPORTED_CODE_LANGUAGES = ["python", "c++", "lisp"]  # add java/rust/go as files land
DEFAULT_CODE_LANGUAGE = "python"

CODE_LANGUAGE_LABELS = {"python": "Python", "c++": "C++", "lisp": "Lisp"}
# languages an pl will be taked reading folders and cleaning pl = listdir(codesnippets) and langauges = listdir(LANGUAGES)
