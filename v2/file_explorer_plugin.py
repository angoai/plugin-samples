import boto3 as boto3
from ango.sdk import SDK
from ango.plugins import FileExplorerPlugin, run


HOST = '<YOUR HOST>'
PLUGIN_ID = '<YOUR PLUGIN ID>'
PLUGIN_SECRET = '<YOUR PLUGIN SECRET>'


PAGE_SIZE = 50


def sample_callback(**data):
    # Extract input parameters
    bucket = data.get("bucket")
    folder = data.get("folder", "")
    files = data.get("files", None)
    upload = data.get("upload", False)
    project_id = data.get("projectId", None)
    integration_id = data.get("integrationId", None)
    scroll_token = data.get("scrollToken", None)
    api_key = data.get("apiKey")
    logger = data.get("logger")

    logger.info("Plugin session is started!")

    sdk = SDK(api_key=api_key, host=HOST)
    integration = sdk.get_integrations(integration_id)

    region = integration.get("region")

    client = boto3.client('s3', region_name=region, aws_access_key_id=integration.get("publicKey"),
                          aws_secret_access_key=integration.get("privateKey"))
    s3paginator = client.get_paginator('list_objects')

    path = folder

    if upload:
        page_iterator = s3paginator.paginate(Bucket=bucket,
                                             Prefix=path,
                                             Delimiter='/',
                                             PaginationConfig={'PageSize': 1000})
        files_to_upload = []
        if files:
            for key in files:
                url = "https://%s.s3.%s.amazonaws.com/%s" % (bucket, region, key)
                files_to_upload.append({"data": url, "externalId": key})
        else:
            for page in page_iterator:
                for content in page.get("Contents", []):
                    key = content["Key"]
                    if key[-1] != "/":
                        url = "https://%s.s3.%s.amazonaws.com/%s" % (bucket, region, key)
                        files_to_upload.append({"data": url, "externalId": key})
        response = sdk.upload_files_cloud(project_id=project_id, assets=files_to_upload, integration_id=integration_id)
        logger.info("Plugin session is ended!")
        if response.get("status", "") == "success":
            return str(len(files_to_upload)) + ' assets are uploaded!'
        else:
            return 'Error: ' + str(response)

    else:
        page_iterator = s3paginator.paginate(Bucket=bucket,
                                             Prefix=path,
                                             Delimiter='/',
                                             PaginationConfig={'PageSize': PAGE_SIZE, 'StartingToken': scroll_token})

        folders = []
        files = []
        page_iter = iter(page_iterator)
        page = next(page_iter)
        new_scroll_token = None
        files_page = page.get("Contents", [])
        folders_page = page.get("CommonPrefixes", [])
        if files_page is not None:
            for content in files_page:
                key = content["Key"]
                if key[-1] != "/":
                    files.append(key)
            if len(files_page) == PAGE_SIZE:
                new_scroll_token = page.get("Contents", [{}])[-1].get("Key", None)

        if folders_page is not None:
            for content in folders_page:
                key = content["Prefix"]
                folders.append(key)

        return {"folders": folders, "files": files, "scrollToken": new_scroll_token, "success": True}


if __name__ == "__main__":
    plugin = FileExplorerPlugin(id=PLUGIN_ID,
                                secret=PLUGIN_SECRET,
                                callback=sample_callback)
    run(plugin, host=HOST)
