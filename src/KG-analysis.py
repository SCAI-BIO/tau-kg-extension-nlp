# %%
from ebel_rest import connect, query
import pandas as pd

# %%
# Database settings
server = "https://graphstore.scai.fraunhofer.de"
password = 'guest'
user = 'guest'
db_name = "depression_mesh"

# %%
# Connect to database
connect(user, password, server, db_name)

#%% Set condition statement based on  which run set we query
run_num = input("Please select the run number \n")
print("extracting triples from run {}".format(run_num))
condition = "WHERE annotation.ResultSet = '{}'".format(run_num)
# %%
#Unique statement per pmid
bel_triple_pmid_query = "select out.bel as subject, @class as relation, in.bel as object, pmid, evidence from bel_relation {}".format(condition)
results = query.sql(bel_triple_pmid_query).data
print(results)

#%%
#Save all triples in excel

triples = pd.DataFrame(data = results)
print(triples)
triples.to_excel('triples.xlsx')

#%%
unique_triples = dict()
unique_statements = set()
for row in results:
    triple = (row["subject"], row["relation"], row["object"])
    pmid = row["pmid"]
    unique_statements.add(triple)

    if pmid in unique_triples:
        unique_triples[pmid].add(triple)

    else:
        unique_triples[pmid] = {triple}

all_ids = []
for key, value in unique_triples.items():
    all_ids.append(key)

print("Total number of unique statements", len(unique_statements))
print("Total number of unique pmids", len(all_ids))

# %%
#Number of  edges
results = "SELECT count(*) FROM bel_relation {}".format(condition)
num_edges = query.sql(results).data
print("Number of Edges", num_edges[0]["count(*)"])

#%% Number of nodes
# Notice: the resultset numbers are embedded in the edges right,
# nodes are shard by the triple edges.
# To find new nodes is a bit tricky,
# I would first get all nodes for triples from result set 1,
# and then all nodes from triples from result set 2,
# and find the difference. To get nodes for a set of triples,
# you can run:
# select expand(bothV()) FROM bel_relation WHERE annotation.ResultSet = "1"
results = "select expand(bothV()) FROM bel_relation {}".format(condition)
num_nodes = query.sql(results).data
print("Number of Nodes", len(num_nodes))

# %%
# Number o namespace occurences
bel_query = "SELECT value as namespace, count(*) as number FROM (select expand(unionAll(out.namespace, in.namespace)) from bel_relation {})".format(condition) + "GROUP BY value ORDER BY number DESC"
results = query.sql(bel_query).data
print(results)

namespaces = []
counts = []
for item in results:
    namespaces.append(item["namespace"])
    counts.append(item["number"])


namespaces = namespaces[:10]
counts = counts [:10]
import matplotlib.pyplot as plt

plt.ylabel('Namespaces')
plt.title('Count of top ten namespaces')
plt.xticks(rotation=30)
plt.legend()
plt.bar(namespaces, counts)
plt.savefig('barplotinference.png', dpi=300, bbox_inches = "tight")
plt.show()


# %%
# Number of node occurences

bel_query = "SELECT value as node_bel, count(*) as number FROM (select expand(unionAll(out.bel, in.bel)) from bel_relation) GROUP BY value ORDER BY number DESC"
results = query.sql(bel_query).data
print(results)

node_bels = []
counts = []
for item in results:
    node_bels.append(item["node_bel"])
    counts.append(item["number"])

node_bels = node_bels[:10]
counts = counts [:10]
import matplotlib.pyplot as plt

plt.xlabel('BEL nodes')
plt.title('Count of top ten node occurences')
plt.xticks(rotation=90)
plt.legend()
plt.bar(node_bels, counts)
#plt.savefig('barplotinference.png', dpi=300, bbox_inches = "tight") #remove comment if u wanna save file
plt.show()


# %% different types of relationships

bel_query = "SELECT @class as edge_type, count(*) as number FROM bel_relation {}".format(condition)+ "GROUP BY @class ORDER BY number DESC"
results = query.sql(bel_query).data
print(results)
relationships = []
counts = []
for item in results:
    relationships.append(item["edge_type"])
    counts.append(item["number"])

relationships = relationships[:10]
counts = counts [:10]

plt.xlabel('BEL relationship types')
plt.title('Count of top ten BEL relationships')
plt.xticks(rotation=90)
plt.legend()
plt.bar(relationships, counts)
#plt.savefig('barplotinference.png', dpi=300, bbox_inches = "tight")
plt.show()


# %% get triples and their quality
bel_query = "select from bel_relation where annotation.Quality is not null"
results = query.sql(bel_query).data
print(results)
# %% get each triple from each run


