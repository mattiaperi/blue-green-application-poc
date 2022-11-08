### This script generate a schema related to the application flow in a ECS Fargate infrastructure
### it use the Diagrams library available in python and graphviz
### For detailed information refer https://diagrams.mingrammer.com/

from diagrams import Diagram, Cluster, Edge
#from urllib.request import urlretrieve
from diagrams.aws.compute import EC2
from diagrams.aws.compute import EC2ContainerRegistry, ECR
from diagrams.aws.compute import ElasticContainerService, ECS
from diagrams.aws.compute import ElasticContainerServiceContainer
from diagrams.aws.compute import ElasticContainerServiceService
from diagrams.aws.compute import Fargate
from diagrams.aws.database import RDS
from diagrams.aws.general import User
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import ElbApplicationLoadBalancer, ALB
from diagrams.aws.network import Route53
from diagrams.aws.storage import ElasticFileSystemEFS, EFS
from diagrams.custom import Custom
from diagrams.elastic.saas import Elastic
from diagrams.k8s.clusterconfig import HPA
from diagrams.k8s.compute import Deployment, Pod, ReplicaSet, StatefulSet
from diagrams.k8s.network import Ingress, Service
from diagrams.k8s.storage import PV, PVC, StorageClass
from diagrams.aws.security import SecretsManager
from diagrams.k8s.rbac import ServiceAccount
from diagrams.aws.security import IdentityAndAccessManagementIamRole, IdentityAndAccessManagementIamPermissions
from diagrams.saas.cdn import Akamai

# with Diagram("Flow", show=False, direction="LR"):
#     dns = Route53("DNS")
#     user = User("Enduser")
#     alb = ElbApplicationLoadBalancer("AppLB")
#     fargate = Fargate("ECS Fargate")
#     ecs_serv = ElasticContainerServiceService("ECS Service")
#     cloudw = Cloudwatch("Cloudwatch Service")
#     ecr = EC2ContainerRegistry("Container Registry")
#     efs = ElasticFileSystemEFS("EFS Persistent Storage")
#     ebs = ElasticFileSystemEFS("EFS Persistent Storage")

# #    pg_url = "https://firebase.google.com/images/integrations/pagerduty.png"
#     pg_icon = "custom_icons/pagerduty.png"
# #    urlretrieve(pg_url, pg_icon)
#     pagerduty = Custom("Pagerduty", pg_icon)

#     with Cluster("Task Definition"):
#         task_1 = ElasticContainerServiceContainer("Container_1")
#         task_2 = ElasticContainerServiceContainer("Container_2")
#         task_3 = ElasticContainerServiceContainer("Container_N")

#     gls = Elastic("GLS")

#     dns << user >> alb >> fargate
#     fargate - ecs_serv >> task_2
#     ecr >> ecs_serv
#     task_2 >> cloudw
#     task_2 - efs
#     cloudw >> gls
#     cloudw >> pagerduty

### Definitions:

with Diagram("Secrets Flow", show=False, direction="LR"):
  akamai = Akamai("Akamai")
  dns = Route53("DNS")
  alb = ElbApplicationLoadBalancer("AppLB")
#   ecr = ElasticContainerServiceService("ECR")
  secret_manager = SecretsManager("SecretsManager")

  with Cluster("IAM"):
    iam_role = IdentityAndAccessManagementIamRole("IAMrole")
    iam_policy = IdentityAndAccessManagementIamRole("IAMpermissions")

  with Cluster("EKS"):
    eks_ingress = Ingress("domain.com")
    eks_service = Service("svc")
    with Cluster("pods"):
      eks_pods    = ([Pod("pod1"),
                      Pod("pod2"),
                      Pod("pod3")])
    eks_rs      = ReplicaSet("rs")
    eks_deploy  = Deployment("dp")
    eks_hpa     = HPA("hpa")
    eks_serviceaccount = ServiceAccount("ServiceAccount")

### Schema:

  net = dns >> alb >> eks_ingress >> eks_service
  akamai >> dns
  net >> eks_pods << eks_rs << eks_deploy << eks_hpa
  eks_pods >> eks_serviceaccount >> iam_role >> iam_policy >> secret_manager 
#   eks_pods >> ecr
  eks_pods >> Edge(label='', color='red') >> secret_manager 
  

