import qrcode
import uuid
import PySimpleGUI as sg
import os
from PIL import Image
import configparser

def save_paths_to_ini(infile, outdir, imgdir):
    config = configparser.ConfigParser()
    config['Paths'] = {
        'InputFile': infile,
        'OutputDir': outdir,
        'ImageDir': imgdir
    }

    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

def load_paths_from_ini():
    config = configparser.ConfigParser()
    config.read('settings.ini')

    paths = {
        '-INFILE-': '',
        '-OUTDIR-': '',
        '-IMGDIR-': ''
    }

    if 'Paths' in config:
        paths['-INFILE-'] = config['Paths'].get('InputFile', '')
        paths['-OUTDIR-'] = config['Paths'].get('OutputDir', '')
        paths['-IMGDIR-'] = config['Paths'].get('ImageDir', '')

    return paths

def generate_uuid_file(output_filepath, num_of_codes):
    with open(output_filepath, 'w') as f:
        for _ in range(num_of_codes):  # Use the specified number here
            f.write(f"('{uuid.uuid4()}'),\n")

def generate_qr_code(data, filename):
    img = qrcode.make(data)
    img.save(filename)

def generate_uuids_to_file(num_uuids, filename):
    with open(filename, 'w') as file:
        for _ in range(num_uuids):
            file.write(f"('{uuid.uuid4()}'),\n")

def create_qr_codes_from_file(input_filepath, output_dir):
    with open(input_filepath, 'r') as file:
        lines = file.readlines()

    for index, line in enumerate(lines):
        uuid_str = line.strip("('),\n")
        qr_data = "https://hedt.dev/contest/" + uuid_str
        generate_qr_code(qr_data, f"{output_dir}/qr_code_{index + 1}.png")

def generate_pdf_from_images(input_dir, output_filepath):
    A4_WIDTH, A4_HEIGHT = 595, 842  # In pixels at 72 DPI
    COLS, ROWS = 4, 5
    images = []

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.png'):
            image_path = os.path.join(input_dir, filename)
            image = Image.open(image_path)
            images.append(image)

    qr_width = A4_WIDTH // COLS
    qr_height = A4_HEIGHT // ROWS
    
    pdf_pages = []

    for i in range(0, len(images), COLS * ROWS):
        page = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), 'white')
        for row in range(ROWS):
            for col in range(COLS):
                idx = i + row * COLS + col
                if idx < len(images):
                    img = images[idx].resize((qr_width, qr_height))
                    page.paste(img, (col * qr_width, row * qr_height))
        pdf_pages.append(page)

    if pdf_pages:  # Ensure the list is not empty
        pdf_pages[0].save(output_filepath, save_all=True, append_images=pdf_pages[1:])
    else:
        sg.popup_error('No PNG images found in the specified directory')


def main():
    initial_paths = load_paths_from_ini()

    layout = [
        [sg.Text('Input File'), sg.InputText(initial_paths['-INFILE-'], key='-INFILE-'), sg.FileBrowse(),
        sg.Text('Number of Codes'), sg.InputText('10', size=(5, 1), key='-NUMCODES-')], 
        [sg.Text('Output Dir for QR Codes'), sg.InputText(initial_paths['-OUTDIR-'], key='-OUTDIR-'), sg.FolderBrowse()],
        [sg.Text('Image Dir for PDF'), sg.InputText(initial_paths['-IMGDIR-'], key='-IMGDIR-'), sg.FolderBrowse()],
        [sg.Button('Generate Text File'), sg.Button('Generate QR Codes'), sg.Button('Generate PDF')],
        [sg.Exit()]
    ]


    window = sg.Window('QR Code Generator', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        elif event == 'Generate Text File':
            if values['-INFILE-']:
                num_of_codes = int(values['-NUMCODES-'])  # Get the number from the input
                generate_uuid_file(values['-INFILE-'], num_of_codes)
                sg.popup('Text file generated with UUIDs!')
            else:
                sg.popup_error('Please select a file path for input.txt')
        elif event == 'Generate QR Codes':
            if values['-INFILE-'] and values['-OUTDIR-']:
                create_qr_codes_from_file(values['-INFILE-'], values['-OUTDIR-'])
                save_paths_to_ini(values['-INFILE-'], values['-OUTDIR-'], values['-IMGDIR-'])
                sg.popup('QR Codes generated in', values['-OUTDIR-'])
            else:
                sg.popup_error('Please select both input file path and output directory')
        elif event == 'Generate PDF':
            if values['-IMGDIR-']:
                output_pdf_path = os.path.join(values['-IMGDIR-'], 'output.pdf')
                save_paths_to_ini(values['-INFILE-'], values['-OUTDIR-'], values['-IMGDIR-'])
                generate_pdf_from_images(values['-IMGDIR-'], output_pdf_path)
                sg.popup('PDF generated at', output_pdf_path)
            else:
                sg.popup_error('Please select an image directory')
                
    window.close()

if __name__ == '__main__':
    main()