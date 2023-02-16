# Source from https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/containerengine_node_pool

resource "oci_containerengine_node_pool" "oke-node-pool" {
    # Required
    cluster_id = oci_containerengine_cluster.oke-cluster.id
    compartment_id = oci_identity_compartment.tf-compartment.id
    kubernetes_version = "v1.25.4"
    name = "pool1"
    node_config_details{
        placement_configs{
            availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
            subnet_id = oci_core_subnet.vcn-private-subnet.id
        } 
#        placement_configs{
#            availability_domain = data.oci_identity_availability_domains.ads.availability_domains[1].name
#            subnet_id = oci_core_subnet.vcn-private-subnet.id
#        }
#         placement_configs{
#            availability_domain = data.oci_identity_availability_domains.ads.availability_domains[2].name
#            subnet_id = oci_core_subnet.vcn-private-subnet.id
#        }
#        size = 3
        size = 1
    }
    node_shape = "VM.Standard3.Flex"

    # Using image Oracle-Linux-7.x-<date>
    # Find image OCID for your region from https://docs.oracle.com/iaas/images/ 
    node_source_details {
         image_id = "ocid1.tenancy.oc1..*****"
         source_type = "image"
    }
 
    # Optional
    initial_node_labels {
        key = "name"
        value = "tf-cluster"
    }    
}
