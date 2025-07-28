import { useEffect } from "react";
import { useRouter } from "next/router";
import { useUser } from '@clerk/nextjs';
import Link from 'next/link';

export default function Home() {
  const { isSignedIn, user, isLoaded } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      router.replace("/create-task");
    }
  }, [isLoaded, isSignedIn, router]);

  if (!isLoaded) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isSignedIn) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <h1 className="text-4xl font-bold mb-8">LeRobot Training Task Management System</h1>
        <div className="space-x-4">
          <Link
            href="/sign-in"
            className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            登录
          </Link>
          <Link
            href="/sign-up"
            className="px-6 py-3 border border-blue-600 text-blue-600 rounded hover:bg-blue-50 transition"
          >
            注册
          </Link>
        </div>
      </div>
    );
  }

  return <div className="min-h-screen flex items-center justify-center">Redirecting...</div>;
}