from ._base import Provider
from ..utils import chdir, upload_to_remarkable
import os, tempfile, shutil

class EPUBProvider(Provider):
    """Provider for direct EPUB uploads"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override operations since we don't need PDF processing
        self.operations = []  # No operations needed for direct EPUB upload

    @staticmethod
    def validate(src):
        """Validate if source is an EPUB file"""
        # Convert to absolute path before validation
        abs_path = os.path.abspath(os.path.expanduser(src))
        return abs_path.lower().endswith('.epub') and os.path.exists(abs_path)


    def get_abs_pdf_urls(self, src):
        """For EPUB files, just return the local path as absolute path"""
        abs_path = os.path.abspath(os.path.expanduser(src))
        return abs_path, abs_path


    def run(self, src, filename=None):
        """Override run method to handle EPUB files directly"""
        # Convert to absolute path
        src = os.path.abspath(os.path.expanduser(src))

        if not self.validate(src):
            raise ValueError("Source must be a valid EPUB file")

        # Generate filename if not provided
        clean_filename = filename or os.path.basename(src)
        if not clean_filename.endswith('.epub'):
            clean_filename += '.epub'

        self.initial_dir = os.getcwd()
        with tempfile.TemporaryDirectory(prefix="p2r_") as working_dir:
            with chdir(working_dir):
                # Simply copy the EPUB file
                shutil.copy(src, clean_filename)

                if self.debug:
                    print("Paused in debug mode in dir: %s" % working_dir)
                    print("Press enter to exit.")
                    return input()

                if self.upload:
                    return upload_to_remarkable(
                        clean_filename,
                        remarkable_dir=self.remarkable_dir,
                        rmapi_path=self.rmapi_path,
                    )

                # If not uploading, copy to target directory
                target_path = os.path.join(self.initial_dir, clean_filename)
                while os.path.exists(target_path):
                    base = os.path.splitext(target_path)[0]
                    target_path = base + "_.epub"
                shutil.move(clean_filename, target_path)

        return target_path
