import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import { getAccountUniqueName } from "../config/accounts";
import { MoneybookStackProps } from "../moneybook-stack";
import { SYSTEM_NAME } from "../config/commons";
import { PythonFunction } from "@aws-cdk/aws-lambda-python-alpha";
import { Runtime } from "aws-cdk-lib/aws-lambda";
import * as path from "path";
import {
  ManagedPolicy,
  Role,
  ServicePrincipal,
  CompositePrincipal,
} from "aws-cdk-lib/aws-iam";

export class MoneybookLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: MoneybookStackProps) {
    super(scope, id, props);

    const lambdaRole = new Role(this, `${SYSTEM_NAME}-lambda-role`, {
      roleName: `${getAccountUniqueName(props.context)}-lambda-role`,
      assumedBy: new CompositePrincipal(
        new ServicePrincipal("lambda.amazonaws.com")
      ),
      managedPolicies: [
        ManagedPolicy.fromAwsManagedPolicyName(
          "service-role/AWSLambdaBasicExecutionRole"
        ),
        ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess"),
      ],
    });

    new PythonFunction(this, `${SYSTEM_NAME}-create-file`, {
      functionName: `${getAccountUniqueName(props.context)}-create-file`,
      handler: "lambda_handler",
      entry: path.join(__dirname, "../../../app/backend/create-file"),
      index: "create_file.py",
      runtime: Runtime.PYTHON_3_10,
      role: lambdaRole,
      environment: {
        BUCKET_NAME: props.s3Stack!.bucket.bucketName,
      },
    });

    new PythonFunction(this, `${SYSTEM_NAME}-read-file`, {
      functionName: `${getAccountUniqueName(props.context)}-read-file`,
      handler: "lambda_handler",
      entry: path.join(__dirname, "../../../app/backend/read-file"),
      index: "read_file.py",
      runtime: Runtime.PYTHON_3_10,
      role: lambdaRole,
      environment: {
        BUCKET_NAME: props.s3Stack!.bucket.bucketName,
      },
    });
  }
}
