~~~json
{
    "name": "Parse CAIDA's ITDK for a router's IPs, ASN, neighbors, and geographic location.",
    "description":"Using the ASN's organizatoin's country in WHOIS to map an ASN to the country of it's headquarters.",
    "links": ["dataset:AS_Organization"],
    "tags": [
        "measurement methodology",
        "topology",
        "software/tools",
        "ASN",
        "geolocation"
    ]
}
~~~


## **<ins> Introduction </ins>**

This solution parses through ITDK datasets and stores a node's `node id`, `isp`, `asn` and `location` as a json object. \
The relevant `node` information is extracted from 4 different files: \
• `node id` and `isp` from **nodes.bz2** \
• `asn` from **nodes.as.bz2** \
• `neighbors` from **links.bz2** \
• `location` from **nodes.geo.bz2**


## **<ins> Solution </ins>**
The following script combines the information across the four files into a dictionary of nodes with the following structure:
~~~json
{
    "id":4,
    "asn":123,
    "isp":["12.3.34"],
     "neighbors":{"3,2,3"},
    "location":{
        "continent":"SA",
        "country":"CO",
        "region":"34",
        "city": "Bogota"
     },
     "links": [
        {"to":"dataset:internet_topology_data_kit"}
    ]
}
~~~


**usage**: `parse_ark.py -n nodes.bz2 -l links.bz2 -a nodes.as.bz2 -g nodes.geo.bz2`

~~~python
import argparse
import bz2
import socket
import struct

parser = argparse.ArgumentParser()
parser.add_argument('-n', dest = 'node_file', default = '', help = 'Please enter the file name of Nodes File')
parser.add_argument('-l', dest = 'link_file', default = '', help = 'Please enter the file name of Links File')
parser.add_argument('-a', dest = 'nodeas_file', default = '', help = 'Please enter the file name of Node-AS File')
parser.add_argument('-g', dest = 'geo_file', default = '', help = 'Please enter the file name of Node_Geolocation File')
args = parser.parse_args()

# create dictionary
nodes = {}
MASK_8 = struct.unpack("!I", socket.inet_aton("255.0.0.0"))[0]
PREFIX_224 = struct.unpack("!I", socket.inet_aton("224.0.0.0"))[0]
MASK_3 = PREFIX_224
PREFIX_0 = struct.unpack("!I", socket.inet_aton("0.0.0.0"))[0]

def node_lookup(nid):
    """
    To check whether nid is in the ndoes.
    If not, create one in nodes.

    param: string, input node id
    """
    if nid not in nodes:
        nodes[nid] = {
            "id": "",
            "asn": "",
            "isp": [],
            "neighbors": set(),
            "location": {
                "continent": "",
                "country": "",
                "region": "",
                "city": ""
                }
        }
    return nodes[nid]

def placeholder_lookup(addr):
    """
    To check whether the node is a placeholder or not
    If the addr is in 224.0.0.0 or 0.0.0.0, then it is a placeholder

    param:
    addr: string, input IPv4 addresss
    """
    binary_addr = struct.unpack("!I", socket.inet_aton(addr))[0]

    if (binary_addr & MASK_3) != PREFIX_224 and (binary_addr & MASK_8) != PREFIX_0:    
        return False
    else:
        return True

# === load nodes.bz2 ===
with bz2.open(args.node_file, mode='r') as f:

    for line in f:
    
        # convert byte string to string
        line = line.decode() 

        # skip the comments or the length of line is zero
        if len(line) == 0 or line[0] == "#":
            continue

        value = line.strip(" \n") # remove tailing newline
        value = value.split(" ")
        value[1] = value[1].replace(":", "") # value[1] == nid
             
        # get isp and check whether the node is placeholder
        isp_list = []
        placeholder = False

        for isp in value[2:]:
            if len(isp) == 0:
                continue
            if placeholder_lookup(isp):
                placeholder = True           
            isp_list.append(isp)

        # if the node the not placeholder, then process the node
        if not placeholder:
            node = node_lookup(value[1])
            node['id'] = value[1].replace("N", "")
            node['isp'] = isp_list

# === load nodes.as.bz2 ===
with bz2.open(args.nodeas_file, mode = 'r') as f:
    for line in f:
        line = line.decode()
        value = line.split(" ")

        # if the node is in nodes, assign AS number to each node
        if value[1] in nodes:
            nodes[value[1]]["asn"] = value[2]

# === load nodes.geo.bz2 file ===
with bz2.open(args.geo_file, 'r') as f:
    for line in f:
        line = line.decode()

        # skip over comments
        if len(line) == 0 or line[0] == "#":
            continue

        value = line.split(" ")
        value[1] = value[1].split("\t")
        value[1][0] = value[1][0].replace(":", "")

        # if the node is in nodes, assign geo info to each node
        if value[1][0] in nodes:
            node = nodes[value[1][0]]
            node["location"]["continent"] = value[1][1]
            node["location"]["country"] = value[1][2]
            node["location"]["region"] = value[1][3]
            node["location"]["city"] = value[1][4]     

# === load links.bz2 file ===
with bz2.open(args.link_file, 'r') as f:
    for line in f:
        line = line.decode()

        # skip over comments of the length of line is zero
        if len(line) == 0 or line[0] == "#":
            continue

        value = line.strip(" \n")
        value = value.split(" ")
    
        neighbors = []
        for nid in value[3:]:
            neighbors.append(nid.split(":")[0])

        for nid in neighbors:
            if nid in nodes:
                for n in neighbors:
                
                    #skip its neighbors are the node itself 
                    if nid == n or n not in nodes:
                        continue

                    nodes[nid]["neighbors"].add(n)
                    nodes[n]["neighbors"].add(nid)
~~~

### Placeholder Perl Code ###
This Perl code parse nodes.bz2 file only.
~~~Perl
#! A/opt/local/bin/perl
# Many nodes in the ITDK are placeholder nodes.
# this are the non response hops in the traceroute
#   12.0.0.1  * 123.3.2.3
# We don't know what machine is there, but we know there is a machine between
# 12.0.0.1 and 123.3.2.3.
# In most analysis, we want to ignore placeholders.
# You identify placeholders by their IP addresses.
# Placeholder nodes have reserved IP addresses
# The following Perl code identifies placeholders
use warnings;
use strict;

use Socket qw(PF_INET SOCK_STREAM pack_sockaddr_in inet_aton);


use constant MASK_3 => unpack("N",inet_aton("224.0.0.0"));
use constant PREFIX_224 => MASK_3;
use constant MASK_8 => unpack("N",inet_aton("255.0.0.0"));
use constant PREFIX_0 => unpack("N",inet_aton("0.0.0.0"));

my $nodes_total = 0;
my $placeholder_total = 0;

while (<>) {
    next if (/#/);
    my ($node,$nid,@addrs) = split /\s+/;
    my $placeholder;
    foreach my $addr (@addrs) {
        my $net = inet_aton($addr);
        my $binary = unpack("N", $net);
        if ((($binary & MASK_3) == PREFIX_224)
            || (($binary & MASK_8) == PREFIX_0)) {
            $placeholder = 1;
            last;
        }
    }
    if (not $placeholder) {
        $nodes_total += 1;
    } else {
        $placeholder_total += 1;
    }

    #print ("$not_place_holder_node $nodes_total $placeholder_total\n");
    # Only process the none placeholder nodes
    #last if ($nodes_total > 10);
}

print ("nodes_total: ",$nodes_total,"\n");
print ("placeholder: ",$placeholder_total,"\n");
~~~


## **<ins> Background </ins>**
### Caveats

 #### Placeholder Nodes ###

• Placeholder nodes are the non-response hops in the traceroute. \
• Generally, placeholder nodes are ignored. \
• Placeholder nodes have reserved IP addresses used to identify them. For the ITDK dataset, we use addresses `224.0.0.0` and `0.0.0.0` as the placeholder addresses.


### Explanation of the Data Files ###
*Download ITDK Datasets:* [link](https://www.caida.org/data/request_user_info_forms/ark.xml)

#### midar-iff.nodes.bz2
The nodes file lists the set of interfaces that were inferred to be on each router. \
Each line indicates that a node `node_id` has interfaces i<sub>1</sub> to i<sub>n</sub>. <br/>
**File format**: node <node_id>: &nbsp; <i<sub>1</sub>> &nbsp; <i<sub>2</sub>> &nbsp; ... &nbsp; <i<sub>n</sub>> <br/>
~~~
node N1:  5.2.116.4 5.2.116.28 5.2.116.66 5.2.116.70 5.2.116.78 5.2.116.88 5.2.116.108 5.2.116.142
~~~


#### midar-iff.links.bz2
The links file lists the set of routers and router interfaces that were inferred to be sharing each link. \
Each line indicates that a link `link_id` connects nodes N<sub>1</sub> to N<sub>m</sub>. \
If it is known which router interface is connected to the link, then the interface address is given after the node ID separated by a colon.<br/>
**File format**: link <link_id>: &nbsp; <N<sub>1</sub>>:i<sub>1</sub> &nbsp;  <N<sub>2</sub>>:i<sub>2</sub> &nbsp;  <N<sub>3</sub>>:i<sub>3</sub> &nbsp;  ... &nbsp;  <N<sub>m</sub>>:i<sub>m</sub> <br/>
~~~
link L1: N27677807:1.0.0.1 N106961
~~~


#### midar-iff.nodes.as.bz2
The node-AS file assigns an AS number to each node found in the nodes file.\
**File format**: node.AS   <node_id>   <AS>   <method>
~~~
node.AS N1 31655 refinement
~~~

#### midar-iff.nodes.geo.bz
The node-geolocation file contains the geographic location for each node in the nodes file.\
**File format**: node.geo   <node_id>:   <continent>   <country>   <region>   <city>   <latitude>   <longitude>
~~~
node.geo N4: SA CO 34 Bogota 4.60971 -74.08175       
~~~
    
More information on ITDK dataset can be found [here](https://www.caida.org/data/request_user_info_forms/ark.xml)