import sys
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


def upload_path_user(instance, filename):
    return "/".join(["user_image", filename])


def validate_image(image):
    file_size = image.size
    limit_byte_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size / 1024
        # converting into MB
        f = f / 1024
        raise ValidationError("Max size of file is %s MB" % f)


def compress_image(image):
    limit_byte_size = settings.MAX_COMPRESSED_IMAGE_SIZE
    print(f"Original image size: {image.size / 1024:.2f} KB")

    img = Image.open(image)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img_format = img.format or "JPEG"

    def compress(img, quality):
        buf = BytesIO()
        img.save(buf, format=img_format, quality=quality, optimize=True)
        return buf

    # Fast path: check if already small enough at quality 85
    buffer = compress(img, 85)
    compressed_size = buffer.tell()
    print(f"Compressed image size: {compressed_size / 1024:.2f} KB at quality 85")

    if compressed_size <= limit_byte_size:
        buffer.seek(0)
        return InMemoryUploadedFile(
            buffer,
            None,
            image.name,
            f"image/{img_format.lower()}",
            compressed_size,
            None,
        )

    # Binary search between min and 85 to find the sweet spot
    lo, hi = 20, 85
    best_buffer = None
    best_size = compressed_size

    while lo <= hi:
        mid = (lo + hi) // 2
        buffer = compress(img, mid)
        compressed_size = buffer.tell()
        print(
            f"Compressed image size: {compressed_size / 1024:.2f} KB at quality {mid}"
        )

        if compressed_size <= limit_byte_size:
            best_buffer = buffer  # best so far: fits and highest quality
            best_size = compressed_size
            lo = mid + 1  # try higher quality
        else:
            hi = mid - 1  # too big, try lower quality

    # If even quality 20 is too large, fall back to resizing
    if best_buffer is None:
        scale = 0.9
        # while scale >= 0.2:
        #     w, h = img.size
        #     resized = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        #     buffer = compress(resized, 20)
        #     compressed_size = buffer.tell()
        #     print(
        #         f"Compressed image size: {compressed_size / 1024:.2f} KB at scale {scale:.2f}"
        #     )
        #     if compressed_size <= limit_byte_size:
        #         best_buffer = buffer
        #         best_size = compressed_size
        #         break
        #     scale = round(scale - 0.1, 1)
        while True:
            w, h = img.size
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            resized = img.resize((new_w, new_h), Image.LANCZOS)
            buffer = compress(resized, 20)
            compressed_size = buffer.tell()
            print(
                f"Compressed image size: {compressed_size / 1024:.2f} KB at scale {scale:.2f}"
            )
            if compressed_size <= limit_byte_size or new_w == 1 or new_h == 1:
                best_buffer = buffer
                best_size = compressed_size
                break
            scale = round(scale - 0.05, 2)

    if best_buffer is None:
        limit_mb = limit_byte_size / 1024 / 1024
        raise ValidationError("Max size of file is %s MB" % limit_mb)

    best_buffer.seek(0)
    return InMemoryUploadedFile(
        best_buffer, None, image.name, f"image/{img_format.lower()}", best_size, None
    )
