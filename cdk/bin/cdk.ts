import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { MoneybookStack } from "../lib/moneybook-stack";
import { getAccountUniqueName, getDevAccount } from "../lib/config/accounts";

const app = new cdk.App();

if (process.env.USER !== undefined) {
  const devAccount = getDevAccount(process.env.USER);
  if (devAccount !== undefined) {
    new MoneybookStack(app, `${getAccountUniqueName(devAccount)}`, {
      env: devAccount,
      context: devAccount,
    });
  }
}

app.synth();
