~~~
{
    "id": "how_to_parse_complete_routed_space_dns_lookup",
    "visibility": "public",
    "name": "How to parse dataset complete routed-space dns lookup?",
    "description": "",
    "links": [{
        "to": "dataset:complete_dns_lookups_dataset"
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
The solution parse the dataset [Complete Routed-Space DNS Lookups](https://www.caida.org/data/active/complete_dns_lookups_dataset.xml) and return the data in dictionary format.

## **<ins> Solution </ins>**

The full script could be found in `parse_dns_lookup.py` and  download dataset `complete routed-space dns lookup` [here](https://www.caida.org/data/active/dns_lookups_dataset_request.xml)\
**Usage:** `python parse_dns_lookup.py -d <dataset>`
- `-d`: *(Required)* Input dataset. Note that the script only supports dataset in  `.bz2` format.  

Below is the method used to parse the dataset.   
~~~python 
def parse_bz2(directory):
    data = {} # return data
    fields = [] # fields of data

    # determine the fields of the data
    filename = directory.split('/')[-1]
    if 'ptr' in filename:
        fields  = ['timestamp', 'IP_address', 'hostname']
    elif 'soa' in filename:
        fields = ['timestamp', 'IP_address', 'name', 'ns', 'mbox', 'serial', 'refresh', 'retry', 'expire', 'ttl']
    
    # parse .bz2 file
    with bz2.open(directory, mode='r') as f:
        for line in f:
            line = line.decode().strip().split()
            for i, field in enumerate(fields):
                data[field] = line[i]
            print(data)
~~~
Example of return data
~~~
# PTR
    {
        'timestamp': '1537482068',
        'IP_address': '192.172.226.123',
        'hostname': 'cider.caida.org'
    }

# SOA
    {
        'timestamp': '1537482068',
        'IP_address': '192.172.226.123',
        'name': '226.172.192.in-addr.arpa.',
        'ns': 'caida.org.',
        'mbox': 'postmaster.caida.org.',
        'serial': '201808220',
        'refresh': '86400',
        'retry': '300',
        'expire': '3600000',
        'ttl': '86400'
    }
~~~
 
##  **<ins> Background </ins>**

### Dataset ###
####  Complete Routed-Space DNS Lookups
We performed the lookups using one of two tools. For older datasets, we used a custom parallel DNS lookup tool based on libunbound, a component of the Unbound validating, recursive, caching DNS resolver. For newer datasets, beginning with 2018-08-23, we use zdns in iterative mode. To determine routed addresses, we use BGP tables collected by RIPE and RouteViews via BGPstream. Lookups of the full routed space take 2-3 weeks to complete.

In the 2014-08-22 dataset, we queried 2.7 billion addresses in 10.6 million /24 prefixes (for this particular dataset, we did not query the .0 and .255 addresses in each /24, but all future datasets will query these as well).


- More information and download dataset [here](https://www.caida.org/data/active/complete_dns_lookups_dataset.xml)


### File Format
There are two kinds of file format.

#### PTR files
PTR files contain one PTR record  per line, with the following
fields separated by tabs:
~~~
timestamp   IP_address       hostname
1537482068  192.172.226.123  cider.caida.org
~~~
- The timestamp indicates when we obtained the DNS result.

- In datasets prior to 2018-08-23, we lowercase the hostnames of successful results, and use uppercase characters to indicate lookup errors.  Here are some examples of errors:

  - FAIL.NON-AUTHORITATIVE.in-addr.arpa
  - FAIL.SERVER-FAILURE.in-addr.arpa
  - FAIL.TIMEOUT.in-addr.arpa

- In datasets starting with 2018-08-23, we leave the case of hostnames alone,
since they provide useful information.  We also no longer use the special
FAIL. .in-addr.arpa hostnames; we simply leave out any failed lookups from
the dataset files.

### SOA files

SOA files contain one SOA record per line, with the following fields separated by tabs: 
~~~
timestamp   IP_address       name                      ns          mbox                   serial     refresh  retry  expire   ttl
1537482068  192.172.226.123  226.172.192.in-addr.arpa. caida.org.  postmaster.caida.org.  201808220  86400    300    3600000  86400
~~~
where
| Field    | Description |
|------------|-------------|
|  ns        | Primary name server for the domain |
|  mbox      | Responsible party for the domain |
|  serial    | timestamp of the domain" (changes whenever you update your domain) |
|  refresh   | number of seconds before the zone should be refreshed | 
|  retry     | number of seconds before a failed refresh should be retried |
|  expire    | upper limit (seconds) before a zone is considered no longer authoritative |
|  ttl       | negative result time to live (TTL) |




