import json
import zipfile
from tqdm import tqdm
from io import BytesIO
from ango.sdk import SDK
from ango.plugins import ExportPlugin, run

HOST = '<YOUR HOST>'
API_KEY = '<YOUR API KEY>'
PLUGIN_ID = '<YOUR PLUGIN ID>'
PLUGIN_SECRET = '<YOUR PLUGIN SECRET>'

sdk = SDK(api_key=API_KEY, host=HOST)


def sample_callback_function(projectId, jsonExport, logger):
    # Convert annotation data to intended format
    file_list = []
    for image_index, asset in enumerate(tqdm(jsonExport)):
        external_id = asset['externalId']
        data_url = asset['asset']
        objects = asset['tasks'][0]['objects']

        object_list = []
        for obj in objects:
            if "bounding-box" in obj:
                class_name = obj['title']
                x, y = int(round(obj["bounding-box"]['x'])), int(round(obj["bounding-box"]['y']))
                w, h = int(round(obj["bounding-box"]['width'])), int(round(obj["bounding-box"]['height']))

                single_object_string = ' '.join([class_name, str(x), str(y), str(w), str(h)])
                object_list.append(single_object_string)
        object_string = '-'.join(object_list)
        file_list.append({'externalId': external_id, 'URL': data_url, 'Annotations': object_string})

    # Create zip file
    zip_file_name = projectId + '.zip'
    zip_data = BytesIO()
    with zipfile.ZipFile(zip_data, mode="w") as zf:
        zf.writestr(projectId + '.json', json.dumps(file_list))

    return zip_file_name, zip_data


if __name__ == "__main__":
    plugin = ExportPlugin(id=PLUGIN_ID,
                          secret=PLUGIN_SECRET,
                          api_key=API_KEY,
                          callback=sample_callback_function,
                          host=HOST)

    run(plugin, host=HOST)
