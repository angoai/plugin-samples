import json
import zipfile
from tqdm import tqdm
from io import BytesIO
from imerit_ango.plugins import ExportPlugin, ExportResponse, run

HOST = '<YOUR HOST>'
PLUGIN_ID = '<YOUR PLUGIN ID>'
PLUGIN_SECRET = '<YOUR PLUGIN SECRET>'


def sample_callback(data):
    # Extract input parameters
    project_id = data.get('projectId')
    json_export = data.get('jsonExport')
    num_assets = data.get('numTasks')
    logger = data.get('logger')
    config_str = data.get('configJSON')
    config = json.loads(config_str)

    logger.info("Plugin session is started!")

    # Check config input
    separator_char = '-'
    if 'separator-character' in config:
        if isinstance(config['separator-character'], str):
            separator_char = config['separator-character']

    # Convert annotation data to intended format
    file_list = []
    for asset_index, asset in enumerate(tqdm(json_export)):
        external_id = asset['externalId']
        data_url = asset['asset']
        objects = asset['task']['tools']

        object_list = []
        for obj in objects:
            if "bounding-box" in obj:
                class_name = obj['title']
                x, y = int(round(obj["bounding-box"]['x'])), int(round(obj["bounding-box"]['y']))
                w, h = int(round(obj["bounding-box"]['width'])), int(round(obj["bounding-box"]['height']))

                single_object_string = ' '.join([class_name, str(x), str(y), str(w), str(h)])
                object_list.append(single_object_string)
        object_string = separator_char.join(object_list)
        file_list.append({'externalId': external_id, 'URL': data_url, 'Annotations': object_string})

    # Create zip file
    zip_file_name = project_id + '.zip'
    zip_data = BytesIO()
    with zipfile.ZipFile(zip_data, mode="w") as zf:
        zf.writestr(project_id + '.json', json.dumps(file_list, indent=4))

    logger.info("Plugin session is ended!")

    export_response_obj = ExportResponse(file=zip_data, file_name=zip_file_name, storage_id="" ,bucket="")
    return export_response_obj


if __name__ == "__main__":
    plugin = ExportPlugin(id=PLUGIN_ID,
                          secret=PLUGIN_SECRET,
                          callback=sample_callback,
                          host=HOST, 
                          version='v3')

    run(plugin, host=HOST)
