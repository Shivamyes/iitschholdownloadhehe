import requests
import re
import subprocess
import os

# Brightcove account details
ACCOUNT_ID = "<your account id>"
LIVESTREAM_TOKEN_URL = "https://spec.iitschool.com/api/v1/livestreamToken"
CLASS_DETAIL_URL = "https://spec.iitschool.com/api/v1/class-detail"
BC_URL = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos/"
HEADERS = {
    "Accept": "application/json",
    "origintype": "web",
    "token": "<your token>",
    "usertype": "2",
    "Content-Type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
}

def sanitize_filename(filename):
    # Replace invalid characters with an underscore
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def fetch_and_download(class_id):
    response = requests.get(f"{CLASS_DETAIL_URL}/{class_id}", headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch class details for {class_id}")
        return

    data = response.json()
    lesson_url = data.get("data", {}).get("class_detail", {}).get("lessonUrl")
    if not lesson_url:
        print(f"Lesson URL not found for {class_id}")
        return

    if lesson_url.isdigit():
        token_response = requests.get(
            f"{LIVESTREAM_TOKEN_URL}?base=web&module=batch&type=brightcove&vid={class_id}",
            headers=HEADERS,
        )
        if token_response.status_code != 200:
            print(f"Failed to fetch Brightcove token for {class_id}")
            return

        token_data = token_response.json()
        brightcove_token = token_data["data"]["token"]

        video_id = data['data']['class_detail']['lessonName']
        video_url = f"{BC_URL}{lesson_url}/master.m3u8?bcov_auth={brightcove_token}"
        sanitized_video_id = sanitize_filename(video_id)  # Sanitize the filename
        output_file = f"{sanitized_video_id}.mp4"
        print(f"Downloading {video_id}")
        
        # Use ffmpeg without progress bar
        command = f'ffmpeg -loglevel error -i "{video_url}" -c copy -bsf:a aac_adtstoasc "{output_file}"'
        subprocess.run(command, shell=True)
        print(f"Saved as {output_file}")

    elif re.match("^[a-zA-Z0-9_-]*$", lesson_url):
        youtube_url = f"https://www.youtube.com/watch?v={lesson_url}"
        sanitized_class_id = sanitize_filename(class_id)  # Sanitize the filename
        output_file = f"{sanitized_class_id}.mp4"
        print(f"Downloading YouTube video {class_id}")
        
        # Use yt-dlp without progress bar
        command = ["yt-dlp", "-f", "best", "-o", output_file, youtube_url]
        subprocess.run(command)
        
        print(f"Saved as {output_file}")
    else:
        print(f"Invalid lesson URL format for {class_id}")

def read_class_ids_from_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
        class_ids = [class_id.strip() for class_id in content.split(',')]
        return class_ids

if __name__ == "__main__":
    class_ids = read_class_ids_from_file('class_ids.txt')  # Read class IDs from the text file
    for class_id in class_ids:
        fetch_and_download(class_id)
