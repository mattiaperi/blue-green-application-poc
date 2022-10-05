# Brief overview

## How it works
Similar to Kubernetes secrets, on pod start and restart, the Secrets Store CSI driver communicates with the provider using gRPC to retrieve the secret content from the external Secrets Store specified in the `SecretProviderClass` custom resource. Then the volume is mounted in the pod as tmpfs and the secret contents are written to the volume.

On pod delete, the corresponding volume is cleaned up and deleted.

See also: https://innablr.com.au/blog/what-is-secret-management-and-how-to-integrate-with-k8s-part-2/

## Repositories and helm charts
They are two different charts for two different software that both serve to integrate AWS Secret Managers with EKS.
1. The *driver*: `secrets-store-csi-driver`                 - maintained by Kubernetes SIG Auth
   - https://secrets-store-csi-driver.sigs.k8s.io/introduction.html
   - https://secrets-store-csi-driver.sigs.k8s.io/troubleshooting.html#common-errors
2. The *provider*: `secrets-store-csi-driver-provider-aws`  - maintained by AWS.
    - https://secrets-store-csi-driver.sigs.k8s.io/providers.html
    - https://github.com/kubernetes-sigs/secrets-store-csi-driver/blob/main/docs/book/src/concepts.md#provider-for-the-secrets-store-csi-driver
    - NB: secrets-store-csi-driver chart is a dependency

Github repository:
1. https://github.com/kubernetes-sigs/secrets-store-csi-driver
2. https://github.com/aws/secrets-store-csi-driver-provider-aws/

Helm charts:
1. https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts/
2. https://github.com/aws/eks-charts/tree/master/stable/csi-secrets-store-provider-aws

## Considerations:
- Secrets sizing
  - AWS SSM parameter store is not an option because secrets are limited in size (4Kb)
  - AWS Secrets manager supports larger secret size: *must have length less than or equal to 65536*
    - https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_CreateSecret.html
    - https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
  - Secret file shared by Diana was ~7KB (6505 bytes)
- Secrets auditing
  - Cloudtrail: `aws cloudtrail lookup-events --region "eu-west-1" --lookup-attributes AttributeKey=EventSource,AttributeValue=secretsmanager.amazonaws.com`
- Binaries
  - https://github.com/HariSekhon/DevOps-Bash-tools/blob/master/aws_secret_add_binary.sh
- Network wise
  - both `secrets-store-csi-driver` and `secrets-store-csi-driver-provider-aws` are daemonset, meaning they are consuming 1 vIP per worker node. To keep in mind when we are right sizing network subnets. DaemonSet in `kube-system`:
    - `aws-node`
    - `csi-secrets-store-secrets-store-csi-driver`
    - `ebs-csi-node`
    - `efs-csi-node`
    - `kube-proxy`
    - `secrets-provider-aws-secrets-store-csi-driver-provider-aws`
    - `<LOGS & MENTRICS agent>`

## Outcome:
- Secrets management via `secrets-store-csi-driver`/`secrets-store-csi-driver-provider-aws` relying on *AWS Secrets Manager* is the suggested approach to secrets management











```bash
aws secretsmanager create-secret --name "TOBEDEL" --secret-string file://~/Downloads/secrets.txt

REGION="eu-west-1"
CLUSTERNAME="mattia-tobedel-dev"

# --> CREATE THE SECRET 
# aws --region "$REGION" secretsmanager  create-secret --name MySecret --secret-string '{"username":"memeuser", "password":"hunter2"}'
aws eks list-clusters --region "$REGION" | jq -r '.clusters[]'
aws secretsmanager list-secrets | jq -r '.SecretList[].ARN'

helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
helm install -n kube-system csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver
kubectl --namespace=kube-system get pods -l "app=secrets-store-csi-driver"

helm repo add aws-secrets-manager https://aws.github.io/secrets-store-csi-driver-provider-aws
helm install -n kube-system secrets-provider-aws aws-secrets-manager/secrets-store-csi-driver-provider-aws

POLICY_ARN=$(aws --region "$REGION" --query Policy.Arn --output text iam create-policy --policy-name "nginx-deployment-policy" --policy-document '{
    "Version": "2012-10-17",
    "Statement": [ {
        "Effect": "Allow",
        "Action": ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
        "Resource": ["arn:aws:secretsmanager:eu-west-1:691629053862:secret:prod/maxmara/secret-R1RQl1"]
    } ]
}')

eksctl utils associate-iam-oidc-provider --region="$REGION" --cluster="$CLUSTERNAME" --approve

eksctl create iamserviceaccount --name nginx-deployment-sa --region="$REGION" --cluster "$CLUSTERNAME" --attach-policy-arn "$POLICY_ARN" --approve --override-existing-serviceaccounts
# This will create:
# - create IAM role for serviceaccount "default/nginx-deployment-sa"  --> `aws iam list-roles | grep nginx -B18 -A9`
# - create serviceaccount "default/nginx-deployment-sa"               --> `kubectl get sa -n default nginx-deployment-sa -o yaml`
# ```yaml
# cat << EOF | kubectl apply -f -
# apiVersion: v1
# kind: ServiceAccount
# metadata:
#   labels:
#     app.kubernetes.io/managed-by: me
#   annotations:
#     eks.amazonaws.com/role-arn: arn:aws:iam::691629053862:role/eksctl-mattia-tobedel-dev-addon-iamserviceac-Role1-1R6UR8GGPF2RC
#   name: nginx-deployment-sa
#   namespace: default
# ```

kubectl apply -f https://raw.githubusercontent.com/aws/secrets-store-csi-driver-provider-aws/main/examples/ExampleSecretProviderClass.yaml


POLICY_ARN=$(aws --region "$REGION" --query Policy.Arn --output text iam create-policy --policy-name nginx-deployment-policy --policy-document '{
    "Version": "2012-10-17",
    "Statement": [ {
        "Effect": "Allow",
        "Action": ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
        "Resource": ["arn:aws:secretsmanager:eu-west-1:691629053862:secret:MySecret-FWTvzp"]
    } ]
}')