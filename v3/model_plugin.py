import json
from ango.sdk import SDK
from ango.plugins import ModelPlugin, run

HOST = '<YOUR HOST>'
PLUGIN_ID = '<YOUR PLUGIN ID>'
PLUGIN_SECRET = '<YOUR PLUGIN SECRET>'


def run_model(**data):
    # Extract input parameters
    project_id = data.get('projectId')
    asset_id = data.get('assetId')
    category_schema = data.get('categorySchema')
    # logger = data.get('logger')
    api_key = data.get('apiKey')
    config_str = data.get('configJSON')
    if config_str is not None:
        config = json.loads(config_str)

    # logger.info("Plugin session is started!")

    sdk = SDK(api_key=api_key, host=HOST)

    get_asset_response = sdk.get_assets(project_id=project_id, asset_id=asset_id)
    data_url = get_asset_response['data']['assets'][0]['data']
    
    object_id = "100001"
    if category_schema is None:
        bbox_obj = [{"objectId": object_id, "bounding-box": {"x": 20, "y": 30, "width": 50, "height": 60}}]
        annotation_json = {"data": data_url,
                           "answer": {"objects": bbox_obj, "classifications": [], "relations": []}}
    else:
        schema_id = category_schema[0]['schemaId']
        bbox_obj = [{"objectId": object_id, "schemaId": schema_id,
                     "bounding-box": {"x": 20, "y": 30, "width": 50, "height": 60}}]
        annotation_json = {"data": data_url,
                           "answer": {"objects": bbox_obj, "classifications": [], "relations": []}}
    
    # logger.info("Plugin session is ended!")
    return annotation_json


if __name__ == "__main__":
    plugin = ModelPlugin(id=PLUGIN_ID,
                         secret=PLUGIN_SECRET,
                         callback=run_model,
                         host=HOST)

    run(plugin, host=HOST)
