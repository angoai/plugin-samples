from ango.sdk import SDK
from ango.plugins import BatchModelPlugin, run

HOST = '<YOUR HOST>'
PLUGIN_ID = '<YOUR PLUGIN ID>'
PLUGIN_SECRET = '<YOUR PLUGIN SECRET>'


def run_model(**data):
    # Extract input parameters
    project_id = data.get('projectId')
    category_schema = data.get('categorySchema')
    logger = data.get('logger')
    api_key = data.get('apiKey')

    # Check whether class mapping is done or not
    if len(category_schema) == 0:
        return "Please complete class mapping!"

    sdk = SDK(api_key=api_key, host=HOST)

    # Get assets of the project
    # get_assets(project_id) returns only 10 assets. For more information check Ango SDK Documentation:
    # https://docs.ango.ai/sdk/sdk-documentation#get_assets-project_id-asset_id-external_id-page-limit
    get_assets_response = sdk.get_assets(project_id)
    asset_list = get_assets_response['data']['assets']

    # Add a dummy bounding-box to every asset
    schema_id = category_schema[0]['schemaId']  # Get schema_id of the first class
    annotation_json_list = []
    for asset in asset_list:
        # model
        external_id = asset['externalId']
        annotation_json = {"externalId": external_id,
                           "objects": [{"schemaId": schema_id,
                                        "bounding-box": {"x": 20, "y": 30, "width": 50, "height": 60}}]}
        annotation_json_list.append(annotation_json)

    # Import labels via SDK
    sdk.import_labels(project_id, annotation_json_list)
    return "All annotations are imported!"


if __name__ == "__main__":
    plugin = BatchModelPlugin(id=PLUGIN_ID,
                              secret=PLUGIN_SECRET,
                              callback=run_model)

    run(plugin, host=HOST)
