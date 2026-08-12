import faiss
import numpy as np
import pickle
import os


class FAISSVectorStore:

    def __init__(self, dimension):
        """
        Initialize the FAISS vector store.

        Args:
            dimension: Dimension of the embedding vectors.
        """
        self.dimension = dimension

        # Create FAISS index using L2 distance
        self.index = faiss.IndexFlatL2(dimension)

        # Store the corresponding document chunks
        self.documents = []

    def add_embeddings(self, embeddings, documents):
        """
        Add embeddings and their corresponding documents.

        Args:
            embeddings: NumPy array or list of embedding vectors.
            documents: List of document chunks.
        """

        embeddings = np.array(embeddings).astype("float32")

        # If only one embedding is provided
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        # Check embedding dimension
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"but received {embeddings.shape[1]}."
            )

        # Check number of embeddings and documents
        if len(embeddings) != len(documents):
            raise ValueError(
                "Number of embeddings must match "
                "number of documents."
            )

        # Add vectors to FAISS
        self.index.add(embeddings)

        # Store corresponding documents
        self.documents.extend(documents)

    def search(self, query_embedding, k=5):
        """
        Search for the most similar document chunks.

        Args:
            query_embedding: Embedding of the user's query.
            k: Number of results to return.

        Returns:
            List of matching documents and their distances.
        """

        # No vectors in the index
        if self.index.ntotal == 0:
            return []

        query_embedding = np.array(
            query_embedding
        ).astype("float32")

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Check query dimension
        if query_embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Query embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"but received {query_embedding.shape[1]}."
            )

        # Don't request more results than available
        k = min(k, self.index.ntotal)

        distances, indices = self.index.search(
            query_embedding,
            k
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):
            if index != -1 and index < len(self.documents):

                results.append({
                    "document": self.documents[index],
                    "distance": float(distance)
                })

        return results

    def save(self, index_path, metadata_path):
        """
        Save FAISS index and document metadata.
        """

        # Create directories if required
        index_directory = os.path.dirname(index_path)
        metadata_directory = os.path.dirname(metadata_path)

        if index_directory:
            os.makedirs(
                index_directory,
                exist_ok=True
            )

        if metadata_directory:
            os.makedirs(
                metadata_directory,
                exist_ok=True
            )

        # Save FAISS index
        faiss.write_index(
            self.index,
            index_path
        )

        # Save documents
        with open(
            metadata_path,
            "wb"
        ) as file:

            pickle.dump(
                self.documents,
                file
            )

    def load(self, index_path, metadata_path):
        """
        Load FAISS index and document metadata.
        """

        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(
                f"Metadata file not found: {metadata_path}"
            )

        # Load FAISS index
        self.index = faiss.read_index(
            index_path
        )

        # Load documents
        with open(
            metadata_path,
            "rb"
        ) as file:

            self.documents = pickle.load(file)