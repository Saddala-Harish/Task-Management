'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { tasksApi } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import axios from 'axios';

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium',
    assigned_to: ''
  });
  const [editingTask, setEditingTask] = useState(null);
  const router = useRouter();
  const { user } = useAuth();

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    loadTasks();
    if (user.role === 'admin' || user.role === 'manager') {
      loadUsers();
    }
  }, [user, router]);

  const loadUsers = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      console.log('Users response:', response.data);
      setUsers(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error loading users:', error);
      setUsers([]);
    }
  };

  const loadTasks = async () => {
    try {
      const response = await tasksApi.getTasks();
      setTasks(response.tasks || []);
    } catch (error) {
      console.error('Error loading tasks:', error);
    }
  };

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await tasksApi.updateTask(taskId, { status: newStatus });
      loadTasks();
    } catch (error) {
      console.error('Error updating task status:', error);
      if (error.response?.status === 422) {
        alert('Invalid status value. Please try again.');
      } else if (error.response?.status === 403) {
        alert('You do not have permission to update this task.');
      } else {
        alert('An error occurred while updating the task.');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const taskData = {
        title: newTask.title,
        description: newTask.description,
        priority: newTask.priority,
        assigned_to: newTask.assigned_to ? Number(newTask.assigned_to) : null
      };

      if (editingTask) {
        await tasksApi.updateTask(editingTask.id, taskData);
        setEditingTask(null);
      } else {
        await tasksApi.createTask(taskData);
      }
      
      setNewTask({ title: '', description: '', priority: 'medium', assigned_to: '' });
      loadTasks();
    } catch (error) {
      console.error('Error with task:', error);
      if (error.response?.status === 422) {
        alert('Please check all fields are filled correctly.');
      } else if (error.response?.status === 403) {
        alert('You do not have permission to perform this action.');
      } else {
        alert('An error occurred. Please try again.');
      }
    }
  };

  const handleEdit = (task) => {
    setEditingTask(task);
    setNewTask({
      title: task.title,
      description: task.description || '',
      priority: task.priority || 'medium',
      assigned_to: task.assigned_to ? String(task.assigned_to) : ''
    });
  };

  const handleCancel = () => {
    setEditingTask(null);
    setNewTask({ title: '', description: '', priority: 'medium', assigned_to: '' });
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="text-xl font-semibold text-gray-800">Task Manager</div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">{user.email} ({user.role})</span>
              <button
                onClick={() => {
                  localStorage.removeItem('token');
                  router.push('/login');
                }}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {(user.role === 'admin' || user.role === 'manager') && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {editingTask ? 'Edit Task' : 'Create New Task'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Task Title
                </label>
                <input
                  type="text"
                  required
                  value={newTask.title}
                  onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md"
                  placeholder="Enter task title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  rows="3"
                  value={newTask.description}
                  onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md"
                  placeholder="Enter task description"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Assign To
                </label>
                <select
                  value={newTask.assigned_to}
                  onChange={(e) => setNewTask({ ...newTask, assigned_to: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md"
                >
                  <option value="">Select User</option>
                  {Array.isArray(users) && users.map(user => (
                    <option key={user.id} value={user.id}>
                      {user.full_name} ({user.email})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Priority
                </label>
                <select
                  value={newTask.priority}
                  onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div className="flex space-x-4">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  {editingTask ? 'Update Task' : 'Create Task'}
                </button>
                {editingTask && (
                  <button
                    type="button"
                    onClick={handleCancel}
                    className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </div>
        )}

        <div className="space-y-4">
          {tasks.map((task) => (
            <div key={task.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{task.title}</h3>
                  <p className="mt-2 text-gray-600">{task.description}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    Assigned to: {task.assignee?.full_name || 'Unassigned'}
                  </p>
                </div>
                {(user.role === 'admin' || (user.role === 'manager' && task.created_by === user.id)) && (
                  <button
                    onClick={() => handleEdit(task)}
                    className="px-3 py-1 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
                  >
                    Edit
                  </button>
                )}
              </div>
              <div className="mt-4 flex justify-between items-center">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  task.priority === 'high' ? 'bg-red-100 text-red-800' :
                  task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {task.priority}
                </span>
                <select
                  value={task.status}
                  onChange={(e) => handleStatusChange(task.id, e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-md"
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}