import os
import unittest
from encryption_logic import equalize

class TestEncryption(unittest.TestCase):

    def setUp(self):
        """Set up test files."""
        self.file1_path = "file1.bin"
        self.file2_path = "file2.bin"
        with open(self.file1_path, "wb") as f:
            f.write(os.urandom(10))
        with open(self.file2_path, "wb") as f:
            f.write(os.urandom(20))

    def tearDown(self):
        """Tear down test files."""
        if os.path.exists(self.file1_path):
            os.remove(self.file1_path)
        if os.path.exists(self.file2_path):
            os.remove(self.file2_path)

    def test_equalize_pads_smaller_file(self):
        """Test that equalize pads the smaller file to the size of the larger file."""
        # Ensure file1 is smaller than file2 before equalization
        self.assertLess(os.path.getsize(self.file1_path), os.path.getsize(self.file2_path))

        # Call the function to be tested
        equalize(self.file1_path, self.file2_path)

        # Check if the files are equal in size after equalization
        self.assertEqual(os.path.getsize(self.file1_path), os.path.getsize(self.file2_path))

    def test_equalize_preserves_content(self):
        """Test that equalize preserves the content of the original files."""
        with open(self.file1_path, "rb") as f:
            original_content1 = f.read()
        with open(self.file2_path, "rb") as f:
            original_content2 = f.read()

        equalize(self.file1_path, self.file2_path)

        with open(self.file1_path, "rb") as f:
            new_content1 = f.read()
        with open(self.file2_path, "rb") as f:
            new_content2 = f.read()

        self.assertTrue(new_content1.startswith(original_content1))
        self.assertTrue(new_content2.startswith(original_content2))

if __name__ == '__main__':
    unittest.main()
