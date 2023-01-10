import os
import tempfile
import pandas as pd
from ango.sdk import SDK
from html import unescape
from ango.plugins import MarkdownPlugin, run

HOST = '<YOUR HOST>'
API_KEY = '<YOUR API KEY>'
PLUGIN_ID = '<YOUR PLUGIN ID>'
PLUGIN_SECRET = '<YOUR PLUGIN SECRET>'

sdk = SDK(api_key=API_KEY, host=HOST)


def sample_callback_function(projectId, file, batches, markdown_text, logger):
    # Read CSV file
    data_df = pd.read_csv(file, dtype=str)
    field_list = list(data_df.columns)
    # Replace escape parameters in HTML code
    markdown_text_raw = unescape(markdown_text)

    # Create tmp directory
    if not os.path.exists('tmp'):
        os.mkdir('tmp')

    for index in range(len(data_df)):
        # Replace placeholders in markdown text with the values on the CSV file
        markdown_text_processed = markdown_text_raw
        for field in field_list:
            search_keyword = '|' + field + '|'
            replace_keyword = data_df.iloc[index][field]
            markdown_text_processed = markdown_text_processed.replace(search_keyword, replace_keyword)

        # Create temporary md file
        with tempfile.TemporaryFile(dir='tmp', suffix='.md', delete=False) as tmp_file:
            tmp_file.write(markdown_text_processed.encode())
            fullpath = tmp_file.name

        # Upload created markdown file
        external_id = str(index).zfill(5) + '.md'
        file_paths = [{"data": fullpath, "externalId": external_id}]
        sdk.upload_files(projectId, file_paths)
        os.remove(fullpath)

    return 'All markdown files are uploaded!'


if __name__ == "__main__":
    plugin = MarkdownPlugin(id=PLUGIN_ID,
                            secret=PLUGIN_SECRET,
                            callback=sample_callback_function)

    run(plugin, host=HOST)
