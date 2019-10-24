## Automating a claims adjudication workflow using Amazon Textract and Amazon Comprehend Medical

Extract, Validate and Visualize medical claims with Amazon Textract and Comprehend Medical
What Is This?
This is a sample python application to automate the extraction and validation of healthcare claim documents using Amazon Textract and Amazon Comprehend Medical. The goal of this to provide developers the base to enhance the guridiction process, analytics and visualiztion required in processing healthcare claims.

Architecture Diagram
![Alt text](./arch-diagram.png?raw=true "Title")

How To Use This
- Upload sample scanned claim documents to S3 bucket in input folder
- Get Parsed result in S3 bucket's result folder
- Get Comprehend Medical output of Procedure field in S3 bucket's procedureresult folder

Deployment
- Deploy AWS Cloudformation template text-cm.yaml
- Update stack with text-cm-update.yaml

## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.
