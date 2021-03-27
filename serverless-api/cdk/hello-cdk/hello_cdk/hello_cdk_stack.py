from aws_cdk import (
    core as cdk,
    aws_lambda,
    aws_apigateway
)


class HelloCdkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        handler = aws_lambda.Function(self, "WidgetHandler",
                                      runtime=aws_lambda.Runtime.PYTHON_3_7,
                                      code=aws_lambda.Code.from_asset(
                                          "hello_cdk/resources"),
                                      handler="hello_world.lambda_handler"
                                      )

        api = aws_apigateway.RestApi(self, "widgets-api",
                                     rest_api_name="Widget Service",
                                     description="This service serves widgets.")

        get_widgets_integration = aws_apigateway.LambdaIntegration(
            handler, request_templates={"application/json": '{ "statusCode": "200" }'})

        api.root.add_method("GET", get_widgets_integration)
