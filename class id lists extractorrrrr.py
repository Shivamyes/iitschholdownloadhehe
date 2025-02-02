import requests
import logging

# Set up logging to track progress
logging.basicConfig(filename='script.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Define headers for API requests
headers = {
    "Accept": "application/json",
    "origintype": "web",
    "token": "<your token>",
    "usertype": "2",
    "Content-Type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
}

# Function to get batch-subject and extract IDs
def get_batch_subject_ids():
    url = "https://spec.iitschool.com/api/v1/batch-subject/108"
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        # Extract subject IDs
        subject_ids = [subject['id'] for subject in data['data']['batch_subject']]
        return subject_ids
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching batch-subject: {e}")
        return []

# Function to get batch-topic and extract topic IDs
def get_batch_topic_ids(subject_id):
    url = f"https://spec.iitschool.com/api/v1/batch-topic/{subject_id}?type=class"
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        # Extract topic IDs
        topic_ids = [topic['id'] for topic in data['data']['batch_topic']]
        return topic_ids
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching batch-topic for subject ID {subject_id}: {e}")
        return []

# Function to get batch-detail and extract class IDs
def get_batch_detail_classes(subject_id, topic_id):
    url = f"https://spec.iitschool.com/api/v1/batch-detail/108?subjectId={subject_id}&topicId={topic_id}"
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        # Check if 'class_list' and 'classes' key exist in the response
        if 'class_list' in data.get('data', {}) and 'classes' in data['data']['class_list']:
            class_ids = [cls['id'] for cls in data['data']['class_list']['classes']]
            return class_ids
        else:
            logging.warning(f"No 'classes' found for subject ID {subject_id} and topic ID {topic_id}.")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching batch-detail for subject ID {subject_id} and topic ID {topic_id}: {e}")
        return []

# Main function to process all subjects, topics, and classes
def process_and_save_class_ids():
    logging.info("Starting to process subjects and topics...")
    all_class_ids = []
    subject_ids = get_batch_subject_ids()

    # Loop through all subject IDs
    for idx, subject_id in enumerate(subject_ids, 1):
        logging.info(f"Processing subject {idx}/{len(subject_ids)} with ID {subject_id}...")
        topic_ids = get_batch_topic_ids(subject_id)
        
        # Loop through all topic IDs for the current subject
        for topic_idx, topic_id in enumerate(topic_ids, 1):
            logging.info(f"Processing topic {topic_idx}/{len(topic_ids)} with ID {topic_id}...")
            class_ids = get_batch_detail_classes(subject_id, topic_id)
            all_class_ids.extend(class_ids)

    # Save all collected class IDs to a text file
    with open("class_ids.txt", "w") as file:
        for class_id in all_class_ids:
            file.write(f"{class_id}\n")

    logging.info(f"Finished processing all subjects and topics. Total class IDs: {len(all_class_ids)}.")
    print(f"Finished processing. Class IDs are saved in 'class_ids.txt'.")

# Run the program
if __name__ == "__main__":
    process_and_save_class_ids()
