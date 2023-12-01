# AWS LightSail Deployment

<h2>Prerequisites</h2>

1. Download and Install Docker for your Operating System [[Reference](https://docs.docker.com/get-docker/)]
2. Download and Install AWS-CLI [[Reference](https://lightsail.aws.amazon.com/ls/docs/en_us/articles/amazon-lightsail-install-software)]
3. Create AWS IAM credentials (Skip if you already have) [[Reference](https://lightsail.aws.amazon.com/ls/docs/en_us/articles/amazon-lightsail-managing-access-for-an-iam-user)]
4. Configure you AWS CLI [[Reference](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)]


<h2>Deployment Steps</h2>

1. <h3>Create Your Lightsail Container Service</h3>
    Complete the following procedure to create a Lightsail container service.
    1. Sign in to the Lightsail console. 
    2. On the Lightsail home page, choose the Containers tab. 
    3. Choose Create container service. 
    4. In the Create a container service page, choose Change AWS Region, then choose an AWS Region for your container service.
    5. Choose a capacity for your container service. For more information, see the Container service capacity (scale and power) section of this guide.

2. <h3>Build Your Plugin as Docker Image</h3>
    > docker build -t <IMAGE-NAME> .

3. <h3>Upload Your image to Lightsail</h3>
    > aws lightsail push-container-image --region <YOUR_REGION> --service-name <YOUR_SERVICE_NAME> --label <IMAGE_NAME> --image <IMAGE_NAME>:latest

    Using eu-central-1 (frankfurt) region is recommended.
    Example:
    > aws lightsail push-container-image --region eu-central-1 --service-name test-plugin --label plugin --image plugin:latest

4. <h3> Deploy Your Image </h3>
   
    1. Choose Create a deployment. 
    2. Specify a custom deployment – Choose your docker image to create a deployment.
    3. The deployment form view opens, where you can enter new deployment parameters such as environment variables.
    4. Enter the parameters of your deployment. For more information about the deployment parameters that you can specify, see the Deployment parameters section in the Creating and managing deployments for your Amazon Lightsail container services guide.
    5. Choose Add container entry to add more than one container entry to your deployment.
    When you're done entering the parameters of your deployment, choose Save and deploy to create the deployment on your container service.