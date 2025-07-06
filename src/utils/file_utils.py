import os

class FileUtils:
    @staticmethod
    def create_folder(folder_name: str) -> str:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        folder_path = os.path.join(project_root, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        return folder_path