from elasticsearch import Elasticsearch
from rdflib import Graph, Namespace, URIRef, Literal
import json
import os
import time

def wait_for_elasticsearch(es, max_retries=30, delay=10):
    """Wait for Elasticsearch to become available"""
    for i in range(max_retries):
        try:
            if es.ping():
                print("Elasticsearch is ready!")
                return True
        except Exception as e:
            print(f"Waiting for Elasticsearch... (attempt {i+1}/{max_retries})")
            time.sleep(delay)
    return False

def create_index(es, index_name):
    """Create an index with appropriate mappings for art data"""
    mapping = {
        "mappings": {
            "properties": {
                "@id": {"type": "keyword"},
                "@type": {"type": "keyword"}
            },
            "dynamic": True  # Allow dynamic mapping for RDF predicates
        },
        "settings": {
            "analysis": {
                "analyzer": {
                    "dutch": {
                        "tokenizer": "standard",
                        "filter": ["lowercase", "dutch_stop", "dutch_stemmer"]
                    }
                },
                "filter": {
                    "dutch_stop": {
                        "type": "stop",
                        "stopwords": "_dutch_"
                    },
                    "dutch_stemmer": {
                        "type": "stemmer",
                        "language": "dutch"
                    }
                }
            }
        }
    }
    
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    
    es.indices.create(index=index_name, body=mapping)
    print(f"Created index: {index_name}")

def process_turtle_file(file_path):
    """Process a Turtle file and convert it to documents for Elasticsearch"""
    g = Graph()
    g.parse(file_path, format="turtle")
    
    documents = {}
    
    # First pass: collect all named resources that have a type
    named_resources = set()
    for s, p, o in g:
        if isinstance(s, URIRef) and str(p) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            named_resources.add(str(s))
    
    # Second pass: process only named resources and their properties
    for s, p, o in g:
        subject_id = str(s)
        
        # Skip if subject is not a named resource we want to index
        if subject_id not in named_resources:
            continue
            
        predicate = str(p)
        
        if subject_id not in documents:
            documents[subject_id] = {
                "@id": subject_id,
                "@type": []
            }
        
        # Handle object based on its type
        if isinstance(o, URIRef):
            obj_value = str(o)
        elif isinstance(o, Literal):
            obj_value = str(o)
        else:
            # Skip blank nodes
            continue
            
        # Add value to the appropriate predicate list
        if predicate not in documents[subject_id]:
            documents[subject_id][predicate] = []
        if obj_value not in documents[subject_id][predicate]:
            documents[subject_id][predicate].append(obj_value)
            
        # Special handling for rdf:type
        if predicate == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            documents[subject_id]["@type"].append(obj_value)
    
    # Convert dictionary to list of documents
    doc_list = list(documents.values())
    print(f"Found {len(doc_list)} documents in {file_path}")
    
    return doc_list

def index_documents(es, index_name, data_dir):
    """Index documents from Turtle files in the data directory"""
    for filename in os.listdir(data_dir):
        if filename.endswith('.ttl'):
            file_path = os.path.join(data_dir, filename)
            print(f"Processing {filename}...")
            
            try:
                documents = process_turtle_file(file_path)
                print(f"Found {len(documents)} documents in {filename}")
                
                # Bulk index the documents
                if documents:
                    bulk_data = []
                    for doc in documents:
                        # Use the document's ID as the Elasticsearch document ID
                        bulk_data.append({"index": {"_index": index_name, "_id": doc["@id"]}})
                        bulk_data.append(doc)
                    
                    if bulk_data:
                        es.bulk(index=index_name, body=bulk_data, refresh=True)
                        print(f"Indexed {len(documents)} documents from {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

def main():
    # Connect to Elasticsearch
    es = Elasticsearch(["http://localhost:9200"])
    
    # Wait for Elasticsearch to be ready
    if not wait_for_elasticsearch(es):
        print("Elasticsearch is not available. Exiting.")
        return
    
    index_name = "artwork"
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "ld")  # Use relative path from script location
    
    # Create index with mapping
    create_index(es, index_name)
    
    # Index documents
    index_documents(es, index_name, data_dir)
    
    print("Indexing complete!")

if __name__ == "__main__":
    main()
