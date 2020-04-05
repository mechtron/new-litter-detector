variable "aws_region" {
  description = "The AWS region"
}

variable "environment" {
  description = "The service's environemnt"
}

variable "function_name" {
  description = "The Lambda function's name"
  default     = "new-litter-detector"
}

variable "repo_root_path" {
  description = "The hard path of this repository"
}
