import os
import shutil
import argparse
from PIL import Image
from pillow_heif import register_heif_opener
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

register_heif_opener()


def process_image(args):
    file_path, target_dir, max_size = args
    filename = os.path.basename(file_path)

    try:
        with Image.open(file_path) as img:
            width, height = img.size

            if width < max_size or height < max_size:
                if filename.lower().endswith('.heic'):
                    jpeg_filename = os.path.splitext(filename)[0] + '.jpg'
                    jpeg_path = os.path.join(target_dir, jpeg_filename)
                    img.convert('RGB').save(jpeg_path, 'JPEG')
                else:
                    shutil.copy2(file_path, os.path.join(target_dir, filename))
                return filename
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

    return None


def process_images(source_dir, target_dir, max_size, num_threads):
    os.makedirs(target_dir, exist_ok=True)

    image_files = [
        os.path.join(source_dir, f) for f in os.listdir(source_dir)
        if os.path.isfile(os.path.join(source_dir, f)) and
        f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.heic'))
    ]

    small_files = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(
            process_image, (f, target_dir, max_size)) for f in image_files]

        for future in tqdm(as_completed(futures), total=len(image_files), desc="Processing images"):
            result = future.result()
            if result:
                small_files.append(result)

    return small_files


def main():
    parser = argparse.ArgumentParser(
        description="Process images and copy small ones.")
    parser.add_argument(
        "source_dir", help="Source directory containing images")
    parser.add_argument("--target_dir", default="~/Downloads/small_files",
                        help="Target directory for small images")
    parser.add_argument("--max_size", type=int, default=256,
                        help="Maximum size in pixels for either dimension")
    parser.add_argument("--threads", type=int,
                        default=os.cpu_count(), help="Number of threads to use")
    args = parser.parse_args()

    source_directory = args.source_dir
    target_directory = os.path.expanduser(args.target_dir)
    max_size = args.max_size
    num_threads = args.threads

    small_files_list = process_images(
        source_directory, target_directory, max_size, num_threads)

    print(f"\nFiles smaller than {max_size}x{max_size} pixels:")
    for file in small_files_list:
        print(file)

    print(f"\nSmall files have been copied to: {target_directory}")
    print(f"Total small files: {len(small_files_list)}")


if __name__ == "__main__":
    main()
