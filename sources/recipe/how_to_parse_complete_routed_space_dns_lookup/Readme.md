~~~
{
    "id": "how_to_parse_complete_routed_space_dns_lookup",
    "visibility": "public",
    "name": "How to parse complete routed space dns lookup?",
    "description": "",
    "links": [{
        "to": "dataset:"
        }],
    "tags": [
        "",
        "ASN",
        "topology",
        "geolocation"
    ]
}
~~~
## **<ins> Introduction </ins>**
The solution parse the data .

## **<ins> Solution </ins>**

The full script could be found in `parse_peeringdb.py` \
**Usage:** `python `
- `-d`: *(Required)* Input dataset. Note that the script only supports dataset in `.sqlite` and `.json` format.
- `-get`: *(Required)* Type of the objects that you would like to retrieve 
- `-id`: *(Optional)* Id of the single object that you would like to retrieve 

Below are the methods used to read and parse data in `.json` file.   
~~~python 


~~~
Below are the methods used to read and parse data in `.sqlite` file.   
~~~python 

~~~

 
##  **<ins> Background </ins>**

### Dataset ###
#### 


#### Objects type in datasets

- Objects type in `.json` dataset:
- [PeeringDB API](https://www.peeringdb.com/apidocs/)

| Object     | Description |
|------------|-------------|
|  ix        |   Internet Exchange Point: the physical infrastructure through which Internet service providers (ISPs) and content delivery networks (CDNs) exchange Internet traffic between their networks |
|  fac       | Facility (Datacenter): a physical location where the IX has infrastructure, a single IX may have multiple facilities |
|  org       | Organization |
|  poc       | Network Point of Contact | 
|  net       | Network: network information |
|  ixfac     | Internet Exchange / Facility presence: combines facility and ix information |
|  ixlan     | Internet Exchange Network Information: abstraction of the physical ix |
|  ixpfx     | Internet Exchange Prefix: IPv4 / IPv6 range used on an ixlan |
|  netfac    | Network / Facility presence: combines net and facility information |
|  netixlan  | Network to Internet Exchange connection: combines ix and net information |

- Objects type in `.sqlite` dataset: 

| Object     | Description |
|------------|-------------|    
|  mgmtFacilities           |  Facility |
|  mgmtPublic               |  Internet Exchange Point|
|  mgmtPublicsFacilities    |  Internet Exchange / Facility presence: similar to combine facility and ix information |
|  mgmtPublicsIPs           |  IP address of Publics| 
|  peerParticipants         |  Network |
|  peerParticipantsContacts |  Network Point of Contact  |
|  peerParticipantsPrivates |  Internet Exchange Network Information: abstraction of the physical ix |
|  peerParticipantsPublics  |  Network to Internet Exchange connection: similar to combine ix and net information |


### sqlite3



