from aws_cdk import (
    core as cdk,
    aws_lambda,
    aws_apigateway
)
import json


class DocumentingApiGatewayCdkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        document_version = 'v1'

        handler = aws_lambda.Function(self, "ExampleFunction",
                                            runtime=aws_lambda.Runtime.PYTHON_3_7,
                                            code=aws_lambda.Code.from_asset(
                                                "documenting_api_gateway_cdk/resources"),
                                            handler="app.lambda_handler"
                                      )
        api = aws_apigateway.RestApi(self, "documenting-api",
                                     rest_api_name="Documenting API",
                                     description="This is a example API")

        aws_apigateway.CfnDocumentationPart(self, f"{construct_id}-Doc1",
                                            location=aws_apigateway.CfnDocumentationPart.LocationProperty(
                                                method='POST',
                                                path='/',
                                                type='METHOD'
                                            ),
                                            properties=json.dumps({
                                                'description': 'Method that returns a hello world'
                                            }),
                                            rest_api_id=api.rest_api_id)
        aws_apigateway.CfnDocumentationPart(self, f"{construct_id}-Doc2",
                                            location=aws_apigateway.CfnDocumentationPart.LocationProperty(
                                                method='POST',
                                                path='/',
                                                type='REQUEST_BODY'
                                            ),
                                            properties=json.dumps({
                                                'description': 'Body with a foo attribute'
                                            }),
                                            rest_api_id=api.rest_api_id)

        aws_apigateway.CfnDocumentationVersion(
            self, 'document-version', documentation_version=document_version, rest_api_id=api.rest_api_id)

        fooRequestModel = api.add_model('FooRequest', schema={
            "title": "FooRequest",
            "type": aws_apigateway.JsonSchemaType.OBJECT,
            "required": ["foo"],
            "properties": {
                "foo": {"type": aws_apigateway.JsonSchemaType.STRING}
            }
        })

        messageModel = api.add_model('MessageResponse', schema={
            "title": "MessageResponse",
            "type": aws_apigateway.JsonSchemaType.OBJECT,
            "properties": {
                "message": {"type": aws_apigateway.JsonSchemaType.STRING}
            }
        })

        request_validator = aws_apigateway.RequestValidator(
            self, 'request_validator', rest_api=api, validate_request_body=True)

        lambda_integration = aws_apigateway.LambdaIntegration(
            handler, request_templates={"application/json": '{ "statusCode": "200" }'})
        api.root.add_method("POST", lambda_integration,
                            request_validator=request_validator,
                            request_models={
                                'application/json': fooRequestModel
                            },
                            method_responses=[
                                aws_apigateway.MethodResponse(
                                    status_code="200",
                                    response_models={
                                        'application/json': messageModel
                                    }
                                )
                            ])
