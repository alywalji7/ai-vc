'use client'

import { useState, useEffect } from 'react'

interface Task {
  name: string
  description: string | null
  cron: string
  task: string
  args: any[]
  kwargs: Record<string, any>
  enabled: boolean
}

export default function SchedulerPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [taskResult, setTaskResult] = useState<any>(null)
  const [runningTask, setRunningTask] = useState<string | null>(null)

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/scheduler/tasks')
      if (!response.ok) {
        throw new Error(`Error fetching tasks: ${response.statusText}`)
      }
      const data = await response.json()
      setTasks(data)
    } catch (err) {
      setError(`Failed to load tasks: ${err instanceof Error ? err.message : String(err)}`)
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const runTask = async (taskName: string) => {
    setRunningTask(taskName)
    setTaskResult(null)
    setError(null)
    try {
      const response = await fetch(`/api/scheduler/tasks/${taskName}/run`, {
        method: 'POST'
      })
      if (!response.ok) {
        throw new Error(`Error running task: ${response.statusText}`)
      }
      const data = await response.json()
      setTaskResult(data)
    } catch (err) {
      setError(`Failed to run task: ${err instanceof Error ? err.message : String(err)}`)
      console.error(err)
    } finally {
      setRunningTask(null)
    }
  }

  // Helper function to format cron expressions in a human-readable way
  const formatCron = (cron: string): string => {
    const parts = cron.split(' ')
    if (parts.length !== 5) return cron
    
    // Simple translation for common patterns
    if (cron === '0 * * * *') return 'Every hour at minute 0'
    if (cron === '0 */6 * * *') return 'Every 6 hours'
    if (cron === '0 */12 * * *') return 'Every 12 hours'
    if (cron === '0 0 * * *') return 'Daily at midnight'
    
    // More specific patterns
    if (parts[0] === '0' && parts[1].startsWith('*/')) {
      return `Every ${parts[1].replace('*/', '')} hours`
    }
    
    return cron
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Scheduler Tasks</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="mb-4">
        <button 
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          onClick={fetchTasks}
        >
          Refresh Tasks
        </button>
      </div>
      
      {loading ? (
        <p>Loading tasks...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tasks.map((task) => (
            <div key={task.name} className="border rounded p-4 shadow">
              <h2 className="text-xl font-semibold">{task.name}</h2>
              <p className="text-gray-600 mb-2">{task.description || 'No description'}</p>
              
              <div className="mb-2">
                <span className="font-semibold">Schedule:</span> {formatCron(task.cron)}
              </div>
              
              <div className="mb-2">
                <span className="font-semibold">Task:</span> {task.task}
              </div>
              
              <div className="mb-2">
                <span className="font-semibold">Arguments:</span>{' '}
                {task.args.length > 0 ? task.args.join(', ') : 'None'}
              </div>
              
              <div className="mb-2">
                <span className="font-semibold">Status:</span>{' '}
                <span className={task.enabled ? 'text-green-600' : 'text-red-600'}>
                  {task.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              
              <button
                className={`mt-2 font-bold py-2 px-4 rounded ${
                  task.enabled
                    ? 'bg-green-500 hover:bg-green-700 text-white'
                    : 'bg-gray-300 text-gray-700 cursor-not-allowed'
                }`}
                onClick={() => task.enabled && runTask(task.name)}
                disabled={!task.enabled || runningTask === task.name}
              >
                {runningTask === task.name ? 'Running...' : 'Run Now'}
              </button>
            </div>
          ))}
        </div>
      )}
      
      {taskResult && (
        <div className="mt-6 border rounded p-4 bg-gray-50">
          <h2 className="text-xl font-semibold mb-2">Task Execution Result</h2>
          <pre className="bg-gray-100 p-3 rounded overflow-x-auto">
            {JSON.stringify(taskResult, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}