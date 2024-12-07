from elasticsearch import Elasticsearch
from rdflib import Graph, Namespace
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
                "id": {"type": "keyword"},
                "type": {"type": "keyword"},
                "label": {"type": "text"},
                "description": {"type": "text"},
                "created_by": {"type": "text"},
                "created_date": {"type": "date", "format": "strict_date_optional_time||epoch_millis"},
                "modified_date": {"type": "date", "format": "strict_date_optional_time||epoch_millis"},
                "rights": {"type": "text"},
                "source": {"type": "text"},
                "subject": {"type": "text"},
                "technique": {"type": "text"},
                "title": {"type": "text"}
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=mapping)
        print(f"Created index: {index_name}")

def process_turtle_file(file_path):
    """Process a Turtle file and convert it to documents for Elasticsearch"""
    g = Graph()
    g.parse(file_path, format="turtle")
    
    # Define common namespaces
    crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
    la = Namespace("https://linked.art/ns/terms/")
    
    documents = []
    
    # Query for artworks
    query = """
    SELECT DISTINCT ?s ?label ?type ?description ?creator ?date ?rights ?source ?subject ?technique
    WHERE {
        ?s a ?type .
        OPTIONAL { ?s rdfs:label ?label }
        OPTIONAL { ?s dc:description ?description }
        OPTIONAL { ?s dc:creator ?creator }
        OPTIONAL { ?s dc:date ?date }
        OPTIONAL { ?s dc:rights ?rights }
        OPTIONAL { ?s dc:source ?source }
        OPTIONAL { ?s dc:subject ?subject }
        OPTIONAL { ?s la:technique ?technique }
    }
    """
    
    for row in g.query(query):
        doc = {
            "id": str(row.s),
            "type": str(row.type),
            "label": str(row.label) if row.label else None,
            "description": str(row.description) if row.description else None,
            "created_by": str(row.creator) if row.creator else None,
            "created_date": str(row.date) if row.date else None,
            "rights": str(row.rights) if row.rights else None,
            "source": str(row.source) if row.source else None,
            "subject": str(row.subject) if row.subject else None,
            "technique": str(row.technique) if row.technique else None
        }
        
        # Remove None values
        doc = {k: v for k, v in doc.items() if v is not None}
        documents.append(doc)
    
    return documents

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
                        bulk_data.append({"index": {"_index": index_name}})
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
    data_dir = "../data/ld"  # Relative to where the script will be on the server
    
    # Create index with mapping
    create_index(es, index_name)
    
    # Index documents
    index_documents(es, index_name, data_dir)
    
    print("Indexing complete!")

if __name__ == "__main__":
    main()
