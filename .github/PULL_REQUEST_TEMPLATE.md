*Issue #, if available:*

*Description of changes:*

Resource handler returned message: "Policy arn:aws:iam::aws:policy/AWSLambdaFullAccess does not exist or is not attachable. (Service: Iam, Status Code: 404, Request ID: 994d21a0-31f1-4d9f-93b5-3459d4a5da72)" (RequestToken: 9d8d7b74-7bd2-2a52-d1af-b3117cf09e5d, HandlerErrorCode: NotFound)
-- It is because this policy is deprecated , hence updated with this one
 
 
Resource handler returned message: "The runtime parameter of python3.7 is no longer supported for creating or updating AWS Lambda functions. We recommend you use the new runtime (python3.12) while creating or updating functions. (Service: Lambda, Status Code: 400, Request ID: 072e0796-1093-4b3e-9d04-69bcbf6fdac7)" (RequestToken: 839f9462-6bf6-b3c0-e2ef-80f2762c457c, HandlerErrorCode: InvalidRequest)
-- It no longer supports 3.7, hence updated with 3.9. It will be great if the allowed list is updated with the latest python supported version in cfn-list
 
Resource handler returned message: "Error occurred while GetObject. S3 Error Code: NoSuchKey. S3 Error Message: The specified key does not exist. (Service: Lambda, Status Code: 400, Request ID: 496487ad-7f64-4dff-91b9-c904b6078cfd)" (RequestToken: 4d6a74ec-827e-4124-6357-7165c0227ef8, HandlerErrorCode: InvalidRequest)
-- This is because it was trying to create PARSE, QUEUE and VALIDATE before custom lambda execution was completed. This resulted in not having those 3 zips in place for respective lambda function to pick up. I have added DependsOn for each one of them.

By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of your choice.
