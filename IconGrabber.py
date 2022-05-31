import os

class IconGrabber:
    def __init__(self, images_repo):
        self.images_repo = images_repo
    
    def grab_filepath(self, filename: str):
        # Filename is a file brought from outside source, Example: examp.xlsx
        if '.' in filename:
            ext = filename.split('.')[-1]
            file_projected_path = self.images_repo + ext + '.png'
            if os.path.isfile(file_projected_path):
                return file_projected_path

        # No file extension found
        return self.images_repo + '_blank.png'
        