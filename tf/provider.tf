provider "aws" {
  region = local.region
  # profile = var.profile

  default_tags {
    tags = {
      "org:cluster"     = local.cluster_name
      "org:finops"      = local.cluster_name
      "org:environment" = local.cluster_environment
      "org:provider"    = "tf"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks_blueprints.eks_cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks_blueprints.eks_cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.this.token
}

provider "helm" {
  kubernetes {
    host                   = module.eks_blueprints.eks_cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks_blueprints.eks_cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.this.token
  }
}
