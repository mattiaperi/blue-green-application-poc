# blue-green-poc
- https://medium.com/adfolks/how-to-give-permission-to-aws-code-build-to-access-eks-cluster-using-a-role-25ca7be73993
- https://www.stacksimplify.com/aws-eks/aws-devops-eks/learn-to-master-devops-on-aws-eks-using-aws-codecommit-codebuild-codepipeline/
- 

1. create Role for CodeBuild `arn:aws:sts::691629053862:assumed-role/codebuild-http-echo-service-role/AWSCodeBuild-387415a4-40ec-43cb-83cb-a51ea8de340c`
   1. `AmazonEC2ContainerRegistryPowerUser`
   2. 


The last phase of the deployment is the upgrade of the cluster thanks to the `helm upgrade` command. Thus, the CodeBuild process needs to be able to access the Kubernetes cluster. To do so, modify the `aws-auth` configMap with the command `kubectl edit -n kube-system configmap/aws-auth` and add the following lines below the `mapUsers` key:
- userarn: arn:aws:iam::<AWS_ACCOUNT_ID>:role/<ROLE_NAME>
  username: <ROLE_NAME>
  groups:
    - system:masters
view raw
aws-auth.yaml hosted with ❤ by GitHub

You’re ready to launch your first deploy, either by pushing new code to the Git branch or by triggering from your terminal `aws codepipeline start-pipeline-execution --name deploy-<ENV>`.


apiVersion: v1
kind: Pod
metadata:
  name: busybox
  namespace: default
spec:
  containers:
  - image: busybox
    command:
      - sleep
      - "3600"
    imagePullPolicy: IfNotPresent
    name: busybox
  restartPolicy: Always


# Accesso CodeBuild to EKS

## 1. Creo lo IAM ROLE con la trust policy che il mio ruolo Codebuild può assumere con sts::AssumeRole
```bash
CODEBUILDROLE_ARN="arn:aws:iam::691629053862:role/service-role/codebuild-http-echo-service-role"
TRUST_POLICY="{ \"Version\": \"2012-10-17\", \"Statement\": [ { \"Effect\": \"Allow\", \"Principal\": { \"AWS\": \"${CODEBUILDROLE_ARN}\" }, \"Action\": \"sts:AssumeRole\" } ] }"
echo ${TRUST_POLICY}
ASSUMEROLE_ARN=$(aws iam create-role --role-name "AAAPLEASEDELETEME2" --assume-role-policy-document "${TRUST_POLICY}" --output text --query 'Role.Arn')
```
>>>  FATTO arn:aws:iam::691629053862:role/AAAPLEASEDELETEME2

## 2. Configure `aws-auth` per dire a EKS che il mio ruolo può fare tutte cose su Kubernetes
```bash
ROLE="    - rolearn: ${ASSUMEROLE_ARN}\n      username: build\n      groups:\n        - system:masters"
kubectl get -n kube-system configmap/aws-auth -o yaml | awk "/mapRoles: \|/{print;print \"${ROLE}\";next}1" > /tmp/aws-auth-patch.yml
kubectl patch configmap/aws-auth -n kube-system --patch "$(cat /tmp/aws-auth-patch.yml)"
```

>>> E QUI INVECE HO MESSO L'ARN DEL ROLE DELLA MIA CODEPIPELINE

## 3. Create a Policy and attach to CodeBuild Service Role, to perform STS:assumerole and permission to READ in EKS:* to the role created in step 1

```json
        {
            "Sid": "EKS",
            "Effect": "Allow",
            "Action": [
                "eks:*"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "STSASSUME",
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "${ASSUMEROLE_ARN}"
        }
```


## 4. Using aws eks update-kubeconfig with the argument — role-arn <Role created in step1>, you will be able to authenticate in the EKS cluster