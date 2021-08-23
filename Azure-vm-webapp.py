#!/usr/bin/env python
# coding: utf-8

# In[2]:


from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os


# In[3]:


from azure.identity import AzureCliCredential
from azure.mgmt.resource import SubscriptionClient

credential = AzureCliCredential()
subscription_client = SubscriptionClient(credential)

subscription_id = next(subscription_client.subscriptions.list())
subs_id = subscription_id.subscription_id
print(subs_id)


# In[4]:


# Step 1: Provision a resource group
resource_client = ResourceManagementClient(credential, subs_id)


# In[33]:


RESOURCE_GROUP_NAME = "PythonAzureExample-VM-rg"
LOCATION = "westus2"


# In[34]:


rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
    {
        "location": LOCATION
    }
)


# In[35]:


print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")


# In[36]:


# Step 2: provision a virtual network
VNET_NAME = "python-example-vnet"
SUBNET_NAME = "python-example-subnet"
IP_NAME = "python-example-ip"
IP_CONFIG_NAME = "python-example-ip-config"
NIC_NAME = "python-example-nic"


# In[37]:


network_client = NetworkManagementClient(credential, subs_id)

# Provision the virtual network and wait for completion
poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {
            "address_prefixes": ["10.0.0.0/16"]
        }
    }
)


# In[38]:


vnet_result = poller.result()


# In[39]:


print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")  


# In[43]:


# step 3: Provision the subnet and wait for completion
poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME, 
    VNET_NAME, SUBNET_NAME,
    { "address_prefix": "10.0.0.0/24" }
)
subnet_result = poller.result()

print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")


# In[44]:


# Step 4: Provision an IP address and wait for completion
poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": { "name": "Standard" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)


# In[45]:


ip_address_result = poller.result()
print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")


# In[46]:


# Step 5: Provision the network interface client
poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
    NIC_NAME, 
    {
        "location": LOCATION,
        "ip_configurations": [ {
            "name": IP_CONFIG_NAME,
            "subnet": { "id": subnet_result.id },
            "public_ip_address": {"id": ip_address_result.id }
        }]
    }
)


# In[47]:


nic_result = poller.result()
print(f"Provisioned network interface client {nic_result.name}")


# In[49]:


# Step 6: Provision the virtual machine
compute_client = ComputeManagementClient(credential, subs_id)

VM_NAME = "ExampleVM"
USERNAME = "azureuser"
PASSWORD = "ChangePa$$w0rd24"


# In[50]:


poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
                                                               {
                                                                   "location": LOCATION,
                                                                   "storage_profile":{
                                                                       "image_reference":{
                                                                           "publisher":'Canonical',
                                                                           "offer":"UbuntuServer",
                                                                           "sku":"16.04.0-LTS",
                                                                           "version":"latest"
                                                                       }
                                                                   },
                                                                   "hardware_profile":{
                                                                       "vm_size":"Standard_DS1_v2"
                                                                   },
                                                                   "os_profile":{
                                                                       "computer_name":VM_NAME,
                                                                       "admin_username":USERNAME,
                                                                       "admin_password":PASSWORD
                                                                   },
                                                                   "network_profile":{
                                                                       "network_interfaces":[{
                                                                           "id":nic_result.id,
                                                                       }]
                                                                   }
                                                               })


# In[51]:


vm_result = poller.result()


# In[52]:


print(f"Provisioned virtual machine{vm_result.name}")


# In[60]:


#------------------------------------Example2-----------------------------------


# In[5]:


import random, os
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClient


# In[6]:


from azure.identity import AzureCliCredential
from azure.mgmt.resource import SubscriptionClient

credential = AzureCliCredential()
subscription_client = SubscriptionClient(credential)

subscription_id = next(subscription_client.subscriptions.list())
subs_id = subscription_id.subscription_id
print(subs_id)


# In[7]:


RESOURCE_GROUP_NAME = 'PythonAzureExample-WebApp-rg'
LOCATION = "centralus"


# In[8]:


# Step 1: Provision the resource group.
resource_client = ResourceManagementClient(credential, subs_id)
rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
    { "location": LOCATION })


# In[9]:


#Step 2: Provision the App Service plan, which defines the underlying VM for the web app.
SERVICE_PLAN_NAME = 'PythonAzureExample-WebApp-plan'
WEB_APP_NAME = os.environ.get("WEB_APP_NAME", f"PythonAzureExample-WebApp-{random.randint(1,100000):05}")


app_service_client = WebSiteManagementClient(credential, subs_id)
poller = app_service_client.app_service_plans.begin_create_or_update(RESOURCE_GROUP_NAME,
    SERVICE_PLAN_NAME,
    {
        "location": LOCATION,
        "reserved": True,
        "sku" : {"name" : "B1"}
    }
)

plan_result = poller.result()

print(f"Provisioned App Service plan {plan_result.name}")


# In[10]:


# Step 3: With the plan in place, provision the web app itself, which is the process that can host
# whatever code we want to deploy to it.

poller = app_service_client.web_apps.begin_create_or_update(RESOURCE_GROUP_NAME,
    WEB_APP_NAME,
    {
        "location": LOCATION,
        "server_farm_id": plan_result.id,
        "site_config": {
            "linux_fx_version": "python|3.8"
        }
    }
)


# In[11]:


web_app_result = poller.result()
print(f"Provisioned web app {web_app_result.name} at {web_app_result.default_host_name}")


# In[12]:


# Step 4: deploy code from github repo
REPO_URL = os.environ["REPO_URL"]

poller = app_service_client.web_apps.begin_create_or_update_source_control(RESOURCE_GROUP_NAME,
    WEB_APP_NAME, 
    { 
        "location": "GitHub",
        "repo_url": "https://github.com/sonianuj287/python-docs-hello-world-1",
        "branch": "master"
    }
)


# In[ ]:



sc_result = poller.result()

print(f"Set source control on web app to {sc_result.branch} branch of {sc_result.repo_url}")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




