Prerequisite:
- Create secret in AWS Secrets Manager
  ```bash
  aws --region "$REGION" secretsmanager  create-secret --name MySecret --secret-string '{"username":"memeuser", "password":"hunter2"}'
  ```
1. Create IAM role for IRSA
  - Create the policy
    ```json
    POLICY_ARN=$(aws --region "$REGION" --query Policy.Arn --output text iam create-policy --policy-name "http-echo-irsa" --policy-document '{
      "Version": "2012-10-17",
      "Statement": [ {
        "Effect": "Allow",
        "Action": ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
        "Resource": ["arn:aws:secretsmanager:eu-west-1:691629053862:secret:MySecret-FWTvzp"]
      } ]
    }')
    ```
  - Create the role with following `Trust policy`
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": "arn:aws:iam::691629053862:oidc-provider/oidc.eks.eu-west-1.amazonaws.com/id/19810D0C13285E0A27C566D67952D2C2"
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "oidc.eks.eu-west-1.amazonaws.com/id/19810D0C13285E0A27C566D67952D2C2:sub": "system:serviceaccount:http-echo:http-echo",
                        "oidc.eks.eu-west-1.amazonaws.com/id/19810D0C13285E0A27C566D67952D2C2:aud": "sts.amazonaws.com"
                    }
                }
            }
        ]
    }
    ```
2. Edit the SA


```bash
kubectl debug -n http-echo -it http-echo-6cf96f5686-rgjms --target=http-echo --image=ubuntu
```