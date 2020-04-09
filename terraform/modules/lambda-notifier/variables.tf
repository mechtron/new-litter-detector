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

variable "twilio_account_sid" {
  description = "Your Twilio account SID"
}

variable "twilio_auth_token" {
  description = "Your Twilio auth token"
}

variable "twilio_from_number" {
  description = "The Twilio phone number you want to use to make phone call alerts"
}
