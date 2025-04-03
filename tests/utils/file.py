import base64
import os
from typing import List, Optional


def create_unique_filename(dir_name: str, file_name: str, ext: str = "md") -> str:
    """
    Generates a unique file name by appending _num if the file already exists.

    Args:
        dir_name (str): The name of the folder.
        file_name (str): The name of the file.
        ext (str): The file extension. Defaults to "md".

    Returns:
        str: The unique file path.

    Raises:
        ValueError: If dir_name or file_name is empty.
    """
    if not dir_name or not file_name:
        raise ValueError("Directory name and file name cannot be empty")

    if not ext:
        ext = "md"

    output_dir = os.path.join(os.getcwd(), dir_name)
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"{file_name}.{ext}")
    num = 1

    while os.path.exists(output_file):
        output_file = os.path.join(output_dir, f"{file_name}_{num}.{ext}")
        num += 1

    return output_file


def save_text_to_unique_file(
    text: str, file_name: str = "text_output", ext: str = "md", dir_name: str = "output"
) -> Optional[str]:
    """
    Saves text to a uniquely named file in the specified folder.

    Args:
        text (str): The text to save.
        file_name (str): The name of the file. Defaults to "text_output".
        ext (str): The file extension. Defaults to "md".
        dir_name (str): The name of the folder. Defaults to "output".

    Returns:
        Optional[str]: The path to the saved file or None if saving failed.
    """
    if not text:
        return None

    try:
        modified_file_name = file_name.replace(" ", "_")
        output_file = create_unique_filename(dir_name, modified_file_name, ext)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(str(text))

        print(f"Text saved to {output_file}")
        return output_file

    except Exception as e:
        print(f"Error saving text: {str(e)}")
        return None


def save_list_to_unique_file(
    text_list: List, file_name: str = "text_output", ext: str = "md", dir_name: str = "output"
) -> Optional[List[str]]:
    """
    Saves a list of text to a uniquely named file in the specified folder.

    Args:
        text_list (List[str]): The text to save.
        file_name (str): The name of the file. Defaults to "text_output".
        ext (str): The file extension. Defaults to "md".
        dir_name (str): The name of the folder. Defaults to "output".

    Returns:
        Optional[List[str]]: The path to the saved file or None if saving failed.
    """
    if not text_list:
        return None

    file_names: List = []
    try:
        for text in text_list:
            output_file = save_text_to_unique_file(text, file_name, ext, dir_name)
            file_names.append(output_file)
        return file_names
    except Exception as e:
        print(f"Error saving text: {str(e)}")
        return None


def save_png_to_unique_file(
    png_data: str, file_name: str = "screenshot", dir_name: str = "output"
) -> Optional[str]:
    """
    Saves PNG data to a uniquely named file in the specified folder.

    Args:
        png_data (str): The PNG data to save.
        file_name (str): The name of the file. Defaults to "screenshot".
        dir_name (str): The name of the folder. Defaults to "output".

    Returns:
        Optional[str]: The path to the saved file or None if saving failed.
    """

    if not png_data:
        return None

    try:
        output_file = create_unique_filename(dir_name, file_name, "png")

        decoded_data = base64.b64decode(png_data)
        with open(output_file, "wb") as f:
            f.write(decoded_data)

        print(f"PNG saved to {output_file}")
        return output_file

    except Exception as e:
        print(f"Error saving PNG: {str(e)}")
        return None


if __name__ == "__main__":
    # Test cases for create_unique_filename
    def test_create_unique_filename():
        print("\nTesting create_unique_filename...")

        # Test basic functionality
        filename1 = create_unique_filename("test_dir", "test_file")
        print(f"Created filename: {filename1}")

        # Test with different extension
        filename2 = create_unique_filename("test_dir", "test_file", "txt")
        print(f"Created filename with custom extension: {filename2}")

        # Test error handling
        try:
            create_unique_filename("", "test_file")
        except ValueError as e:
            print(f"Caught expected error: {e}")

    # Test cases for save_text_to_unique_file
    def test_save_text_to_unique_file():
        print("\nTesting save_text_to_unique_file...")

        # Test with valid text
        test_text = "This is a test text"
        result = save_text_to_unique_file(test_text, "test_text")
        print(f"Save result: {result}")

        # Test with empty text
        result = save_text_to_unique_file("", "empty_text")
        print(f"Empty text result: {result}")

    # Run all tests
    test_create_unique_filename()
    test_save_text_to_unique_file()
