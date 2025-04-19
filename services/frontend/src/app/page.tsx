import Link from 'next/link';

export default function Home() {
  return (
    <div className="container mx-auto py-10 px-4">
      <h1 className="text-4xl font-bold mb-6">Polyglot Monorepo</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Data Ingestion & Knowledge Graph</h2>
          <p className="text-gray-600 mb-4">
            Ingest data from various sources such as GitHub and Crunchbase, normalize it into entities 
            and relationships, and store it in a property-graph schema in Postgres.
          </p>
          <div className="text-sm text-gray-500">
            <div className="mb-1"><span className="font-semibold">API:</span> http://localhost:8080</div>
            <div><span className="font-semibold">Documentation:</span> http://localhost:8080/docs</div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Event-Driven ETL Scheduler</h2>
          <p className="text-gray-600 mb-4">
            Orchestrate periodic ingestion tasks with Celery and Flower. Monitor job success rates 
            and latency with Grafana and Prometheus.
          </p>
          <div className="text-sm text-gray-500">
            <div className="mb-1"><span className="font-semibold">API:</span> http://localhost:8085</div>
            <div><span className="font-semibold">UI:</span> <Link href="/scheduler" className="text-blue-500 hover:underline">Scheduler Dashboard</Link></div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Vectorizer & Similarity API</h2>
          <p className="text-gray-600 mb-4">
            Generate vector embeddings for text, code, and tabular data using the all-MiniLM-L6-v2 model.
            Search for similar items with high cosine similarity using Qdrant vector database.
          </p>
          <div className="text-sm text-gray-500">
            <div className="mb-1"><span className="font-semibold">API:</span> http://localhost:8090</div>
            <div><span className="font-semibold">UI:</span> <Link href="/similarity" className="text-blue-500 hover:underline">Similarity Search & Storage</Link></div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Deal-Flow Radar (Scoring Service)</h2>
          <p className="text-gray-600 mb-4">
            Identify promising companies for investment using a CatBoost binary classifier trained 
            on company metrics and predicting top-decile exits.
          </p>
          <div className="text-sm text-gray-500">
            <div className="mb-1"><span className="font-semibold">API:</span> http://localhost:8095</div>
            <div><span className="font-semibold">UI:</span> <Link href="/radar" className="text-blue-500 hover:underline">Investment Opportunity Radar</Link></div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-1 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Backend API Service</h2>
          <p className="text-gray-600 mb-4">
            FastAPI backend service with user authentication and data access endpoints.
          </p>
          <div className="text-sm text-gray-500">
            <div className="mb-1"><span className="font-semibold">API:</span> http://localhost:8000</div>
            <div><span className="font-semibold">Documentation:</span> http://localhost:8000/docs</div>
          </div>
        </div>
      </div>
      
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200 mt-6">
        <h2 className="text-xl font-semibold mb-2">Project Overview</h2>
        <p className="text-gray-700">
          This polyglot monorepo follows the polylith folder pattern with services, libs, infra, and docs directories.
          The tech stack includes Python 3.11 for backend services and TypeScript/Next.js 14 for the frontend portal.
          Infrastructure includes Docker configuration for Postgres 16, Redis, Qdrant, and Minio services.
        </p>
      </div>
    </div>
  );
}