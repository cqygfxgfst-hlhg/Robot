import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';

interface ErrorLogDialogProps {
  isOpen: boolean;
  onClose: () => void;
  jobId: string;
}

interface ErrorLogData {
  job_id: string;
  error_log: string;
  failed_at: string;
}

export default function ErrorLogDialog({
  isOpen,
  onClose,
  jobId
}: ErrorLogDialogProps) {
  const { getToken } = useAuth();
  const [errorLog, setErrorLog] = useState<ErrorLogData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && jobId) {
      fetchErrorLog();
    }
  }, [isOpen, jobId]);

  const fetchErrorLog = async () => {
    setLoading(true);
    setError(null);
    try {
      // 获取Clerk token
      const token = await getToken();
      
                const response = await fetch(`http://myrobotbalancer-401487233.us-east-2.elb.amazonaws.com/jobs/${jobId}/error-log`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setErrorLog(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || '获取错误日志失败');
      }
    } catch (err) {
      setError('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">错误日志详情</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl font-bold"
          >
            ×
          </button>
        </div>
        
        <div className="flex-1 overflow-auto">
          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">加载错误日志中...</p>
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-red-600">{error}</p>
            </div>
          )}
          
          {errorLog && !loading && (
            <div className="space-y-4">
              <div className="bg-gray-50 p-3 rounded-md">
                <p className="text-sm text-gray-600">
                  <strong>任务ID:</strong> {errorLog.job_id}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>失败时间:</strong> {new Date(errorLog.failed_at).toLocaleString()}
                </p>
              </div>
              
              <div>
                <h4 className="font-medium mb-2">错误详情:</h4>
                <pre className="bg-gray-900 text-green-400 p-4 rounded-md overflow-x-auto text-sm whitespace-pre-wrap">
                  {errorLog.error_log}
                </pre>
              </div>
            </div>
          )}
        </div>
        
        <div className="mt-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  );
} 