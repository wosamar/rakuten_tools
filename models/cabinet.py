class FileInfo:
    def __init__(self, file_elem):
        self.folder_id = file_elem.find("FolderId").text
        self.folder_name = file_elem.find("FolderName").text
        self.folder_path = file_elem.find("FolderPath").text
        self.file_id = file_elem.find("FileId").text
        self.file_name = file_elem.find("FileName").text
        self.file_path = file_elem.find("FilePath").text
        self.file_url = file_elem.find("FileUrl").text
        self.file_type = file_elem.find("FileType").text
        self.file_size = float(file_elem.findtext("FileSize", "0"))
        self.file_width = int(file_elem.findtext("FileWidth", "0"))
        self.file_height = int(file_elem.findtext("FileHeight", "0"))
        self.file_access_date = file_elem.find("FileAccessDate").text
        self.timestamp = file_elem.find("TimeStamp").text


class ShopInfo:
    def __init__(self, name):
        self.name = name
        self.folder_id = None
        self.folder_name = None
        self.folder_path = None
        self.file_count = 0
        self.files = []
        self.skus = set()  # 存原始 SKU

    def add_sku(self, sku):
        self.skus.add(sku)

    def set_folder(self, folder_elem):
        self.folder_id = folder_elem.find("FolderId").text
        self.folder_name = folder_elem.find("FolderName").text
        self.folder_path = folder_elem.find("FolderPath").text
        self.file_count = int(folder_elem.findtext("FileCount", "0"))

    def add_file(self, file_elem):
        self.files.append(FileInfo(file_elem))

    def has_folder(self):
        return self.folder_id is not None

    def has_files(self):
        return len(self.files) > 0

    def missing_files(self):
        missing = []
        file_names = [f.file_name for f in self.files]
        for sku in self.skus:
            # 把商店名稱去掉只比對編號
            parts = sku.split("-", 2)
            if len(parts) == 3:
                clean_sku = f"{parts[1]}-{parts[2]}"
            else:
                clean_sku = sku
            if not any(clean_sku in fn for fn in file_names):
                missing.append(sku)
        return missing