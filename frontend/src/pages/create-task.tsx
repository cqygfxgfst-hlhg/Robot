import React, { useState } from "react";
import { useUser, useAuth } from '@clerk/nextjs';
import { SignIn } from '@clerk/nextjs';
import { useRouter } from 'next/router';

export default function CreateTaskPage() {
  const { isSignedIn, user, isLoaded } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const [modelName, setModelName] = useState("");
  const [datasetUrl, setDatasetUrl] = useState("");
  const [parameters, setParameters] = useState("{}");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 如果还在加载用户状态，显示加载中
  if (!isLoaded) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  // 如果未登录，显示登录页面
  if (!isSignedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please Login First</h1>
          <SignIn />
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);

    let paramsObj;
    try {
      paramsObj = JSON.parse(parameters);
    } catch {
      setError("Parameters must be valid JSON format");
      setLoading(false);
      return;
    }

    try {
      // 获取Clerk token
      const token = await getToken();
      
              const res = await fetch("http://myrobotbalancer-401487233.us-east-2.elb.amazonaws.com/jobs", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          model_name: modelName,
          dataset_url: datasetUrl,
          parameters: paramsObj,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setResult(`Task created successfully, ID: ${data.message_id}`);
      } else {
        setError(data.detail || "Task creation failed");
      }
    } catch (err) {
      setError("Network error or server not responding");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-6 bg-white rounded-2xl shadow">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Create Training Task</h1>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-600">
            Welcome, {user?.firstName || user?.emailAddresses[0]?.emailAddress}
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          >
            View Tasks
          </button>
        </div>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-medium mb-1">Model Name</label>
          <input
            type="text"
            placeholder="e.g. resnet50"
            value={modelName}
            onChange={e => setModelName(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block font-medium mb-1">Dataset URL</label>
          <input
            type="text"
            placeholder="e.g. s3://my-bucket/data"
            value={datasetUrl}
            onChange={e => setDatasetUrl(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block font-medium mb-1">Parameters (JSON)</label>
          <textarea
            placeholder='e.g. {"epochs": 10, "lr": 0.001}'
            value={parameters}
            onChange={e => setParameters(e.target.value)}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
        >
          {loading ? "Submitting..." : "Create Task"}
        </button>
      </form>
      {result && <div className="mt-4 text-green-600">{result}</div>}
      {error && <div className="mt-4 text-red-600">{error}</div>}
    </div>
  );
}
