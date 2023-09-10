import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import { MoneybookS3Stack } from "./stack/s3-stack";
import { MoneybookLambdaStack } from "./stack/lambda-stack";
import { Account } from "./config/accounts";
import { SYSTEM_NAME } from "./config/commons";

export interface MoneybookStackProps extends cdk.StackProps {
  context: Account;
  s3Stack?: MoneybookS3Stack;
}

export class MoneybookStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: MoneybookStackProps) {
    super(scope, id, props);

    const s3Stack = new MoneybookS3Stack(this, `${SYSTEM_NAME}-s3Stack`, props);
    props.s3Stack = s3Stack;

    new MoneybookLambdaStack(this, `${SYSTEM_NAME}-lambdaStack`, props);
  }
}
