import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import Depends, File, HTTPException, UploadFile

from src.connection.schemas import SQLiteUpload

SQLITE_EXTENSIONS = {".db", ".db3", ".sqlite", ".sqlite3"}
SQLITE_HEADER = b"SQLite format 3\x00"
MAX_SQLITE_BYTES = 50 * 1024 * 1024  # ~52 MB


async def process_sqlite_upload(file: UploadFile = File(...)) -> SQLiteUpload:
    """Validates an uploaded SQLite file and saves it to a temporary file.

    The file is checked by extension, header and size. The caller owns the
    temporary file and must delete it when finished.

    Args:
        file: The uploaded file.

    Returns:
        The temporary file's path and the original file name without its extension.

    Raises:
        400: If the extension is unsupported or the content is
            not a SQLite database
        413: If the file exceeds `MAX_SQLITE_BYTES`.
    """
    file_name = file.filename or "database.sqlite"
    suffix = Path(file_name).suffix.lower()
    if suffix not in SQLITE_EXTENSIONS:
        raise HTTPException(400, "Unsupported SQLite file extension.")

    header = await file.read(len(SQLITE_HEADER))
    if header != SQLITE_HEADER:
        raise HTTPException(400, "Not a valid SQLite database file.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(header)
            size = len(header)
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_SQLITE_BYTES:
                    raise HTTPException(413, "SQLite file is too large.")
                temp_file.write(chunk)
    except BaseException:
        if temp_path:
            temp_path.unlink(missing_ok=True)
        raise

    return SQLiteUpload(
        file_path=str(temp_path),
        file_name=Path(file_name).stem,  # Remove file extension
    )


SQLiteDBFile = Annotated[SQLiteUpload, Depends(process_sqlite_upload)]
