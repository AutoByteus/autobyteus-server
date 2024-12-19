import os
import requests
from tqdm import tqdm


def download_with_progress(url: str, path: str, message: str):
    """Comman download utils to fetch data and store it in resource path."""
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Ensure we notice bad responses

    os.makedirs(os.path.dirname(path), exist_ok=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte

    with (
        open(path, "wb") as file,
        tqdm(
            desc=message,
            total=total_size,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar,
    ):
        for data in response.iter_content(block_size):
            file.write(data)
            bar.update(len(data))

    print(f"{message} completed and saved to {path}")
