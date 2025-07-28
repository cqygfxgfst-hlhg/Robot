import { useEffect, useState } from "react"
import { useRouter } from 'next/router';
import { useUser, useAuth } from '@clerk/nextjs';
import ConfirmDialog from '../components/ui/ConfirmDialog';
import ErrorLogDialog from '../components/ui/ErrorLogDialog';

type Job = {
  id: string
  model_name: string
  dataset_url: string
  status: string
  created_at: string
  completed_at?: string
  failed_at?: string
  retry_from?: string
  retry_count?: number
}

export default function DashboardPage() {
  const { isSignedIn, user, isLoaded } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([])
  const [error, setError] = useState("")
  const [retryJobId, setRetryJobId] = useState<string | null>(null);
  const [isRetryDialogOpen, setIsRetryDialogOpen] = useState(false);
  const [retryLoading, setRetryLoading] = useState(false);
  const [errorLogJobId, setErrorLogJobId] = useState<string | null>(null);
  const [isErrorLogDialogOpen, setIsErrorLogDialogOpen] = useState(false);

  const fetchJobs = async () => {
    try {
      // 获取Clerk token
      const token = await getToken();
      
              const res = await fetch("http://myrobotbalancer-401487233.us-east-2.elb.amazonaws.com/jobs", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
      const data = await res.json()
      
      // 确保jobs始终是数组
      const jobsArray = Array.isArray(data.jobs) ? data.jobs : 
                       Array.isArray(data) ? data : [];
      
      setJobs(jobsArray)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError("Failed to fetch tasks: " + errorMessage)
      setJobs([]) // 出错时设置为空数组
    }
  }

  useEffect(() => {
    // 只有在用户已登录且加载完成时才获取任务
    if (isSignedIn && isLoaded) {
      fetchJobs()
      const interval = setInterval(fetchJobs, 5000)
      return () => clearInterval(interval)
    }
  }, [isSignedIn, isLoaded])

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
          <p className="text-gray-600">You need to login to view task list</p>
        </div>
      </div>
    );
  }

  const handleRetryClick = (jobId: string) => {
    setRetryJobId(jobId);
    setIsRetryDialogOpen(true);
  };

  const handleRetryConfirm = async () => {
    if (!retryJobId) return;
    
    setRetryLoading(true);
    try {
      // 获取Clerk token
      const token = await getToken();
      
              const response = await fetch(`http://myrobotbalancer-401487233.us-east-2.elb.amazonaws.com/jobs/${retryJobId}/retry`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
      });
      
      if (response.ok) {
        // 重试成功，刷新任务列表
        await fetchJobs();
        alert('Task retry started!');
      } else {
        const errorData = await response.json();
        alert(`Retry failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      alert('Network error, please try again later');
    } finally {
      setRetryLoading(false);
      setIsRetryDialogOpen(false);
      setRetryJobId(null);
    }
  };

  const handleRetryCancel = () => {
    setIsRetryDialogOpen(false);
    setRetryJobId(null);
  };

  const handleViewErrorLog = (jobId: string) => {
    setErrorLogJobId(jobId);
    setIsErrorLogDialogOpen(true);
  };

  const handleErrorLogClose = () => {
    setIsErrorLogDialogOpen(false);
    setErrorLogJobId(null);
  };

  return (
    <div className="max-w-4xl mx-auto mt-10 p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Task Dashboard</h1>
        <button
          onClick={() => router.push('/create-task')}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
        >
          Create New Task
        </button>
      </div>
      {error && <p className="text-red-600 mb-4">{error}</p>}
      <table className="w-full text-sm border border-gray-200 rounded shadow-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 text-left">Model Name</th>
            <th className="p-2 text-left">Dataset URL</th>
            <th className="p-2 text-left">Status</th>
            <th className="p-2 text-left">Retry Info</th>
            <th className="p-2 text-left">Created At</th>
            <th className="p-2 text-left">Completed/Failed At</th>
            <th className="p-2 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          {jobs && jobs.length > 0 ? jobs.map(job => (
            <tr key={job.id} className="border-t border-gray-100 hover:bg-gray-50">
              <td className="p-2">{job.model_name}</td>
              <td className="p-2 text-blue-600">{job.dataset_url}</td>
              <td className="p-2">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    job.status === "completed"
                      ? "bg-green-100 text-green-800"
                      : job.status === "failed"
                      ? "bg-red-100 text-red-800"
                      : job.status === "running"
                      ? "bg-yellow-100 text-yellow-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {job.status}
                </span>
              </td>
              <td className="p-2">
                {job.retry_count && job.retry_count > 0 ? (
                  <span className="text-xs text-gray-600">
                    Retry {job.retry_count} times
                  </span>
                ) : job.retry_from ? (
                  <span className="text-xs text-blue-600">
                    From retry
                  </span>
                ) : (
                  <span className="text-xs text-gray-400">
                    Original task
                  </span>
                )}
              </td>
              <td className="p-2">{new Date(job.created_at).toLocaleString()}</td>
              <td className="p-2">
                {job.completed_at ? (
                  <span className="text-xs text-green-600">
                    Completed: {new Date(job.completed_at).toLocaleString()}
                  </span>
                ) : job.failed_at ? (
                  <span className="text-xs text-red-600">
                    Failed: {new Date(job.failed_at).toLocaleString()}
                  </span>
                ) : (
                  <span className="text-xs text-gray-400">
                    In progress...
                  </span>
                )}
              </td>
              <td className="p-2">
                <div className="flex space-x-2">
                  {(job.status === "failed" || job.status === "completed") && (
                    <button
                      onClick={() => handleRetryClick(job.id)}
                      disabled={retryLoading}
                      className="px-3 py-1 bg-orange-500 text-white text-xs rounded hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {retryLoading && retryJobId === job.id ? "Retrying..." : "Retry"}
                    </button>
                  )}
                  {job.status === "failed" && (
                    <button
                      onClick={() => handleViewErrorLog(job.id)}
                      className="px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
                    >
                      View Log
                    </button>
                  )}
                </div>
              </td>
            </tr>
          )) : (
            <tr>
                          <td colSpan={7} className="p-4 text-center text-gray-500">
              No task data available
            </td>
            </tr>
          )}
        </tbody>
      </table>
      
      <ConfirmDialog
        isOpen={isRetryDialogOpen}
        onClose={handleRetryCancel}
        onConfirm={handleRetryConfirm}
        title="Confirm Retry Task"
        message="Are you sure you want to retry this training task? This will create a new task instance and restart the training."
        confirmText="Confirm Retry"
        cancelText="Cancel"
      />
      
      <ErrorLogDialog
        isOpen={isErrorLogDialogOpen}
        onClose={handleErrorLogClose}
        jobId={errorLogJobId || ""}
      />
    </div>
  )
}
