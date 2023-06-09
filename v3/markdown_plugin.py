import math
import json
import numpy as np
import pandas as pd
from io import BytesIO
from ango.sdk import SDK
from html import unescape
from base64 import b64decode
from imerit_ango.plugins import MarkdownPlugin, run

HOST = '<YOUR HOST>'
PLUGIN_ID = '<YOUR PLUGIN ID>'
PLUGIN_SECRET = '<YOUR PLUGIN SECRET>'


def check_config(config, column_names):
    batch_name_column = 'AUTO_DETECT'
    if 'batch_name_column' in config:
        if config['batch_name_column'] in column_names:
            batch_name_column = config['batch_name_column']

    external_id_columns = []
    if 'external_id_columns' in config:
        external_id_columns = config['external_id_columns']

    upload_batch_size = 100
    if 'upload_batch_size' in config:
        if isinstance(config['upload_batch_size'], int):
            if config['upload_batch_size'] > 0:
                upload_batch_size = config['upload_batch_size']

    return batch_name_column, external_id_columns, upload_batch_size


def sample_callback(**data):
    # Extract input parameters
    file = data.get('inputFile')
    project_id = data.get('projectId')
    api_key = data.get('apiKey')
    # batches = data.get('batches', [])
    markdown_text = data.get('markdownText', [])
    # integration_id = data.get('integrationId')
    logger = data.get('logger')
    config_str = data.get('configJSON')
    config = json.loads(config_str)

    logger.info("Plugin session is started!")

    sdk = SDK(api_key=api_key, host=HOST)

    # Read CSV file
    file_decoded = BytesIO(b64decode(file))
    data_df = pd.read_csv(file_decoded, dtype=str, keep_default_na=False)
    field_list = list(data_df.columns)

    batch_name_column, external_id_columns, upload_batch_size = check_config(config, field_list)

    # Detect the batch field
    batch_field = ""
    batch_flag = False
    if batch_name_column == "AUTO_DETECT":
        batch_keywords = ['batch', 'batch_name', 'batch-name', 'batchname']
        for field in field_list:
            if field.lower() in batch_keywords:
                batch_field = field
                batch_flag = True
                break
    elif batch_name_column == "IGNORE":
        batch_field = ""
        batch_flag = False
    else:
        batch_field = batch_name_column
        batch_flag = True

    # Get project batches
    project_batch_name_list = []
    if batch_flag:
        batch_response = sdk.get_batches(project_id)
        for index in range(len(batch_response)):
            batch_name = batch_response[index]['name']
            project_batch_name_list.append(batch_name)

    # Create batches
    if batch_flag:
        unique_batch_name_list = list(data_df[batch_field].unique())
        for batch_name in unique_batch_name_list:
            if batch_name not in project_batch_name_list:
                sdk.create_batch(project_id=project_id, batch_name=batch_name)

    # Replace escape characters in HTML code
    markdown_text_raw = unescape(markdown_text)

    response = {'status': 'success'}
    batch_size = upload_batch_size
    num_batches = math.ceil(len(data_df) / batch_size)
    logger.info("Files Uploaded: [" + str(len(data_df)) + "/0]")
    for batch_index in range(num_batches):
        start_index = batch_index*batch_size
        end_index = np.min([(batch_index+1)*batch_size, len(data_df)])

        file_paths = []
        for index in range(start_index, end_index):
            # Replace placeholders in Markdown text with the values on the CSV file
            markdown_text_processed = markdown_text_raw
            for field in field_list:
                search_keyword = '|' + field + '|'
                replace_keyword = data_df.iloc[index][field]
                markdown_text_processed = markdown_text_processed.replace(search_keyword, replace_keyword)

            # Create temporary md file
            if len(external_id_columns) == 0:
                external_id = str(index).zfill(5) + '.md'
            else:
                name_list = []
                for external_id_column in external_id_columns:
                    name_list.append(data_df.iloc[index][external_id_column])
                external_id = '_'.join(name_list)

            if batch_flag:
                batch_name = data_df.iloc[index][batch_field]
                file_paths.append({"data": markdown_text_processed, "externalId": external_id, "batches": [batch_name]})
            else:
                file_paths.append({"data": markdown_text_processed, "externalId": external_id})

        response = sdk.upload_files_cloud(project_id=project_id, assets=file_paths)
        logger.info("Files Uploaded: [" + str(len(data_df)) + "/" + str(end_index) + "]")

    logger.info("Plugin session is ended!")
    if response['status'] == 'success':
        return 'All markdown files are uploaded!'
    else:
        logger.warning(response['message'])
        return response['message']


if __name__ == "__main__":
    plugin = MarkdownPlugin(id=PLUGIN_ID,
                            secret=PLUGIN_SECRET,
                            callback=sample_callback)

    run(plugin, host=HOST)
