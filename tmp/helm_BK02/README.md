# README


## Prerequisite:
1. Create secret in AWS Secrets Manager
  ```bash
  aws --region "$REGION" secretsmanager  create-secret --name MySecret --secret-string '{"username":"memeuser", "password":"hunter2"}'
  ```
2. Create IAM role for IRSA
  - Create the IAM policy
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
  - Create the IAM role (with following `Trust policy` and above policy)
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
    ```bash
    aws iam get-role --role-name "http-echo-irsa"
    ```
3. Edit the SA accordingly with IAM role `arn`

4. Test
```bash
kubectl exec -it -n http-echo $(kubectl get pods -n http-echo | awk '/http-echo/{print $1}' | head -1) -- cat /mnt/secrets-store/MySecret; echo
kubectl debug -n http-echo -it $(kubectl get pods -n http-echo | awk '/http-echo/{print $1}' | head -1) --target=http-echo --image=ubuntu
```

