import re, os


class FileOperations():
    def read(self, file):
        file_name = re.findall(r'[^\\]+$', file)[0]
        file_info = os.path.splitext(file_name)
        with open(file, "r") as f:
            file_data = {
                "name": file_info[0],
                "type": file_info[1],
                "content": f
            }
            return file_data

    def write(self):
        with open("1.txt", "w") as f:
            f.write("hello world")


