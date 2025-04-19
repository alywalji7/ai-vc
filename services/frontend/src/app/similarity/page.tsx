import Link from 'next/link';
import SimilaritySearch from '../components/SimilaritySearch';
import StoreEmbeddings from '../components/StoreEmbeddings';

export default function SimilarityPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Vector Similarity Service</h1>
        <p className="text-gray-600 mb-4">
          This service allows you to search for similar text, code, or tabular data using vector embeddings.
        </p>
        <Link href="/" className="text-blue-600 hover:underline">
          Back to Home
        </Link>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <SimilaritySearch />
        <StoreEmbeddings />
      </div>

      <div className="mt-12 bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h2 className="text-xl font-bold mb-3">How It Works</h2>
        <p className="mb-4">
          This service uses the Sentence Transformers package from Hugging Face and the all-MiniLM-L6-v2 model to generate embeddings for text, code, and tabular data.
        </p>
        <h3 className="text-lg font-medium mb-2">Features:</h3>
        <ul className="list-disc list-inside mb-4 space-y-1">
          <li>Generate embeddings for text, code, and tabular data</li>
          <li>Store embeddings in Qdrant vector database</li>
          <li>Search for similar items using cosine similarity</li>
          <li>Filter results by metadata</li>
        </ul>
        <p className="mb-4">
          <strong>Note:</strong> Stored embeddings will be automatically handled by the backend service, even if Qdrant is not available. In that case, IDs will still be generated, but the actual similarity search will return empty results.
        </p>
      </div>
    </div>
  );
}