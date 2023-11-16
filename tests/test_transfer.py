##### PSA: This test has external dependencies 'wrapt_timeout_decorator' and 'unittest' #####
##### OBS: I strongly discourage running this test on a production machine. #####

import wrapt_timeout_decorator
from unittest.mock import patch
import os, time

@wrapt_timeout_decorator.timeout(10)
def test_implicit_mount():
    print("Running basic functionality test.")
    with patch.dict('os.environ', {
        'PYREMOTEDATA_REMOTE_USERNAME': 'foo',
        'PYREMOTEDATA_REMOTE_URI': '0.0.0.0',
        'PYREMOTEDATA_REMOTE_DIRECTORY': 'upload',
        'PYREMOTEDATA_AUTO': 'yes'
    }):
        # Import the module
        from pyremotedata.implicit_mount import IOHandler
        # Open the connection
        handler = IOHandler()
        handler.start()
        # Run some commands
        print(handler.pwd())
        print(handler.ls())
        # Cleanup
        handler.stop()
        from pyremotedata.config import remove_config
        remove_config()
    print("Basic functionality test passed.")

@wrapt_timeout_decorator.timeout(25)
def test_upload_download():
    print("Running upload/download test.")
    with patch.dict('os.environ', {
        'PYREMOTEDATA_REMOTE_USERNAME': 'foo',
        'PYREMOTEDATA_REMOTE_URI': '0.0.0.0',
        'PYREMOTEDATA_REMOTE_DIRECTORY': 'upload',
        'PYREMOTEDATA_AUTO': 'yes'
    }):
        # Import the module
        from pyremotedata.implicit_mount import IOHandler
        # Open the connection
        handler = IOHandler()
        handler.start()
        print(handler.pwd())
        # Upload a test file to the mock SFTP server
        os.system("openssl rand -out localfile.txt -base64 $(( 2**27 * 9/16 ))")
        start_upload = time.time()
        upload_result = handler.put("localfile.txt", "testfile.txt")
        end_upload = time.time()
        # Download the test file from the mock SFTP server
        start_download = time.time()
        download_result = handler.download("testfile.txt", "testfile.txt")
        end_download = time.time()
        # Get the local directory where the file should be downloaded to
        local_directory = handler.lpwd()
        # Sanity checks
        local_file_exists = os.path.exists(os.path.join(local_directory, 'testfile.txt'))
        local_file_size = os.path.getsize(os.path.join(local_directory, 'testfile.txt')) / 10**6
        if not local_file_exists:
            raise RuntimeError("Something went wrong with the download. The file does not exist locally.")
        if not (local_file_size > 10 and local_file_size < 20):
            raise RuntimeError("Something went wrong with the download. The file size is not correct.")
        # Cleanup
        handler.stop() 
        os.remove("localfile.txt")       
        from pyremotedata.config import remove_config
        remove_config()

    # Calculate results
    upload_time = end_upload - start_upload
    download_time = end_download - start_download
    upload_speed, download_speed = 100/upload_time, 100/download_time
    print(f'Upload/download test passed with upload {upload_speed:.1f} MB/s and download {download_speed:.1f} MB/s.') 

try:
    test_implicit_mount()
except Exception as e:
    print("Basic functionality test failed.")
    raise e

try:
    test_upload_download()
except Exception as e:
    print("Upload/download test failed.")
    raise e