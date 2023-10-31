import os
import pandas as pd
import argparse
from jinja2 import Environment, FileSystemLoader

class ClassGenerator:
    def __init__(self, excel_file, template_file, language, code_folder):
        self.excel_file = excel_file
        self.template_file = template_file
        self.language = language
        self.code_folder = code_folder
    
    def read_excel(self, sheet_name):
        df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
        df['Multiplicity'].fillna(-1, inplace=True)
        df['Multiplicity'] = df['Multiplicity'].astype(int)
        df['Multiplicity'].replace(-1, pd.NA, inplace=True)
        return df

    def write_to_file(self, descriptor):
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template(self.template_file)
        extension_mapping = {'python': '.py', 'matlab': '.m', 'c': '.c'}

        extension = extension_mapping.get(self.language, '.txt')  # Default to .txt if language not supported

        if not os.path.exists(self.code_folder):
            os.makedirs(self.code_folder)

        for name, df in descriptor.items():
            file_path = os.path.join(self.code_folder, f"{name}{extension}")
            with open(file_path, "w") as f:
                f.write(template.render(name=name, attributes=df.to_dict(orient='records')))

    def generate_classes(self):
        xls = pd.ExcelFile(self.excel_file)
        sheet_names = xls.sheet_names
        descriptor = {}

        for sheet_name in sheet_names:
            df = self.read_excel(sheet_name)
            descriptor[sheet_name] = df

        self.write_to_file(descriptor)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate code from an Excel file.')
    parser.add_argument('--excel_file', required=True, help='Path for the Excel code descriptor file.')
    parser.add_argument('--template_file', required=True, help='Path for the Jinja2 template file.')
    parser.add_argument('--language', required=True, help='Language for the generated code.')
    parser.add_argument('--code_folder', required=True, help='Folder for the generated code.')
    args = parser.parse_args()

    generator = ClassGenerator(args.excel_file, args.template_file, args.language, args.code_folder)
    generator.generate_classes()
