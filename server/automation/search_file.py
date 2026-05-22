import subprocess
import string
import os


def _get_all_drives() -> list[str]:
    """Returns a list of all available drive letters (e.g., ['C:', 'D:'])."""
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(f"{letter}:")
    return drives


def _run_search(command: str) -> list[str]:
    """Run a shell command and return non-empty output lines."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        lines = result.stdout.strip().splitlines()
        return [line.strip() for line in lines if line.strip()]
    except subprocess.TimeoutExpired:
        return ["Error: Search timed out after 120 seconds."]
    except Exception as e:
        return [f"Error: {e}"]


# ──────────────────────────────────────────────
#  FILE SEARCH FUNCTIONS
# ──────────────────────────────────────────────

def search_file_in_system(name: str, folder: str = None, drive: str = None) -> list[str]:
    """Search for a file by name across ALL drives."""
    if folder:
        folder = folder.rstrip("\\")
        return _run_search(f'where /R "{folder}" "{name}" 2>nul')
    if drive:
        drive = drive.rstrip("\\")
        return _run_search(f'where /R {drive}\\ "{name}" 2>nul')
    results = []
    for drive in _get_all_drives():
        results.extend(
            _run_search(f'where /R {drive}\\ "{name}" 2>nul')
        )
    return results


def search_file_by_extension(extension: str, folder: str = None, drive: str = None) -> list[str]:
    """Search for files with a given extension.

    If folder is provided, searches inside that folder.
    Otherwise searches the entire system.
    """
    ext = extension if extension.startswith(".") else f".{extension}"
    pattern = f"*{ext}"

    if folder:
        folder = folder.rstrip("\\")
        return _run_search(f'where /R "{folder}" "{pattern}" 2>nul')

    if drive:
        drive = drive.rstrip("\\")
        return _run_search(f'where /R {drive}\\ "{pattern}" 2>nul')

    results = []
    for drive in _get_all_drives():
        results.extend(
            _run_search(f'where /R {drive}\\ "{pattern}" 2>nul')
        )
    return results


def search_file_by_keyword(keyword: str, folder: str = None, drive: str = None) -> list[str]:
    """Search for files whose name contains the given keyword.

    Uses `dir /S /B` with a wildcard pattern.
    """
    pattern = f"*{keyword}*"
    if folder:
        folder = folder.rstrip("\\")
        return _run_search(f'dir /S /B "{folder}\\{pattern}" 2>nul')

    if drive:
        drive = drive.rstrip("\\")
        return _run_search(f'dir /S /B {drive}\\{pattern} 2>nul')

    results = []
    for drive in _get_all_drives():
        results.extend(
            _run_search(f'dir /S /B {drive}\\{pattern} 2>nul')
        )
    return results


def search_file_by_size(min_bytes: int = 0, max_bytes: int = None, folder: str = None) -> list[str]:
    """Search for files within a size range (in bytes).

    Uses PowerShell to filter by file size.
    """
    target = f'"{folder}"' if folder else '"$env:SystemDrive\\"'
    size_filter = f"$_.Length -ge {min_bytes}"
    if max_bytes is not None:
        size_filter += f" -and $_.Length -le {max_bytes}"

    if folder:
        ps_cmd = (
            f'Get-ChildItem -Path {target} -Recurse -File -ErrorAction SilentlyContinue '
            f'| Where-Object {{ {size_filter} }} '
            f'| Select-Object -ExpandProperty FullName'
        )
    else:
        ps_cmd = (
            f'Get-PSDrive -PSProvider FileSystem | ForEach-Object {{ '
            f'Get-ChildItem -Path $_.Root -Recurse -File -ErrorAction SilentlyContinue '
            f'| Where-Object {{ {size_filter} }} '
            f'| Select-Object -ExpandProperty FullName }}'
        )
    return _run_search(f'powershell -Command "{ps_cmd}"')


def search_file_modified_by_date(folder: str = None, date: str = "today") -> list[str]:
    """Search for files modified today."""
    target = f'"{folder}"' if folder else '"$env:SystemDrive\\"'

    if date == "today":
        date = '(Get-Date).Date'
    else:
        date = f'"(Get-Date -Date "{date}").Date"'

    if folder:
        ps_cmd = (
            f'Get-ChildItem -Path {target} -Recurse -File -ErrorAction SilentlyContinue '
            f'| Where-Object {{ $_.LastWriteTime.Date -eq {date} }} '
            f'| Select-Object -ExpandProperty FullName'
        )
    else:
        ps_cmd = (
            f'Get-PSDrive -PSProvider FileSystem | ForEach-Object {{ '
            f'Get-ChildItem -Path $_.Root -Recurse -File -ErrorAction SilentlyContinue '
            f'| Where-Object {{ $_.LastWriteTime.Date -eq {date} }} '
            f'| Select-Object -ExpandProperty FullName }}'
        )
    return _run_search(f'powershell -Command "{ps_cmd}"')


def search_file_by_date_range(start_date: str, end_date: str, folder: str = None) -> list[str]:
    """Search for files modified between two dates (format: YYYY-MM-DD)."""
    target = f'"{folder}"' if folder else '"$env:SystemDrive\\"'

    if folder:
        ps_cmd = (
            f'Get-ChildItem -Path {target} -Recurse -File -ErrorAction SilentlyContinue '
            f'| Where-Object {{ $_.LastWriteTime -ge "{start_date}" -and $_.LastWriteTime -le "{end_date}" }} '
            f'| Select-Object -ExpandProperty FullName'
        )
    else:
        ps_cmd = (
            f'Get-PSDrive -PSProvider FileSystem | ForEach-Object {{ '
            f'Get-ChildItem -Path $_.Root -Recurse -File -ErrorAction SilentlyContinue '
            f'| Where-Object {{ $_.LastWriteTime -ge "{start_date}" -and $_.LastWriteTime -le "{end_date}" }} '
            f'| Select-Object -ExpandProperty FullName }}'
        )
    return _run_search(f'powershell -Command "{ps_cmd}"')


# ──────────────────────────────────────────────
#  FOLDER SEARCH FUNCTIONS
# ──────────────────────────────────────────────

def search_folder_in_system(name: str, folder: str = None, drive:str = None) -> list[str]:
    """Search for a folder by name across ALL drives."""
    if folder:
        folder = folder.rstrip("\\")
        return _run_search(
        f'dir /S /B /AD "{folder}" 2>nul | findstr /I /E "\\\\{name}"'
        )

    if drive:
        drive = drive.rstrip("\\")
        return _run_search(
            f'dir /S /B /AD {drive}\\ 2>nul | findstr /I /E "\\\\{name}"'
        )

    results = []
    for drive in _get_all_drives():
        results.extend(
            _run_search(
                f'dir /S /B /AD {drive}\\  2>nul | findstr /I /E "\\\\{name}"'
            )
        )
    return results


def search_folder_by_keyword(keyword: str, folder: str = None, drive: str = None) -> list[str]:
    """Search for folders whose name contains the given keyword."""
    if folder:
        folder = folder.rstrip("\\")
        return _run_search(
            f'dir /S /B /AD "{folder}" 2>nul | findstr /I "\\\\[^\\\\]*{keyword}[^\\\\]*$"'
        )

    if drive:
        drive = drive.rstrip("\\")
        return _run_search(
                f'dir /S /B /AD {drive}\\ 2>nul | findstr /I "\\\\[^\\\\]*{keyword}[^\\\\]*$"'
            )

    results = []
    for drive in _get_all_drives():
        results.extend(
            _run_search(
                f'dir /S /B /AD {drive}\\ 2>nul | findstr /I "\\\\[^\\\\]*{keyword}[^\\\\]*$"'
            )
        )
    return results


def search_empty_folders(folder: str = None) -> list[str]:
    """Search for empty folders."""
    if folder:
        target = f'"{folder}"'
    else:
        target = '"$env:SystemDrive\\"'

    if folder:
        ps_cmd = (
            f'Get-ChildItem -Path {target} -Recurse -Directory -ErrorAction SilentlyContinue '
            f'| Where-Object {{ (Get-ChildItem -Path $_.FullName -Force -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0 }} '
            f'| Select-Object -ExpandProperty FullName'
        )
    else:
        ps_cmd = (
            f'Get-PSDrive -PSProvider FileSystem | ForEach-Object {{ '
            f'Get-ChildItem -Path $_.Root -Recurse -Directory -ErrorAction SilentlyContinue '
            f'| Where-Object {{ (Get-ChildItem -Path $_.FullName -Force -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0 }} '
            f'| Select-Object -ExpandProperty FullName }}'
        )
    return _run_search(f'powershell -Command "{ps_cmd}"')


def search_folder_modified_today(folder: str = None) -> list[str]:
    """Search for folders modified today."""
    if folder:
        target = f'"{folder}"'
    else:
        target = '"$env:SystemDrive\\"'

    if folder:
        ps_cmd = (
            f'Get-ChildItem -Path {target} -Recurse -Directory -ErrorAction SilentlyContinue '
            f'| Where-Object {{ $_.LastWriteTime.Date -eq (Get-Date).Date }} '
            f'| Select-Object -ExpandProperty FullName'
        )
    else:
        ps_cmd = (
            f'Get-PSDrive -PSProvider FileSystem | ForEach-Object {{ '
            f'Get-ChildItem -Path $_.Root -Recurse -Directory -ErrorAction SilentlyContinue '
            f'| Where-Object {{ $_.LastWriteTime.Date -eq (Get-Date).Date }} '
            f'| Select-Object -ExpandProperty FullName }}'
        )
    return _run_search(f'powershell -Command "{ps_cmd}"')


def search_folder_by_date_range(start_date: str, end_date: str, folder: str = None) -> list[str]:
    """Search for folders modified between two dates (format: YYYY-MM-DD)."""
    if folder:
        target = f'"{folder}"'
    else:
        target = '"$env:SystemDrive\\"'

    if folder:
        ps_cmd = (
            f'Get-ChildItem -Path {target} -Recurse -Directory -ErrorAction SilentlyContinue '
            f'| Where-Object {{ $_.LastWriteTime -ge "{start_date}" -and $_.LastWriteTime -le "{end_date}" }} '
            f'| Select-Object -ExpandProperty FullName'
        )
    else:
        ps_cmd = (
            f'Get-PSDrive -PSProvider FileSystem | ForEach-Object {{ '
            f'Get-ChildItem -Path $_.Root -Recurse -Directory -ErrorAction SilentlyContinue '
            f'| Where-Object {{ $_.LastWriteTime -ge "{start_date}" -and $_.LastWriteTime -le "{end_date}" }} '
            f'| Select-Object -ExpandProperty FullName }}'
        )
    return _run_search(f'powershell -Command "{ps_cmd}"')



# search_file_and_folders = {
#     'search_file_by_name': search_file_in_system,
#     'search_file_by_extension': search_file_by_extension,
#     'search_file_by_keyword': search_file_by_keyword,
#     'search_file_by_size': search_file_by_size,
#     'search_file_modified_by_date': search_file_modified_by_date,
#     'search_file_by_date_range': search_file_by_date_range,
#     'search_folder_by_name': search_folder_in_system,
#     'search_folder_by_keyword': search_folder_by_keyword,
#     'search_folder_modified_today': search_folder_modified_today,
#     'search_folder_by_date_range': search_folder_by_date_range,
#     'search_empty_folders': search_empty_folders
# }

