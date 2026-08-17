import faiss
import numpy as np
import pickle
import os


class FAISSVectorStore:

    def __init__(self, dimension):
        """
        Initialize FAISS vector store.

        Uses normalized embeddings + Inner Product,
        which is equivalent to cosine similarity.
        """

        self.dimension = dimension

        # Inner Product on normalized vectors
        # = Cosine Similarity
        self.index = faiss.IndexFlatIP(dimension)

        self.documents = []

    def add_embeddings(self, embeddings, documents):

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        # Normalize vectors for cosine similarity
        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)

        self.documents.extend(documents)

    def search(
        self,
        query_embedding,
        k=5,
        similarity_threshold=0.45
    ):

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        # Normalize query
        faiss.normalize_L2(query_embedding)

        similarities, indices = self.index.search(
            query_embedding,
            k
        )

        results = []

        for similarity, index in zip(
            similarities[0],
            indices[0]
        ):

            # Ignore invalid FAISS indices
            if index < 0:
                continue

            # Similarity filtering
            if similarity < similarity_threshold:
                continue

            if index < len(self.documents):

                results.append({
                    "document": self.documents[index],
                    "similarity": float(similarity)
                })

        return results

    def save(
        self,
        index_path,
        metadata_path
    ):

        # Create directories if necessary
        os.makedirs(
            os.path.dirname(index_path),
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            index_path
        )

        with open(
            metadata_path,
            "wb"
        ) as file:

            pickle.dump(
                self.documents,
                file
            )

    def load(
        self,
        index_path,
        metadata_path
    ):

        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(
                f"Metadata file not found: {metadata_path}"
            )

        self.index = faiss.read_index(
            index_path
        )

        with open(
            metadata_path,
            "rb"
        ) as file:

            self.documents = pickle.load(file)

        self.dimension = self.index.d

        print("FAISS vector store loaded.")
        print(
            f"Total vectors: {self.index.ntotal}"
        )