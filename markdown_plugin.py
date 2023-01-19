import os
import pandas as pd
from tqdm import tqdm
from io import BytesIO
from ango.sdk import SDK
from shutil import rmtree
from html import unescape
from base64 import b64decode
from ango.plugins import MarkdownPlugin, run

HOST = '<YOUR HOST>'
PLUGIN_ID = '<YOUR PLUGIN ID>'
PLUGIN_SECRET = '<YOUR PLUGIN SECRET>'


def sample_callback_function(**data):
    # Extract input parameters
    file = data.get('inputFile')
    projectId = data.get('projectId')
    api_key = data.get('apiKey')
    batches = data.get('batches', [])
    markdown_text = data.get('markdownText', [])
    integration_id = data.get('integrationId')
    logger = data.get('logger')

    sdk = SDK(api_key=api_key, host=HOST)

    # Read CSV file
    file_decoded = BytesIO(b64decode(file))
    data_df = pd.read_csv(file_decoded, dtype=str)
    field_list = list(data_df.columns)

    # Create Batches
    batch_keywords = ['batch', 'batch_name', 'batch-name', 'batchname']
    batch_field = ""
    batch_flag = False
    for field in field_list:
        if field.lower() in batch_keywords:
            batch_field = field
            batch_flag = True
            break

    # Get project batches
    project_batch_name_list = []
    if batch_flag:
        batch_response = sdk.get_batches(projectId)
        for index in range(len(batch_response)):
            batch_name = batch_response[index]['name']
            project_batch_name_list.append(batch_name)

    # Create batches
    if batch_flag:
        unique_batch_name_list = list(data_df[batch_field].unique())
        for batch_name in unique_batch_name_list:
            if batch_name not in project_batch_name_list:
                sdk.create_batch(project_id=projectId, batch_name=batch_name)

    # Replace escape parameters in HTML code
    markdown_text_raw = unescape(markdown_text)

    # Create tmp directory
    TEMP_FILE = 'tmp'
    if not os.path.exists(TEMP_FILE):
        os.mkdir(TEMP_FILE)

    for index in range(len(data_df)):
        # Replace placeholders in markdown text with the values on the CSV file
        markdown_text_processed = markdown_text_raw
        for field in field_list:
            search_keyword = '|' + field + '|'
            replace_keyword = data_df.iloc[index][field]
            markdown_text_processed = markdown_text_processed.replace(search_keyword, replace_keyword)

        # Create temporary md file
        f = open("%sdemofile%s.md" % (TEMP_FILE, index), "w")
        f.write(markdown_text_processed)
        f.close()
        fullpath = f.name

        # Upload created markdown file
        external_id = str(index).zfill(5) + '.md'
        file_paths = [{"data": fullpath, "externalId": external_id}]

        if batch_flag:
            batch_name = data_df.iloc[index][batch_field]
            batch_list = [batch_name]
            sdk.upload_files(project_id=projectId, file_paths=file_paths, batches=batch_list)
        else:
            sdk.upload_files(project_id=projectId, file_paths=file_paths)

    rmtree(TEMP_FILE)
    return 'All markdown files are uploaded!'


if __name__ == "__main__":
    plugin = MarkdownPlugin(id=PLUGIN_ID,
                            secret=PLUGIN_SECRET,
                            callback=sample_callback_function)

    run(plugin, host=HOST)
