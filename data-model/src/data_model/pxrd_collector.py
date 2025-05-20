import os
from typing import List
from .use_case_specific.pxrd_collector_mocof1 import process_pxrd_file_use_case_specific


class PXRDFile:

    def __init__(self, path: str):
        """
        Initializes the PXRDFile object with the given file path.

        Args:
            path (str): The path to the PXRD file.
        """
        self.path = path
        file_name = os.path.basename(path)

        # File name pattern: PXRD_(experiment id)_(X-ray source)_(sample holder shape)-(sample holder diameter).xyd, eg. PXRD_KE-232_Co-Kα1_film-3mm.xyd
        # Extract experiment id, x-ray source, sample holder shape and diameter from the file name
        file_name_parts = file_name.replace(".xyd", "").split("_")
        self.experiment_id = file_name_parts[1]
        self.xray_source = file_name_parts[2].replace("a","α")
        self.sample_holder_shape = file_name_parts[3].split("-")[0]
        self.sample_holder_diameter = file_name_parts[3].split("-")[1] if "-" in file_name_parts[3] else None
        process_pxrd_file_use_case_specific(self)  # Process the PXRD file



def collect_pxrd_file_paths(path: str) -> list:
    """
    Collects all PXRD files from the given directory and its subdirectories.

    Args:
        path (str): The path to the directory to search for PXRD files.

    Returns:
        list: A list of paths to the collected PXRD files.
    """
    import os
    import fnmatch

    pxrd_files = []
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, '*.xyd'):
            pxrd_files.append(os.path.join(root, file))
    return pxrd_files

def collect_pxrd_files(path: str) -> List[PXRDFile]:
    """
    Collects all PXRD files from the given directory and its subdirectories.

    Args:
        path (str): The path to the directory to search for PXRD files.

    Returns:
        list: A list of PXRDFile objects representing the collected PXRD files.
    """
    pxrd_files = collect_pxrd_file_paths(path)
    return [PXRDFile(pxrd_file) for pxrd_file in pxrd_files]


def filter_pxrd_files(experiment_id: str, all_pxrd_files: list) -> List[PXRDFile] | None:
    """
    Filters the collected PXRD files based on the given experiment ID.

    Args:
        experiment_id (str): The experiment ID to filter the PXRD files.
        all_pxrd_files (list): A list of PXRDFile objects representing all collected PXRD files.

    Returns:
        list: A list of PXRDFile objects representing the filtered PXRD files.
    """
    filtered_files = [pxrd_file for pxrd_file in all_pxrd_files if pxrd_file.experiment_id == experiment_id]
    return filtered_files if len(filtered_files) > 0 else None