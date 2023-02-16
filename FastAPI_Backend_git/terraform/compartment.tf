
resource "oci_identity_compartment" "tf-compartment" {
    # Required
    compartment_id = "ocid1.tenancy.oc1..*****"
    description = "Compartment for Terraform resources."
    name = "tf-infra"
}
