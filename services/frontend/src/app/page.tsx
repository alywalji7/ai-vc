'use client'

import { useState, useEffect } from 'react'

interface User {
  id: number
  username: string
  email: string
  is_active: boolean
}

export default function HomePage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchUsers() {
      try {
        // Use a proxy approach through Next.js API routes to avoid CORS issues
        const response = await fetch('/api/users')
        if (!response.ok) {
          throw new Error('Failed to fetch users')
        }
        const data = await response.json()
        setUsers(data)
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred')
        setLoading(false)
      }
    }

    fetchUsers()
  }, [])

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-12">
      <div className="z-10 max-w-5xl w-full items-center justify-between text-sm">
        <h1 className="text-4xl font-bold mb-8">Polyglot Monorepo Frontend</h1>
        
        <div className="mb-8">
          <p className="text-lg">
            This is the frontend application for the polyglot monorepo. It's built with Next.js 14 and TypeScript.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md w-full">
          <h2 className="text-2xl font-semibold mb-4">Users</h2>
          
          {loading ? (
            <p>Loading users...</p>
          ) : error ? (
            <div className="bg-red-100 p-4 rounded text-red-800 mb-4">
              <p>Error: {error}</p>
              <p className="text-sm mt-2">The backend API might not be running or accessible.</p>
            </div>
          ) : users.length === 0 ? (
            <p>No users found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white">
                <thead>
                  <tr className="bg-gray-200 text-gray-800 text-left">
                    <th className="py-3 px-4 border-b font-semibold">ID</th>
                    <th className="py-3 px-4 border-b font-semibold">Username</th>
                    <th className="py-3 px-4 border-b font-semibold">Email</th>
                    <th className="py-3 px-4 border-b font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="py-2 px-4 border-b text-gray-900">{user.id}</td>
                      <td className="py-2 px-4 border-b text-gray-900">{user.username}</td>
                      <td className="py-2 px-4 border-b text-gray-900">{user.email}</td>
                      <td className="py-2 px-4 border-b">
                        {user.is_active ? (
                          <span className="text-green-600 font-medium">Active</span>
                        ) : (
                          <span className="text-red-600 font-medium">Inactive</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
